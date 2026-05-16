"""
Production agent service layer for Kavach AI.
Wraps AgentManager with:
- Structured response parsing
- Error handling & fallbacks
- Timeout management
- Rate limiting
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import json

from backend.agents.agent_manager import AgentManager
from backend.database_models import DetectionHistory
from backend.utils import (
    extract_json_from_text,
    safe_get,
    log_llm_error,
    create_fallback_scam_scenario,
    create_fallback_health_score,
    generate_dynamic_amount,
    generate_dynamic_tip,
    generate_dynamic_ui_title,
    generate_dynamic_ui_description,
    generate_dynamic_actions,
    infer_scam_type_from_message,
)

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service layer for AI agents.
    Handles response parsing, error recovery, and structured outputs.
    """
    
    def __init__(self):
        self.infiltrator = AgentManager("Infiltrator")
        self.forensic = AgentManager("Forensic")
        self.mentor = AgentManager("Mentor")
        self.call_timeout_seconds = 30
    
    async def detect_message(self, message: str, db=None, user_id=None) -> Dict[str, Any]:
        """
        Detect if a message is a scam using the Forensic Agent.
        
        Returns:
            {"classification": "SCAM" or "SAFE", "confidence": 0.0-1.0, "reason": str}
        """
        try:
            prompt = (
                "Classify the following message as SCAM or SAFE.\n"
                "Return ONLY a valid JSON object with NO markdown formatting, NO backticks:\n"
                "{\n"
                '  "classification": "Scam" or "Safe",\n'
                '  "confidence": 0.95,\n'
                '  "reason": "Brief explanation"\n'
                "}\n\n"
                f"Message:\n{message}"
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.forensic.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed:
                logger.warning("Detection response not JSON, using fallback")
                return {
                    "classification": "SAFE",
                    "confidence": 0.5,
                    "reason": "Unable to parse AI response, defaulting to SAFE"
                }
            
            # Normalize classification to uppercase
            classification = parsed.get("classification", "Safe")
            if isinstance(classification, str):
                if "scam" in classification.lower():
                    classification = "SCAM"
                else:
                    classification = "SAFE"
            else:
                classification = "SAFE"
            
            confidence = min(1.0, max(0.0, float(parsed.get("confidence", 0.5))))
            reason = str(parsed.get("reason", "Analysis complete"))
            
            result = {
                "classification": classification,
                "confidence": confidence,
                "reason": reason
            }
            
            # Save to database if provided
            if db and user_id:
                try:
                    history_entry = DetectionHistory(
                        user_id=user_id,
                        message=message,
                        classification=classification,
                        confidence=confidence,
                        reason=reason
                    )
                    db.add(history_entry)
                    db.commit()
                except Exception as db_err:
                    logger.error(f"Failed to save detection history: {db_err}")
            
            return result
        
        except asyncio.TimeoutError:
            logger.error("Detection timeout")
            return {
                "classification": "SAFE",
                "confidence": 0.3,
                "reason": "Detection timed out - defaulting to SAFE"
            }
        except Exception as e:
            log_llm_error("detect", e, message[:50])
            return {
                "classification": "SAFE",
                "confidence": 0.5,
                "reason": "Detection error - defaulting to SAFE"
            }
    
    async def explain_message(self, message: str) -> Dict[str, Any]:
        """
        Explain why a message is a scam.
        
        Returns:
            {
                "message_parts": [...],
                "highlights": [...],
                "reasons": [...]
            }
        """
        try:
            prompt = (
                f"Analyze this scam message in deep detail:\n{message}\n\n"
                "Return ONLY valid JSON (NO markdown, NO backticks):\n"
                "{\n"
                '  "message_parts": [\n'
                '    {"text": "plain text", "highlight_index": null},\n'
                '    {"text": "suspicious text", "highlight_index": 0}\n'
                "  ],\n"
                '  "highlights": [\n'
                "    {\n"
                '      "label": "Tactic Name",\n'
                '      "color": "danger|warning|cyber",\n'
                '      "icon": "Link|Clock|Building|AlertTriangle|PhoneOff|Eye",\n'
                '      "tooltip": "Why suspicious",\n'
                '      "text": "Exact highlighted text"\n'
                "    }\n"
                "  ],\n"
                '  "reasons": ["reason 1", "reason 2"]\n'
                "}"
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.forensic.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed:
                logger.warning("Explain response not JSON, using generic fallback")
                return {
                    "message_parts": [{"text": message, "highlight_index": None}],
                    "highlights": [],
                    "reasons": ["This message appears suspicious"]
                }
            
            return {
                "message_parts": parsed.get("message_parts", [{"text": message, "highlight_index": None}]),
                "highlights": parsed.get("highlights", []),
                "reasons": parsed.get("reasons", ["Suspicious message detected"])
            }
        
        except asyncio.TimeoutError:
            logger.error("Explain timeout")
            return {
                "message_parts": [{"text": message, "highlight_index": None}],
                "highlights": [],
                "reasons": ["Analysis timed out"]
            }
        except Exception as e:
            log_llm_error("explain", e, message[:50])
            return {
                "message_parts": [{"text": message, "highlight_index": None}],
                "highlights": [],
                "reasons": ["Unable to analyze - appears suspicious"]
            }
    
    async def recommend_actions(self, message: str) -> Dict[str, Any]:
        """
        Recommend actions for user.
        
        Returns:
            {"actions": [{"icon": ..., "text": ..., "detail": ...}]}
        """
        try:
            prompt = (
                f"What should user do about this message?\n{message}\n\n"
                "Return ONLY valid JSON (NO markdown, NO backticks):\n"
                "{\n"
                '  "actions": [\n'
                "    {\n"
                '      "icon": "Ban|Phone|Shield|CheckCircle",\n'
                '      "text": "Short action text",\n'
                '      "detail": "Detailed explanation"\n'
                "    }\n"
                "  ]\n"
                "}"
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.mentor.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed or "actions" not in parsed:
                logger.warning("Actions response not JSON, using fallback")
                return {
                    "actions": [
                        {"icon": "Ban", "text": "Do not click links", "detail": "Unknown senders often hide malware"},
                        {"icon": "Phone", "text": "Verify directly", "detail": "Call official number from your bank card"}
                    ]
                }
            
            return {"actions": parsed.get("actions", [])}
        
        except asyncio.TimeoutError:
            logger.error("Actions timeout")
            return {
                "actions": [
                    {"icon": "Ban", "text": "Do not engage", "detail": "Analysis timed out"}
                ]
            }
        except Exception as e:
            log_llm_error("action", e, message[:50])
            return {
                "actions": [
                    {"icon": "Shield", "text": "Stay safe", "detail": "Use caution with suspicious messages"}
                ]
            }
    
    async def generate_scam_scenario(self) -> Dict[str, Any]:
        """
        Generate a realistic, high-fidelity scam scenario.
        """
        try:
            prompt = (
                "STart a new cyber-scam simulation session.\n"
                "Follow TURN 1 (THE HOOK) logic. Do not jump to the trap immediately.\n"
                "Return ONLY valid JSON with the exact schema defined in your instructions."
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.infiltrator.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed or not parsed.get("message"):
                logger.warning("Scenario generation failed, using fallback")
                return create_fallback_scam_scenario("Generation failed")
            
            # Ensure stage is set to 1 for initial message
            parsed["escalation_stage"] = 1
            return parsed
        
        except Exception as e:
            logger.error(f"Scenario generation error: {e}")
            return create_fallback_scam_scenario(str(e))

    async def continue_scenario(self, scenario: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """
        Continue an active scenario based on user response, progressing through stages.
        """
        try:
            current_stage = int(scenario.get("escalation_stage", 1))
            next_stage = current_stage + 1
            personality = scenario.get("scammer_personality", "Standard")
            
            prompt = (
                f"PERSISTENCE: You are acting as: {personality}\n"
                f"CURRENT STAGE: {current_stage}\n"
                f"USER REPLIED: {user_message}\n\n"
                f"GOAL: Progress to STAGE {next_stage}. Adapt your tone based on the user's reply.\n"
                "If the user is suspicious, try to reassure them or escalate urgency.\n"
                "If the user is falling for it, move closer to THE TRAP.\n"
                "Return ONLY valid JSON with updated 'escalation_stage'."
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.infiltrator.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed:
                logger.warning("Scenario continuation failed")
                return {
                    "message": "The scammer has disconnected. You managed to avoid the trap... for now.",
                    "risk_level": "low",
                    "escalation_stage": current_stage,
                    "tip": "Always be wary of unsolicited messages that try to build trust over time."
                }
            
            # Update stage if not present in response
            if "escalation_stage" not in parsed:
                parsed["escalation_stage"] = next_stage
                
            return parsed
        
        except asyncio.TimeoutError:
            logger.error("Scenario continuation timeout")
            return {
                "message": "System timeout - scenario ended",
                "risk_level": "medium",
            }
        except Exception as e:
            log_llm_error("continue_scenario", e, user_message[:50])
            return {
                "message": "Scenario ended due to error",
                "risk_level": "low",
            }
    
    async def evaluate_health(self) -> Dict[str, Any]:
        """
        Evaluate session security health.
        
        Returns:
            {"score": 0-100, "alerts": [...]}
        """
        try:
            prompt = (
                "Provide a security health score (0-100) for a cyber security learning session. "
                "Include 2-3 recent alerts.\n\n"
                "Return ONLY valid JSON (NO markdown, NO backticks):\n"
                "{\n"
                '  "score": 75,\n'
                '  "alerts": [\n'
                '    {"time": "Just now", "text": "Alert message", "type": "warning|danger|safe"}\n'
                "  ]\n"
                "}"
            )
            
            result = await asyncio.wait_for(
                asyncio.to_thread(self.mentor.send_message, prompt),
                timeout=self.call_timeout_seconds
            )
            
            parsed = extract_json_from_text(result)
            
            if not parsed:
                return create_fallback_health_score()
            
            score = max(0, min(100, int(parsed.get("score", 75))))
            alerts = parsed.get("alerts", [])
            
            return {
                "score": score,
                "alerts": alerts
            }
        
        except asyncio.TimeoutError:
            logger.error("Health evaluation timeout")
            return create_fallback_health_score()
        except Exception as e:
            log_llm_error("health_score", e)
            return create_fallback_health_score()


# Global agent service instance
agent_service = AgentService()
