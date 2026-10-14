import os
import time
import logging
import json
from typing import Optional, List
from groq import Groq
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from backend/.env regardless of cwd
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(_env_path, override=True)

# Import prompts – use relative imports for package structure
from .agent_prompts import INFILTRATOR_PROMPT, FORENSIC_PROMPT, MENTOR_PROMPT

# Configure API Keys securely from environment
api_keys_raw = os.environ.get("GROQ_API_KEYS", os.environ.get("GROQ_API_KEY", ""))
API_KEYS = [k.strip().strip('"').strip("'") for k in api_keys_raw.split(",") if k.strip().strip('"').strip("'")]
CURRENT_KEY_IDX = 0

# Configurable Groq model with smart fallback candidates
CUSTOM_GROQ_MODEL = os.environ.get("GROQ_MODEL")

# Prioritized list of known high-quality Groq chat models
CANDIDATE_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "allam-2-7b",
]

if CUSTOM_GROQ_MODEL and CUSTOM_GROQ_MODEL not in CANDIDATE_MODELS:
    CANDIDATE_MODELS.insert(0, CUSTOM_GROQ_MODEL)

if not API_KEYS:
    logger.warning("⚠️ No GROQ_API_KEY found. Agents will use fallback mode.")


class AgentManager:
    """Wraps a Groq API client with dynamic model discovery, key rotation, and persona management."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.client: Optional[Groq] = None
        self.conversation_history = []
        self.active_model: Optional[str] = None
        self.available_models_on_key: List[str] = []

        if agent_type == "Infiltrator":
            self.system_instruction = INFILTRATOR_PROMPT
            self.default_temperature = 0.8
        elif agent_type == "Forensic":
            self.system_instruction = FORENSIC_PROMPT
            self.default_temperature = 0.2
        elif agent_type == "Mentor":
            self.system_instruction = MENTOR_PROMPT
            self.default_temperature = 0.4
        else:
            self.system_instruction = ""
            self.default_temperature = 0.7

        self._init_client()

    def _init_client(self):
        """Initialize Groq client and dynamically discover available models for this key."""
        global CURRENT_KEY_IDX
        if not API_KEYS:
            self.client = None
            logger.warning(f"[{self.agent_type}] Cannot initialize Groq client: No API keys configured.")
            return

        try:
            current_key = API_KEYS[CURRENT_KEY_IDX]
            self.client = Groq(api_key=current_key, timeout=25.0)
            self.conversation_history = []

            # Discover available models on this specific API key
            try:
                models_data = self.client.models.list().data
                self.available_models_on_key = [m.id for m in models_data]
                logger.info(f"[{self.agent_type}] Discovered {len(self.available_models_on_key)} models on Groq key.")
            except Exception as model_list_err:
                logger.warning(f"[{self.agent_type}] Could not list models from Groq: {model_list_err}")
                self.available_models_on_key = []

            # Select best candidate model
            selected_model = None
            if CUSTOM_GROQ_MODEL and (not self.available_models_on_key or CUSTOM_GROQ_MODEL in self.available_models_on_key):
                selected_model = CUSTOM_GROQ_MODEL
            elif self.available_models_on_key:
                for candidate in CANDIDATE_MODELS:
                    if candidate in self.available_models_on_key:
                        selected_model = candidate
                        break

            if not selected_model:
                selected_model = CANDIDATE_MODELS[0]

            self.active_model = selected_model
            logger.info(f"✅ [{self.agent_type}] Initialized Groq API client with model: {self.active_model}")

        except Exception as e:
            self.client = None
            logger.error(f"❌ Failed to initialise {self.agent_type}: {e}")

    def send_message(
        self,
        message: str,
        temperature: Optional[float] = None,
        max_tokens: int = 1200,
        response_format: Optional[dict] = None,
        retry_count: int = 0
    ) -> str:
        """Send a message to the agent and return its text response with automatic model & key fallback."""
        global CURRENT_KEY_IDX

        if not self.client:
            logger.warning(f"[{self.agent_type}] Client not initialized. Using fallback generator.")
            return self._get_hard_fallback(message)

        temp = temperature if temperature is not None else self.default_temperature
        resp_fmt = response_format if response_format is not None else {"type": "json_object"}

        # Determine model priority order for this attempt
        models_to_try = [self.active_model] if self.active_model else []
        for cand in CANDIDATE_MODELS:
            if cand not in models_to_try:
                if not self.available_models_on_key or cand in self.available_models_on_key:
                    models_to_try.append(cand)

        messages = self.conversation_history.copy()
        payload_messages = [
            {"role": "system", "content": self.system_instruction},
            *messages,
            {"role": "user", "content": message}
        ]

        last_error = None
        start_time = time.time()

        for model_name in models_to_try:
            try:
                logger.info(f"[{self.agent_type}] Requesting completion from Groq model: {model_name} (temp={temp})")
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=payload_messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    response_format=resp_fmt,
                )

                assistant_message = response.choices[0].message.content
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[{self.agent_type}] Groq call succeeded using {model_name} in {duration_ms:.1f}ms")

                # Cache working model as active
                self.active_model = model_name

                # Store in conversation history for multi-turn context
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})

                if len(self.conversation_history) > 16:
                    self.conversation_history = self.conversation_history[-16:]

                return assistant_message

            except Exception as model_err:
                err_str = str(model_err)
                last_error = err_str
                logger.warning(f"[{self.agent_type}] Model {model_name} failed: {err_str[:160]}")

                # Rate limit or quota error -> rotate API key if multiple available
                if "rate_limit" in err_str.lower() or "429" in err_str or "quota" in err_str.lower():
                    if len(API_KEYS) > 1 and retry_count < len(API_KEYS) - 1:
                        logger.info(f"[{self.agent_type}] Rate limit reached. Rotating API key... ({retry_count + 1}/{len(API_KEYS) - 1})")
                        CURRENT_KEY_IDX = (CURRENT_KEY_IDX + 1) % len(API_KEYS)
                        self._init_client()
                        return self.send_message(
                            message,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            response_format=response_format,
                            retry_count=retry_count + 1
                        )

                # Check if it's a model not found / decommissioned error, continue loop to try next model
                if any(x in err_str.lower() for x in ["404", "not found", "decommissioned", "not available", "400"]):
                    continue

                # If another unrecoverable error occurred (e.g. 401 invalid key), rotate or break
                if "401" in err_str or "unauthorized" in err_str.lower() or "invalid api key" in err_str.lower():
                    if len(API_KEYS) > 1 and retry_count < len(API_KEYS) - 1:
                        logger.warning(f"[{self.agent_type}] Invalid API key detected. Rotating to next key...")
                        CURRENT_KEY_IDX = (CURRENT_KEY_IDX + 1) % len(API_KEYS)
                        self._init_client()
                        return self.send_message(
                            message,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            response_format=response_format,
                            retry_count=retry_count + 1
                        )
                    break

        logger.error(f"[{self.agent_type}] All candidate Groq models failed. Last error: {last_error[:200] if last_error else 'unknown'}. Using fallback.")
        return self._get_hard_fallback(message)

    def _get_hard_fallback(self, message: str) -> str:
        """Return a diverse structured fallback response when live Groq calls are unavailable."""
        if self.agent_type == "Infiltrator":
            try:
                from backend.fallback_scenarios import fallback_engine
                scenario = fallback_engine.generate_random_scenario()
                scenario["generation_source"] = "fallback"
                scenario["is_ai_generated"] = False
                return json.dumps(scenario)
            except Exception as e:
                logger.error(f"Fallback engine error: {e}")
                # Emergency basic structure
                return json.dumps({
                    "scenario_type": "upi_fraud",
                    "message": "Payment of ₹4,999 to Flipkart is processing. If not authorized by you, tap to cancel immediately: safesim.link/cancel-upi",
                    "amount": 4999,
                    "tip": "UPI cancel links are often collect requests in disguise. Never enter your PIN to receive or cancel a payment.",
                    "risk_level": "high",
                    "ui_title": "⚠️ Urgent UPI Transaction Alert",
                    "ui_description": "A fraudulent payment alert designed to induce panic and extract approval.",
                    "recommended_actions": [
                        {"label": "🔴 Cancel ₹4,999 Payment", "action_id": "pay", "type": "danger"},
                        {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
                        {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
                        {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
                        {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"}
                    ],
                    "await_user_response": True,
                    "next_step": "wait_for_user",
                    "generation_source": "fallback",
                    "is_ai_generated": False
                })

        elif self.agent_type == "Forensic":
            return json.dumps({
                "classification": "SCAM",
                "confidence": 0.94,
                "reason": "Analyzed message exhibits hallmark social engineering tactics: fabricated urgency, unverified links, and deceptive caller ID.",
                "message_parts": [{"text": message, "highlight_index": 0}],
                "highlights": [{
                    "label": "Urgent Threat",
                    "color": "danger",
                    "icon": "AlertTriangle",
                    "tooltip": "Scammers manufacture artificial urgency to force quick, uncritical action.",
                    "text": message[:60] if len(message) > 60 else message
                }],
                "reasons": [
                    "High pressure or artificial deadline",
                    "Unverified domain link or unfamiliar sender",
                    "Request to act outside official application channels"
                ]
            })

        elif self.agent_type == "Mentor":
            return json.dumps({
                "score": 75,
                "alerts": [
                    {"time": "Just now", "text": "Operating in safety simulation mode", "type": "warning"}
                ],
                "actions": [
                    {"icon": "Ban", "text": "Do not click links", "detail": "Never tap links received in unsolicited messages"},
                    {"icon": "Phone", "text": "Verify officially", "detail": "Reach out directly through official app or verified helpline"}
                ]
            })

        return json.dumps({"status": "unavailable"})
