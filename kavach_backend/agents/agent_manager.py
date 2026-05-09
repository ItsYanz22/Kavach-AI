import os
from groq import Groq
from dotenv import load_dotenv

# Load from the kavach_backend/.env regardless of cwd
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(_env_path, override=True)

# Import prompts – works when running from kavach_backend/ directory
from agents.agent_prompts import INFILTRATOR_PROMPT, FORENSIC_PROMPT, MENTOR_PROMPT

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
            return (
                "Agent unavailable – API key missing or invalid configuration. "
                "Please check your .env file."
            )
        
        try:
            # Build messages for this request
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": message})
            
            # List of available Groq models (in preference order)
            # These are currently active models - update if deprecated
            available_models = [
                "llama-3.1-8b-instant",          # Fastest and highest rate limit
                "llama-3.3-70b-versatile",       # Latest Llama 3.3 (70B)
                "llama3-70b-8192",               # Llama 3 (70B)
                "mixtral-8x7b-32768",            # Mixtral (8x7B)
                "gemma2-9b-it",                  # Gemma 2 (9B) - lightweight fallback
            ]
            
            model_name = available_models[0]  # Try first model
            
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": self.system_instruction},
                        *messages
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                )
            except Exception as model_error:
                # If primary model fails, try fallback
                if "decommissioned" in str(model_error).lower() or "not available" in str(model_error).lower():
                    print(f"[WARN] Model {model_name} unavailable, trying fallback...")
                    # Try gemma2 as a lightweight, reliable fallback
                    response = self.client.chat.completions.create(
                        model="gemma2-9b-it",
                        messages=[
                            {"role": "system", "content": self.system_instruction},
                            *messages
                        ],
                        temperature=0.7,
                        max_tokens=1024,
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
            print(f"\n[CRITICAL] Groq API Error:\n{error_msg}\n")
            
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                # Automatic API Key Rotation
                if len(API_KEYS) > 1 and retry_count < len(API_KEYS) - 1:
                    print(f"[INFO] Rate limit reached. Rotating API key and retrying... ({retry_count+1}/{len(API_KEYS)-1})")
                    CURRENT_KEY_IDX = (CURRENT_KEY_IDX + 1) % len(API_KEYS)
                    self._init_client()
                    return self.send_message(message, retry_count=retry_count + 1)
                
                print("\n" + "="*50)
                print("[WARNING] ALL GROQ API KEYS DEPLETED OR RATE LIMITED!")
                print("Your API key has hit the rate limit or expired.")
                print("Activating Fallback Offline Sandbox Mode with predefined scenarios.")
                print("="*50 + "\n")
                if self.agent_type == "Infiltrator":
                    import random
                    fallbacks = [
                        '{"scenario_type": "phishing", "message": "URGENT: Your bank account is compromised. Submit KYC verification below within 24 hours to prevent asset freeze. http://verify-kyc-now.site/login", "amount": 49999, "tip": "Institutions will never send unverified HTTP links threatening asset freeze.", "risk_level": "high", "ui_title": "⚠ Bank KYC Phishing", "ui_description": "A fake banking alert asking for urgent verification.", "recommended_actions": [{"label": "🔗 Verify KYC", "action_id": "pay", "type": "danger"}, {"label": "🛑 Ignore & Report", "action_id": "ignore", "type": "warning"}, {"label": "🔍 Inspect URL", "action_id": "analyze", "type": "cyber"}], "await_user_response": true}',
                        '{"scenario_type": "investment", "message": "Invest in CryptoBoost and earn up to 20% daily returns. Limited spots available. Send $5000 to safesim.link/investnow and get a $1000 bonus. Hurry, offer ends soon!", "amount": 5000, "tip": "Promises of guaranteed high returns are almost always scams.", "risk_level": "critical", "ui_title": "⚠ Investment Fraud", "ui_description": "An unsolicited message offering unrealistic daily returns.", "recommended_actions": [{"label": "💸 Send Money", "action_id": "pay", "type": "danger"}, {"label": "🛑 Delete Message", "action_id": "ignore", "type": "warning"}, {"label": "🔍 Analyze", "action_id": "analyze", "type": "cyber"}], "await_user_response": true}',
                        '{"scenario_type": "delivery", "message": "IndiaPost: Your package could not be delivered due to unpaid customs fee of ₹45. Pay now to release your package: safesim.link/indiapost-fee", "amount": 45, "tip": "Scammers use low fees to steal your card details during payment.", "risk_level": "medium", "ui_title": "⚠ Fake Delivery Fee", "ui_description": "A smishing text pretending to be a postal service holding a package.", "recommended_actions": [{"label": "💳 Pay ₹45", "action_id": "pay", "type": "danger"}, {"label": "🛑 Block Sender", "action_id": "ignore", "type": "warning"}, {"label": "🔍 Check URL", "action_id": "analyze", "type": "cyber"}], "await_user_response": true}',
                        '{"scenario_type": "utility", "message": "Dear customer, your electricity power will be disconnected at 9:30 PM tonight due to pending bill update. Call our officer at 9876543210 immediately.", "amount": 12500, "tip": "Official utility boards never threaten immediate disconnection via SMS.", "risk_level": "high", "ui_title": "⚠ Electricity Disconnection Threat", "ui_description": "A high-pressure tactic forcing you to call a fake customer service number.", "recommended_actions": [{"label": "📞 Call Officer", "action_id": "pay", "type": "danger"}, {"label": "🛑 Ignore", "action_id": "ignore", "type": "warning"}, {"label": "🔍 Analyze Text", "action_id": "analyze", "type": "cyber"}], "await_user_response": true}'
                    ]
                    return random.choice(fallbacks)
                
                elif self.agent_type == "Forensic":
                    return """{
                     "classification": "Scam",
                     "confidence": 0.99,
                     "reason": "Sandbox identified strict urgency and external malicious links.",
                     "message_parts": [
                       { "text": "URGENT: Your bank account is compromised. ", "highlight_index": 0 },
                       { "text": "Submit KYC verification below within 24 hours to prevent asset freeze.", "highlight_index": 1 },
                       { "text": " http://verify-kyc-now.site/login", "highlight_index": 2 }
                     ],
                     "highlights": [
                       { "label": "Emotional Pressure", "color": "danger", "icon": "AlertTriangle", "tooltip": "Leverages fear of losing assets to force quick compliance.", "text": "URGENT: Your bank account is compromised." },
                       { "label": "False Urgency", "color": "warning", "icon": "Clock", "tooltip": "Tight 24 hour deadline induces panic.", "text": "Submit KYC verification below within 24 hours to prevent asset freeze." },
                       { "label": "Malicious Phishing Link", "color": "cyber", "icon": "Link", "tooltip": "Suspicious HTTP site completely unrelated to a real bank dashboard.", "text": " http://verify-kyc-now.site/login" }
                     ],
                     "reasons": [
                       "Directs to an unverified, non-bank domain.",
                       "Threatens asset freezing to invoke fear.",
                       "Bypasses standard, secure banking communication channels."
                     ]
                    }"""
                
                elif self.agent_type == "Mentor":
                    if "Evaluate the current session" in message:
                        return '{"score": 75, "alerts": [{"time": "System", "text": "Offline sandbox engaged due to API limits", "type": "warning"}]}'
                    
                    if "Provide a list of recommended actions" in message:
                        return """{
                            "actions": [
                                { "icon": "Ban", "text": "Do not click unknown links", "detail": "Never open URLs from unknown senders" },
                                { "icon": "Phone", "text": "Verify with official source", "detail": "Call the company directly using their official number" }
                            ]
                        }"""
                    return "1. Do NOT click the link.\n2. Contact the institution through official channels.\n3. Delete the message and block the sender."
                
            elif "401" in error_msg or "api key" in error_msg.lower():
                return f"System Alert: Invalid API Key. Please verify your GROQ_API_KEY in .env"
            
            return f"Error communicating with AI: {error_msg[:150]}"
