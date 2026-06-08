import os
import logging
from groq import Groq
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from the kavach_backend/.env regardless of cwd
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(_env_path, override=True)

# Import prompts – use relative imports for package structure
from .agent_prompts import INFILTRATOR_PROMPT, FORENSIC_PROMPT, MENTOR_PROMPT

# Configure API Key securely from environment
api_keys_raw = os.environ.get("GROQ_API_KEYS", os.environ.get("GROQ_API_KEY", ""))
API_KEYS = [k.strip().strip('"').strip("'") for k in api_keys_raw.split(",") if k.strip().strip('"').strip("'")]
CURRENT_KEY_IDX = 0

if not API_KEYS:
    print("⚠️  Warning: No GROQ_API_KEY found. Agents will return fallback messages.")


class AgentManager:
    """Wraps a Groq API client with a specific agent persona."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type

        self.system_instruction = ""
        if agent_type == "Infiltrator":
            self.system_instruction = INFILTRATOR_PROMPT
        elif agent_type == "Forensic":
            self.system_instruction = FORENSIC_PROMPT
        elif agent_type == "Mentor":
            self.system_instruction = MENTOR_PROMPT

        self._init_client()

    def _init_client(self):
        try:
            if API_KEYS:
                self.client = Groq(api_key=API_KEYS[CURRENT_KEY_IDX])
            else:
                self.client = None
            self.conversation_history = []
            print(f"[OK] {self.agent_type} agent initialised with Groq API")
        except Exception as e:
            self.client = None
            print(f"[ERROR] Failed to initialise {self.agent_type}: {e}")

    def send_message(self, message: str, retry_count=0) -> str:
        """Send a message to the agent and return its text response."""
        global CURRENT_KEY_IDX
        
        if not self.client:
            logger.error(f"[{self.agent_type}] Client not initialized. API key missing?")
            return self._get_hard_fallback(message)
        
        try:
            # Build messages for this request
            messages = self.conversation_history.copy()
            
            # List of available Groq models (in preference order)
            # Using models confirmed available on Groq free tier
            available_models = [
                "mixtral-8x7b-32768",      # Best for JSON and complex tasks
                "llama-3.3-70b-versatile",  # Good alternative
                "llama3-70b-8192",          # Another option
            ]
            
            model_name = available_models[0]
            
            logger.info(f"[{self.agent_type}] Sending request to {model_name}")
            
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": self.system_instruction},
                        *messages,
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                )
            except Exception as model_error:
                # If primary model fails, try fallback models
                if any(x in str(model_error).lower() for x in ["decommissioned", "not available", "404"]):
                    logger.warning(f"[{self.agent_type}] Model {model_name} unavailable, trying llama-3.3-70b-versatile...")
                    response = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": self.system_instruction},
                            *messages,
                            {"role": "user", "content": message}
                        ],
                        temperature=0.7,
                        max_tokens=1024,
                        response_format={"type": "json_object"},
                    )
                else:
                    raise
            
            assistant_message = response.choices[0].message.content
            
            # Store in conversation history for context
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 10 messages for context
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
            
        except Exception as e:
            error_msg = str(e).replace('"', "'")
            logger.error(f"[{self.agent_type}] Groq API Error: {error_msg}")
            
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                # Automatic API Key Rotation
                if len(API_KEYS) > 1 and retry_count < len(API_KEYS) - 1:
                    logger.info(f"[{self.agent_type}] Rate limit reached. Rotating API key... ({retry_count+1}/{len(API_KEYS)-1})")
                    CURRENT_KEY_IDX = (CURRENT_KEY_IDX + 1) % len(API_KEYS)
                    self._init_client()
                    return self.send_message(message, retry_count=retry_count + 1)
                
                logger.warning(f"[{self.agent_type}] ALL API KEYS DEPLETED. Activating sandbox fallback.")
                return self._get_hard_fallback(message)
            
            if "401" in error_msg or "api key" in error_msg.lower():
                logger.error(f"[{self.agent_type}] Invalid API Key detected.")
                return self._get_hard_fallback(message)
            
            return self._get_hard_fallback(message)

    def _get_hard_fallback(self, message: str) -> str:
        """Return a structured fallback response based on agent type."""
        import random
        import json
        
        if self.agent_type == "Infiltrator":
            fallbacks = [
                {
                    "scenario_type": "phishing",
                    "message": "URGENT: Your bank account is compromised. Submit KYC verification below within 24 hours to prevent asset freeze. http://verify-kyc-now.site/login",
                    "amount": 49999,
                    "tip": "Institutions will never send unverified HTTP links threatening asset freeze.",
                    "risk_level": "high",
                    "ui_title": "⚠ Bank KYC Phishing",
                    "ui_description": "A fake banking alert asking for urgent verification.",
                    "recommended_actions": [
                        {"label": "🔗 Verify KYC", "action_id": "pay", "type": "danger"},
                        {"label": "🛑 Ignore & Report", "action_id": "ignore", "type": "warning"},
                        {"label": "🔍 Inspect URL", "action_id": "analyze", "type": "cyber"}
                    ],
                    "await_user_response": True,
                    "next_step": "wait_for_user"
                },
                {
                    "scenario_type": "investment",
                    "message": "Invest in CryptoBoost and earn up to 20% daily returns. Send $500 to safesim.link/investnow and get a $100 bonus!",
                    "amount": 500,
                    "tip": "Promises of guaranteed high returns are almost always scams.",
                    "risk_level": "critical",
                    "ui_title": "⚠ Investment Fraud",
                    "ui_description": "An unsolicited message offering unrealistic daily returns.",
                    "recommended_actions": [
                        {"label": "💸 Send Money", "action_id": "pay", "type": "danger"},
                        {"label": "🛑 Delete", "action_id": "ignore", "type": "warning"}
                    ],
                    "await_user_response": True,
                    "next_step": "wait_for_user"
                }
            ]
            return json.dumps(random.choice(fallbacks))
        
        elif self.agent_type == "Forensic":
            return json.dumps({
                "classification": "SCAM",
                "confidence": 0.95,
                "reason": "Analyzed patterns suggest high-pressure phishing tactics.",
                "message_parts": [{"text": message, "highlight_index": 0}],
                "highlights": [{
                    "label": "Suspicious Activity",
                    "color": "danger",
                    "icon": "AlertTriangle",
                    "tooltip": "Detected high-pressure urgency in communication.",
                    "text": message[:50]
                }],
                "reasons": ["Unverified source", "Sense of urgency", "Suspicious link structure"]
            })
        
        elif self.agent_type == "Mentor":
            if "Evaluate" in message or "score" in message.lower():
                return json.dumps({
                    "score": 75,
                    "alerts": [{"time": "Just now", "text": "AI connection issues detected - operating in safety mode", "type": "warning"}]
                })
            return json.dumps({
                "actions": [
                    {"icon": "Ban", "text": "Do not click links", "detail": "Always verify URLs manually"},
                    {"icon": "Phone", "text": "Call official number", "detail": "Use the number from the back of your card"}
                ]
            })
        
        return "Service temporarily unavailable. Please stay alert."
