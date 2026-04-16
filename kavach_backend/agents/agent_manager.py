import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load from the kavach_backend/.env regardless of cwd
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(_env_path, override=True)

# Import prompts – works when running from kavach_backend/ directory
from agents.agent_prompts import INFILTRATOR_PROMPT, FORENSIC_PROMPT, MENTOR_PROMPT

# Temporarily remove GCP ADC to prevent scope/ALTS errors in local dev
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Configure API Key securely from environment
api_key = os.environ.get("GEMINI_API_KEY", "").strip('"').strip("'").strip()
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️  Warning: No GEMINI_API_KEY found. Agents will return fallback messages.")


class AgentManager:
    """Wraps a Google Gemini chat model with a specific agent persona."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type

        system_instruction = ""
        if agent_type == "Infiltrator":
            system_instruction = INFILTRATOR_PROMPT
        elif agent_type == "Forensic":
            system_instruction = FORENSIC_PROMPT
        elif agent_type == "Mentor":
            system_instruction = MENTOR_PROMPT

        try:
            # Auto-detect a working model
            available_models = [
                m.name
                for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]

            # Prefer flash → pro → first available
            model_name = "gemini-1.5-flash"
            if "models/gemini-1.5-flash" in available_models:
                model_name = "models/gemini-1.5-flash"
            elif "models/gemini-1.5-flash-latest" in available_models:
                model_name = "models/gemini-1.5-flash-latest"
            elif "models/gemini-pro" in available_models:
                model_name = "models/gemini-pro"
            elif available_models:
                model_name = available_models[0]

            self.model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
            )
            self.chat = self.model.start_chat(history=[])
            print(f"[OK] {agent_type} agent initialised with {model_name}")

        except Exception as e:
            self.model = None
            self.chat = None
            print(f"[ERROR] Failed to initialise {agent_type}: {e}")

    def send_message(self, message: str) -> str:
        """Send a message to the agent and return its text response."""
        if not self.chat:
            return (
                "Agent unavailable – API key missing or invalid configuration. "
                "Please check your .env file."
            )
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            error_msg = str(e).replace('"', "'")
            print(f"\n[CRITICAL] Gemini AI Error:\n{error_msg}\n")
            if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                 print("[INFO] Activating Fallback Offline Sandbox Mode")
                 if self.agent_type == "Infiltrator":
                     return '{"text": "URGENT: Your bank account is compromised. Submit KYC verification below within 24 hours to prevent asset freeze. http://verify-kyc-now.site/login", "amount": 49999, "tip": "Institutions will never send unverified HTTP links threatening asset freeze.", "scam_type": "KYC Phishing Target"}'
                 
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
                     return "1. Do NOT click the link.\n2. Contact the institution through official channels.\n3. Delete the message and block the sender."
                     
            elif "400" in error_msg or "API key not valid" in error_msg:
                 return f"System Alert: Invalid API Key. Please verify your GEMINI_API_KEY in .env"
            return f"Error communicating with AI: {error_msg[:150]}"
