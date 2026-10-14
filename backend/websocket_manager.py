"""
Production WebSocket session manager for Kavach AI.
Handles:
- Session lifecycle management
- Anti-spam scenario control
- State machine for conversation flow
- Connection cleanup
- Graceful error handling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set, Tuple, List
from fastapi import WebSocket
import json

logger = logging.getLogger(__name__)


class SessionState:
    """Tracks the state of a user session in the War Room."""
    
    AWAITING_INITIAL_SCENARIO = "awaiting_initial_scenario"
    ACTIVE_SCENARIO = "active_scenario"
    AWAITING_USER_RESPONSE = "awaiting_user_response"
    SCENARIO_RESOLVED = "scenario_resolved"
    IDLE = "idle"
    ERROR = "error"


class WarRoomSession:
    """
    Manages a single user's War Room conversation session.
    
    Prevents spam by enforcing:
    - Only ONE active scenario per session
    - Must wait for user response before continuing
    - Rate limiting on AI agent calls
    - Timeout for abandoned sessions
    """
    
    def __init__(self, session_id: str, ws: WebSocket):
        self.session_id = session_id
        self.websocket = ws
        self.user_id: Optional[str] = None
        
        # Concurrency control
        self.generation_lock = asyncio.Lock()

        # State management
        self.state = SessionState.IDLE
        self.active_scenario: Optional[Dict[str, Any]] = None
        self.awaiting_response = False
        
        # Session-aware scenario diversity tracking (prevents repetitive scenarios)
        self.scenario_history: List[Dict[str, Any]] = []

        # Timing & rate limiting
        self.created_at = datetime.utcnow()
        self.last_message_at = datetime.utcnow()
        self.last_ai_call_at: Optional[datetime] = None
        self.ai_call_cooldown_seconds = 1  # Throttle AI calls
        
        # Message tracking
        self.message_count = 0
        self.max_messages_per_hour = 100  # Rate limit per session
        
        # Scenario tracking
        self.scenarios_generated = 0
        self.max_scenarios_per_session = 50  # Prevent infinite loops
        
        logger.info(f"[SESSION] Created: {session_id}")
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has been inactive too long."""
        idle_duration = datetime.utcnow() - self.last_message_at
        return idle_duration > timedelta(minutes=timeout_minutes)
    
    def can_generate_new_scenario(self) -> Tuple[bool, str]:
        """
        Check if we can generate a new scenario.
        Returns (bool, reason_if_false)
        """
        # Check scenario limit per session
        if self.scenarios_generated >= self.max_scenarios_per_session:
            return False, f"Session scenario limit ({self.max_scenarios_per_session}) reached."
        
        # Check message rate limit
        if self.message_count >= self.max_messages_per_hour:
            return False, "Rate limit reached. Please wait before generating more scenarios."
        
        # Check AI call cooldown
        if self.last_ai_call_at:
            time_since_call = (datetime.utcnow() - self.last_ai_call_at).total_seconds()
            if time_since_call < self.ai_call_cooldown_seconds:
                wait_time = self.ai_call_cooldown_seconds - time_since_call
                return False, f"Please wait {wait_time:.1f}s before next scenario."
        
        return True, ""
    
    def record_scenario(self, scenario: Dict[str, Any]) -> None:
        """Record scenario metadata into session history to prevent future repetition."""
        record = {
            "scenario_type": scenario.get("scenario_type") or scenario.get("scam_type") or "unknown",
            "attacker_persona": scenario.get("attacker_persona") or scenario.get("scammer_personality") or "unknown",
            "ui_title": scenario.get("ui_title") or "",
            "manipulation_tactics": scenario.get("manipulation_tactics", []),
            "summary": (scenario.get("message") or "")[:80]
        }
        self.scenario_history.append(record)
        if len(self.scenario_history) > 8:
            self.scenario_history = self.scenario_history[-8:]

    def get_history_summary(self) -> List[Dict[str, Any]]:
        """Return compact summary of recent scenarios in this session."""
        return [item.copy() for item in self.scenario_history]

    def start_scenario(self, scenario: Dict[str, Any]) -> None:
        """Mark that a new scenario has started."""
        self.active_scenario = scenario
        self.state = SessionState.ACTIVE_SCENARIO
        self.awaiting_response = True
        self.scenarios_generated += 1
        self.last_ai_call_at = datetime.utcnow()
        self.record_scenario(scenario)
        logger.info(f"[SESSION] {self.session_id}: Scenario #{self.scenarios_generated} started ({scenario.get('scenario_type')})")
    
    def record_user_response(self) -> None:
        """Record that user has responded."""
        self.message_count += 1
        self.last_message_at = datetime.utcnow()
        self.awaiting_response = False
        self.state = SessionState.AWAITING_USER_RESPONSE
        logger.info(f"[SESSION] {self.session_id}: User response recorded (msg #{self.message_count})")
    
    def resolve_scenario(self) -> None:
        """Mark current scenario as resolved."""
        self.state = SessionState.SCENARIO_RESOLVED
        self.active_scenario = None
        self.awaiting_response = False
        logger.info(f"[SESSION] {self.session_id}: Scenario resolved")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize session state for debugging/logging."""
        return {
            "session_id": self.session_id,
            "state": self.state,
            "has_active_scenario": self.active_scenario is not None,
            "awaiting_response": self.awaiting_response,
            "messages": self.message_count,
            "scenarios": self.scenarios_generated,
            "recent_types": [s["scenario_type"] for s in self.scenario_history],
            "elapsed_minutes": (datetime.utcnow() - self.created_at).total_seconds() / 60,
            "is_expired": self.is_expired(),
        }


class WarRoomConnectionManager:
    """
    Manages all active WebSocket connections and their sessions.
    
    Handles:
    - Session creation/destruction
    - Connection cleanup
    - Broadcasting to multiple clients (if needed)
    - Rate limiting across all sessions
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, WarRoomSession] = {}
        self.session_lock = asyncio.Lock()  # Thread-safe session access
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def connect(self, session_id: str, websocket: WebSocket) -> WarRoomSession:
        """
        Connect a new client and create/retrieve their session.
        
        Args:
            session_id: Unique session identifier
            websocket: FastAPI WebSocket connection
            
        Returns:
            WarRoomSession for this connection
        """
        await websocket.accept()
        
        async with self.session_lock:
            # Create new session if doesn't exist
            if session_id not in self.active_sessions:
                session = WarRoomSession(session_id, websocket)
                self.active_sessions[session_id] = session
                logger.info(f"[WS] New session connected: {session_id}")
            else:
                session = self.active_sessions[session_id]
                # Reconnection - update websocket
                session.websocket = websocket
                logger.info(f"[WS] Session reconnected: {session_id}")
        
        return session
    
    async def disconnect(self, session_id: str) -> None:
        """
        Disconnect a session and clean up resources.
        
        Args:
            session_id: Session to disconnect
        """
        async with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                logger.info(
                    f"[WS] Session disconnected: {session_id} | Stats: {session.to_dict()}"
                )
                del self.active_sessions[session_id]
    
    async def broadcast_cleanup(self) -> None:
        """
        Periodically clean up expired sessions.
        Runs in background.
        """
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                async with self.session_lock:
                    expired_sessions = [
                        sid for sid, session in self.active_sessions.items()
                        if session.is_expired(timeout_minutes=30)
                    ]
                
                for session_id in expired_sessions:
                    try:
                        await self.active_sessions[session_id].websocket.close(
                            code=1000,
                            reason="Session idle timeout"
                        )
                    except Exception:
                        pass  # Already closed
                    
                    async with self.session_lock:
                        del self.active_sessions[session_id]
                    
                    logger.info(f"[WS] Session expired (timeout): {session_id}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WS] Cleanup task error: {e}")
    
    def start_cleanup(self) -> None:
        """Start background cleanup task."""
        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self.broadcast_cleanup())
    
    async def stop_cleanup(self) -> None:
        """Stop background cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def send_error(self, session_id: str, error_msg: str) -> None:
        """
        Send error message to client.
        
        Args:
            session_id: Target session
            error_msg: Error description
        """
        async with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                try:
                    await session.websocket.send_json({
                        "error": error_msg,
                        "session_state": session.state,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                except Exception as e:
                    logger.error(f"[WS] Failed to send error to {session_id}: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about all active sessions."""
        return {
            "total_sessions": len(self.active_sessions),
            "sessions": [
                session.to_dict()
                for session in self.active_sessions.values()
            ]
        }


# Global connection manager instance
war_room_manager = WarRoomConnectionManager()
