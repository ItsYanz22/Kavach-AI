"""
Diagnostic and debug endpoints for Kavach AI.
Helps troubleshoot production issues.
"""

import os
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import logging

from backend.config import EnvConfig
from backend.logs_structured import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/env")
async def debug_env() -> Dict[str, Any]:
    """
    Check environment variables and configuration.
    Returns sanitized environment info for debugging.
    """
    return {
        "status": "ok",
        "environment": EnvConfig.ENVIRONMENT,
        "debug_mode": EnvConfig.DEBUG_MODE,
        "log_level": EnvConfig.LOG_LEVEL,
        "port": EnvConfig.PORT,
        "api_keys": {
            "groq_configured": bool(EnvConfig.GROQ_API_KEY),
            "groq_keys_count": len(EnvConfig.GROQ_API_KEYS),
            "jwt_secret_configured": EnvConfig.JWT_SECRET_KEY != "dev-secret-key-change-in-production",
        },
        "database": {
            "url": EnvConfig.DATABASE_URL.split("@")[-1] if "@" in EnvConfig.DATABASE_URL else EnvConfig.DATABASE_URL,
        },
        "websocket": {
            "heartbeat_interval": EnvConfig.WS_HEARTBEAT_INTERVAL,
            "session_timeout": EnvConfig.WS_SESSION_TIMEOUT,
        },
        "ai": {
            "request_timeout": EnvConfig.AI_REQUEST_TIMEOUT,
            "fallback_enabled": EnvConfig.AI_FALLBACK_ENABLED,
        },
    }


@router.get("/agents")
async def debug_agents() -> Dict[str, Any]:
    """
    Test agent initialization and connectivity.
    """
    from backend.services import agent_service
    
    results = {
        "status": "ok",
        "agents": {}
    }
    
    # Test each agent
    for agent_name in ["Infiltrator", "Forensic", "Mentor"]:
        try:
            agent = getattr(agent_service, agent_name.lower())
            test_message = f"Test message from debug endpoint for {agent_name}"
            
            # Try to send a message with short timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(agent.send_message, test_message),
                timeout=5.0
            )
            
            results["agents"][agent_name] = {
                "status": "ok",
                "initialized": agent.client is not None,
                "response_length": len(response),
                "sample_response": response[:100] + "..." if len(response) > 100 else response,
            }
        except asyncio.TimeoutError:
            results["agents"][agent_name] = {
                "status": "timeout",
                "initialized": agent.client is not None,
                "message": "Agent timed out after 5 seconds",
            }
        except Exception as e:
            results["agents"][agent_name] = {
                "status": "error",
                "initialized": agent.client is not None,
                "error": str(e)[:200],
            }
    
    return results


@router.get("/scenario")
async def debug_scenario() -> Dict[str, Any]:
    """
    Generate a test scenario and return the full structure.
    """
    from backend.services import agent_service
    from backend.fallback_scenarios import fallback_engine
    
    try:
        # Try to generate via agent first
        prompt = (
            "Generate a single realistic phishing scam scenario. "
            "Return ONLY valid JSON with NO markdown:\n"
            "{\n"
            '  "scenario_type": "type",\n'
            '  "message": "the scam message",\n'
            '  "amount": 0,\n'
            '  "tip": "educational tip",\n'
            '  "risk_level": "high",\n'
            '  "ui_title": "title",\n'
            '  "ui_description": "description"\n'
            "}"
        )
        
        scenario = await asyncio.wait_for(
            asyncio.to_thread(agent_service.infiltrator.send_message, prompt),
            timeout=10.0
        )
        
        return {
            "status": "ok",
            "source": "agent",
            "scenario": json.loads(scenario) if isinstance(scenario, str) else scenario,
        }
    except Exception as e:
        # Fallback to local scenarios
        logger.warning_event("scenario_generation_failed", error=str(e))
        
        return {
            "status": "fallback",
            "source": "fallback_engine",
            "scenario": fallback_engine.generate_random_scenario(),
            "error": str(e)[:200],
        }


@router.get("/websocket")
async def debug_websocket() -> Dict[str, Any]:
    """
    Get WebSocket manager status.
    """
    from backend.websocket_manager import war_room_manager
    
    sessions = war_room_manager.get_active_sessions()
    
    return {
        "status": "ok",
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": session.session_id,
                "state": session.state,
                "created_at": session.created_at.isoformat(),
                "scenarios_generated": session.scenarios_generated,
                "message_count": session.message_count,
            }
            for session in sessions
        ],
    }


@router.post("/test-ai")
async def test_ai(message: str = "Hello, can you respond to this test message?") -> Dict[str, Any]:
    """
    Send a test message to the AI and measure response time.
    """
    import time
    from backend.services import agent_service
    
    results = {}
    
    for agent_name in ["Infiltrator", "Forensic", "Mentor"]:
        try:
            agent = getattr(agent_service, agent_name.lower())
            
            start_time = time.time()
            response = await asyncio.wait_for(
                asyncio.to_thread(agent.send_message, message),
                timeout=30.0
            )
            elapsed_ms = (time.time() - start_time) * 1000
            
            results[agent_name] = {
                "status": "ok",
                "elapsed_ms": elapsed_ms,
                "response_length": len(response),
                "response": response[:500],
            }
            
            logger.info_event(
                "ai_test",
                agent=agent_name,
                elapsed_ms=elapsed_ms,
                response_length=len(response)
            )
        except asyncio.TimeoutError:
            results[agent_name] = {
                "status": "timeout",
                "message": "Request timed out after 30 seconds",
            }
        except Exception as e:
            results[agent_name] = {
                "status": "error",
                "error": str(e)[:200],
            }
    
    return {
        "status": "ok",
        "test_message": message,
        "results": results,
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for deployment readiness.
    """
    from backend.services import agent_service
    
    checks = {
        "api": "ok",
        "agents_initialized": False,
        "api_keys_configured": False,
        "db_accessible": False,
        "warnings": [],
    }
    
    # Check agents
    try:
        checks["agents_initialized"] = (
            agent_service.infiltrator.client is not None and
            agent_service.forensic.client is not None and
            agent_service.mentor.client is not None
        )
    except:
        pass
    
    # Check API keys
    checks["api_keys_configured"] = bool(EnvConfig.GROQ_API_KEY)
    if not checks["api_keys_configured"]:
        checks["warnings"].append("No GROQ API key configured - using fallback scenarios")
    
    # Check database
    try:
        from backend.database_models import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks["db_accessible"] = True
    except Exception as e:
        checks["warnings"].append(f"Database check failed: {str(e)[:100]}")
    
    # Config validation
    is_valid, config_warnings = EnvConfig.validate_startup()
    checks["config_valid"] = is_valid
    checks["warnings"].extend(config_warnings)
    
    return {
        "status": "ok" if not checks["warnings"] else "warning",
        "timestamp": asyncio.get_event_loop().time(),
        "checks": checks,
    }
