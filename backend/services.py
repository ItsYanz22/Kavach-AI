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
import random

from backend.agents.agent_manager import AgentManager
from backend.database_models import DetectionHistory
from backend.fallback_scenarios import FallbackScenarioEngine
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
        self.fallback_engine = FallbackScenarioEngine()
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
    
    async def generate_scam_scenario(self, session_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Generate a fresh, unique, high-fidelity cybercrime scenario using Groq AI.
        Uses session-aware history to avoid repeating recent scenario types, personas, or storylines.
        Falls back gracefully to the diverse 25-category taxonomy if Groq is unavailable.
        """
        try:
            if not self.infiltrator.client:
                logger.info("AI client not available, selecting diverse fallback scenario")
                exclude = [s.get("scenario_type") for s in session_history if s.get("scenario_type")] if session_history else None
                return self.fallback_engine.generate_random_scenario(exclude_types=exclude)

            # Build history exclusion instructions if past scenarios exist for this session
            history_prompt = ""
            if session_history:
                recent_lines = []
                for s in session_history[-6:]:
                    s_type = s.get("scenario_type", "unknown")
                    s_title = s.get("ui_title", "")
                    s_persona = s.get("attacker_persona", "")
                    recent_lines.append(f"- Type: {s_type} | Persona: {s_persona} | Title: {s_title}")
                
                history_prompt = (
                    "\n\nRECENT SCENARIOS ALREADY PLAYED IN THIS SESSION (DO NOT REPEAT OR CLOSELY RESEMBLE THESE):\n"
                    + "\n".join(recent_lines) + "\n"
                    "CRITICAL: You MUST choose a COMPLETELY DIFFERENT category from the 25 taxonomy types, "
                    "with a totally different narrative, attacker persona, and manipulation strategy!"
                )

            prompt = (
                "You are generating a fresh cyber-safety simulation scenario for the Kavach AI War Room.\n"
                "Select ONE distinct attack category from the 25-category taxonomy (e.g. upi_fraud, electricity_threat, "
                "digital_arrest, customs_parcel, job_scam, qr_code_scam, kyc_phishing, otp_theft, etc.) that hasn't been used recently.\n"
                "Use authentic Indian digital ecosystem context (e.g., UPI, PhonePe, Paytm, SBI, FedEx, Mumbai Police, BSES, India Post).\n"
                f"{history_prompt}\n\n"
                "Return ONLY a valid JSON object with NO markdown, NO backticks, and NO commentary outside the JSON:\n"
                "{\n"
                '  "scenario_type": "one_of_the_25_taxonomy_types",\n'
                '  "difficulty": "medium",\n'
                '  "attacker_persona": "Specific role, e.g. Customer Support Specialist",\n'
                '  "victim_context": "Why user received this alert",\n'
                '  "message": "Realistic initial scam message with persuasive hook and fictional URL/number",\n'
                '  "initial_message": "Same text as message",\n'
                '  "conversation_goal": "What the attacker wants user to do",\n'
                '  "manipulation_tactics": ["urgency", "authority impersonation", "fear"],\n'
                '  "risk_indicators": ["unverified link", "threatening tone", "unknown sender"],\n'
                '  "dangerous_action": "approve_payment|verify_credentials|download_file",\n'
                '  "safe_actions": ["ignore", "analyse", "block", "report"],\n'
                '  "educational_explanation": "Why this message is fraudulent and how the attack works",\n'
                '  "recommended_response": "Best practice action the user should take",\n'
                '  "ui_title": "Concise UI title with emoji (e.g. ⚡ Electricity Disconnection Alert)",\n'
                '  "ui_description": "1-sentence summary of the deceptive tactic",\n'
                '  "amount": 2840,\n'
                '  "tip": "Short, memorable cyber security rule of thumb",\n'
                '  "danger_button_label": "🔴 Contextual Dangerous Action (e.g. Pay ₹2,840 Bill / Approve UPI)",\n'
                '  "await_user_response": true\n'
                "}"
            )

            logger.info("Calling Groq AI to generate diverse scenario...")
            result = await asyncio.wait_for(
                asyncio.to_thread(self.infiltrator.send_message, prompt, temperature=0.85, max_tokens=1400),
                timeout=self.call_timeout_seconds
            )

            parsed = extract_json_from_text(result)

            if not parsed or not parsed.get("message") or not parsed.get("ui_title"):
                logger.warning(f"Failed to parse valid scenario from Groq output. Raw: {result[:200] if result else 'empty'}")
                exclude = [s.get("scenario_type") for s in session_history if s.get("scenario_type")] if session_history else None
                return self.fallback_engine.generate_random_scenario(exclude_types=exclude)

            # Ensure message fields are synchronized
            msg = parsed.get("message") or parsed.get("initial_message") or ""
            parsed["message"] = msg
            parsed["initial_message"] = msg

            # Build contextual action buttons (danger button reflects the exact scenario)
            danger_label = parsed.get("danger_button_label")
            if not danger_label:
                amt = parsed.get("amount", 0)
                if amt and amt > 0:
                    danger_label = f"🔴 Pay ₹{amt:,}"
                elif "kyc" in parsed.get("scenario_type", "").lower() or "verify" in msg.lower():
                    danger_label = "🔴 Verify Credentials"
                elif "download" in msg.lower() or "apk" in msg.lower():
                    danger_label = "🔴 Download & Install"
                else:
                    danger_label = "🔴 Comply & Proceed"

            parsed["recommended_actions"] = [
                {"label": danger_label, "action_id": "pay", "type": "danger"},
                {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
                {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
                {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
                {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
            ]

            parsed["escalation_stage"] = 1
            parsed["await_user_response"] = True
            parsed["next_step"] = "wait_for_user"
            parsed["is_ai_generated"] = True
            parsed["generation_source"] = "groq"
            parsed["model_used"] = getattr(self.infiltrator, "active_model", "groq")

            logger.info(f"✅ Live Groq scenario generated: type={parsed.get('scenario_type')} model={parsed.get('model_used')}")
            return parsed

        except asyncio.TimeoutError:
            logger.error(f"Scenario generation timeout after {self.call_timeout_seconds}s, using fallback")
            exclude = [s.get("scenario_type") for s in session_history if s.get("scenario_type")] if session_history else None
            return self.fallback_engine.generate_random_scenario(exclude_types=exclude)
        except Exception as e:
            logger.error(f"Scenario generation error: {e}", exc_info=True)
            exclude = [s.get("scenario_type") for s in session_history if s.get("scenario_type")] if session_history else None
            return self.fallback_engine.generate_random_scenario(exclude_types=exclude)

    async def continue_scenario(self, scenario: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """
        Continue an active scenario based on the user's specific response.
        Maintains conversational coherence within the SAME scenario storyline without switching topics.
        """
        try:
            current_stage = int(scenario.get("escalation_stage", 1))
            next_stage = current_stage + 1
            scenario_type = scenario.get("scenario_type") or scenario.get("scam_type") or "social_engineering"
            persona = scenario.get("attacker_persona") or scenario.get("scammer_personality") or "The Scammer"
            original_message = scenario.get("message", "")
            ui_title = scenario.get("ui_title", "⚠️ Ongoing Security Simulation")
            ui_desc = scenario.get("ui_description", "")
            amount = scenario.get("amount", 0)

            # Check for terminal user actions
            lower_msg = user_message.lower().strip()
            if "block" in lower_msg or "[system: user blocked" in lower_msg:
                return {
                    "message": "🚫 Sender has been blocked. The connection has been severed. You successfully stopped this social engineering attack!",
                    "escalation_stage": 5,
                    "resolved": True,
                    "risk_level": "resolved",
                    "ui_title": ui_title,
                    "ui_description": "Attack successfully neutralized by blocking.",
                    "tip": "Blocking the sender is the single most effective countermeasure against cyber deception.",
                    "recommended_actions": [],
                    "await_user_response": False
                }

            if "report" in lower_msg or "[system: user reported" in lower_msg:
                return {
                    "message": "⚠️ Scam reported to authorities. Incident logs archived. Well done staying vigilant!",
                    "escalation_stage": 5,
                    "resolved": True,
                    "risk_level": "resolved",
                    "ui_title": ui_title,
                    "ui_description": "Incident reported. Threat neutralized.",
                    "tip": "Reporting suspicious messages helps cybersecurity teams shut down phishing infrastructure.",
                    "recommended_actions": [],
                    "await_user_response": False
                }

            # If scenario reached stage 5+, resolve
            if current_stage >= 4:
                return {
                    "message": "The scammer has terminated the session after realizing you are not complying. Excellent defense!",
                    "escalation_stage": 5,
                    "resolved": True,
                    "risk_level": "resolved",
                    "ui_title": ui_title,
                    "ui_description": "Scammer abandoned the attempt after repeated resistance.",
                    "tip": "Scammers operate on volume; when they encounter persistent friction or delay, they move on.",
                    "recommended_actions": [],
                    "await_user_response": False
                }

            # If Groq is not available, provide coherent context-aware fallback continuation
            if not self.infiltrator.client:
                return self._generate_contextual_continuation_fallback(scenario, user_message, next_stage)

            prompt = (
                f"You are the scammer in an active cyber-safety training simulation.\n"
                f"CRITICAL RULE: You MUST continue the EXACT active conversation below. DO NOT SWITCH TOPICS OR START A NEW SCAM.\n\n"
                f"ACTIVE SCENARIO CONTEXT:\n"
                f"- Scenario Type: {scenario_type}\n"
                f"- Your Attacker Persona: {persona}\n"
                f"- Initial Scam Hook: {original_message}\n"
                f"- Current Conversation Stage: Turn #{current_stage}\n"
                f"- User's Response: \"{user_message}\"\n\n"
                f"INSTRUCTIONS FOR YOUR RESPONSE (Turn #{next_stage}):\n"
                f"1. If user questioned you, said 'no', expressed doubt, or asked for proof:\n"
                f"   Stay in character. Provide plausible-sounding bureaucratic justification, cite fake reference numbers/regulations, "
                f"   and increase urgency to convince them to comply.\n"
                f"2. If user ignored the message (or user says '[SYSTEM: User ignored the message]'):\n"
                f"   Send a follow-up pressure reminder asking if they are there, warning that the deadline is expiring.\n"
                f"3. If user complied or asked what to do:\n"
                f"   Guide them step-by-step toward the trap (approving the UPI request, sharing the OTP, or clicking the mock link).\n\n"
                f"Return ONLY a valid JSON object (no markdown, no backticks):\n"
                f"{{\n"
                f'  "message": "Your next message continuing THIS exact scenario",\n'
                f'  "escalation_stage": {next_stage},\n'
                f'  "ui_title": "{ui_title}",\n'
                f'  "ui_description": "{ui_desc}",\n'
                f'  "amount": {amount},\n'
                f'  "tip": "Security tip explaining the persuasion tactic you just used in this turn",\n'
                f'  "danger_button_label": "🔴 Contextual Action Label",\n'
                f'  "resolved": false\n'
                f"}}"
            )

            result = await asyncio.wait_for(
                asyncio.to_thread(self.infiltrator.send_message, prompt, temperature=0.75, max_tokens=900),
                timeout=self.call_timeout_seconds
            )

            parsed = extract_json_from_text(result)

            if not parsed or not parsed.get("message"):
                return self._generate_contextual_continuation_fallback(scenario, user_message, next_stage)

            # Preserve UI metadata
            parsed["escalation_stage"] = next_stage
            parsed["ui_title"] = parsed.get("ui_title") or ui_title
            parsed["ui_description"] = parsed.get("ui_description") or ui_desc
            parsed["amount"] = parsed.get("amount") if parsed.get("amount") is not None else amount

            # Generate actions matching the continued scenario
            danger_label = parsed.get("danger_button_label") or scenario.get("danger_button_label")
            if not danger_label:
                if amount and amount > 0:
                    danger_label = f"🔴 Pay ₹{amount:,}"
                else:
                    danger_label = "🔴 Comply & Proceed"

            parsed["recommended_actions"] = [
                {"label": danger_label, "action_id": "pay", "type": "danger"},
                {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
                {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
                {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
                {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
            ]
            parsed["await_user_response"] = True

            return parsed

        except asyncio.TimeoutError:
            logger.error("Scenario continuation timeout - generating fallback continuation")
            return self._generate_contextual_continuation_fallback(scenario, user_message, current_stage + 1)
        except Exception as e:
            log_llm_error("continue_scenario", e, user_message[:50])
            return self._generate_contextual_continuation_fallback(scenario, user_message, current_stage + 1)

    def _generate_contextual_continuation_fallback(
        self,
        scenario: Dict[str, Any],
        user_message: str,
        stage: int
    ) -> Dict[str, Any]:
        """Generate a coherent continuation within the active scenario context without switching to another scam."""
        s_type = scenario.get("scenario_type") or scenario.get("scam_type") or "general"
        ui_title = scenario.get("ui_title", "⚠️ Ongoing Security Simulation")
        ui_desc = scenario.get("ui_description", "")
        amount = scenario.get("amount", 0)

        is_ignore = "[system: user ignored" in user_message.lower()
        is_doubt = any(w in user_message.lower() for w in ["who", "why", "no", "fake", "proof", "how"])

        if is_ignore:
            msg = "Sir/Madam, are you there? This is an automated final notice. If you do not respond immediately, your account/service will be suspended as per protocol."
            tip = "Scammers follow up quickly when ignored to re-engage their victims before they consult others."
        elif is_doubt:
            msg = f"I understand your hesitation, but this is a time-sensitive alert under Case Reference #{random.randint(10000, 99999)}. We cannot verify details over public chat; please click the link to confirm your identity."
            tip = "Scammers often respond to doubt by referencing fake case numbers or official policies to rebuild authority."
        else:
            msg = f"Thank you for confirming. To complete the verification and prevent penalties, please approve the pending request of ₹{amount:,} or submit the requested details now."
            tip = "Once initial compliance is established, scammers push directly for the financial or data transfer."

        return {
            "message": msg,
            "escalation_stage": stage,
            "ui_title": ui_title,
            "ui_description": ui_desc,
            "amount": amount,
            "tip": tip,
            "recommended_actions": [
                {"label": f"🔴 Comply (₹{amount:,})" if amount else "🔴 Comply & Proceed", "action_id": "pay", "type": "danger"},
                {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
                {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
                {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
                {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
            ],
            "await_user_response": True,
            "resolved": False
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
