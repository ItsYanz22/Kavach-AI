"""
Production utilities for Kavach AI backend.
Handles:
- Safe JSON parsing from LLM outputs
- Dynamic UI generation
- Prompt formatting
- Error recovery
"""

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
import random

# Production logging
logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────────
# LLM OUTPUT PARSING
# ────────────────────────────────────────────────────────────────────────────

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extract JSON object from LLM response.
    
    LLMs often wrap JSON in markdown code blocks or add extra text.
    This function robustly extracts the first valid JSON object.
    
    Args:
        text: Raw LLM response
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Remove markdown code block wrappers if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    # Try to find JSON object using curly braces
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        logger.warning("No JSON object found in LLM output")
        return None
    
    json_str = text[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e} | Input: {json_str[:100]}...")
        return None


def safe_get(data: Dict, *keys: str, default: Any = None) -> Any:
    """
    Safely get nested values from dict with fallback.
    
    Args:
        data: Dictionary to query
        keys: Nested keys to traverse
        default: Value if key not found
        
    Returns:
        Value or default
        
    Example:
        safe_get(response, "data", "amount", default=2500)
    """
    if not isinstance(data, dict):
        return default
    
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    
    return current if current is not None else default


# ────────────────────────────────────────────────────────────────────────────
# DYNAMIC UI GENERATION
# ────────────────────────────────────────────────────────────────────────────

# Realistic, context-aware values for scam amounts (in Indian Rupees)
SCAM_AMOUNTS = {
    "upi_fraud": [500, 1000, 2500, 5000, 10000],
    "otp_phishing": [1000, 5000, 10000, 25000],
    "digital_arrest": [10000, 50000, 100000],
    "fake_lottery": [5000, 10000, 50000, 100000, 500000],
    "parcel_delivery": [500, 1000, 2000, 5000],
    "electricity_scam": [1000, 2000, 5000],
    "insurance_claim": [5000, 10000, 25000],
    "crypto_investment": [10000, 50000, 100000],
    "job_offer": [1000, 5000, 10000],
    "bank_phishing": [5000, 10000, 25000, 50000],
}

# Context-aware tips for each scam type
SCAM_TIPS = {
    "upi_fraud": "Never share your UPI PIN or OTP with anyone, even if they claim to be from your bank.",
    "otp_phishing": "Banks never ask for OTPs via phone/email. Always dial the official number on your card.",
    "digital_arrest": "Government agencies never threaten arrest over phone. This is a classic scam.",
    "fake_lottery": "You cannot win a lottery you never entered. Delete such messages immediately.",
    "parcel_delivery": "Verify package status directly on the courier's official app/website.",
    "electricity_scam": "Utilities never threaten immediate disconnection via SMS. Always verify on official portals.",
    "insurance_claim": "Contact your insurance company directly from their official website, never via email links.",
    "crypto_investment": "No legitimate investment guarantees 100% returns. Be extremely cautious.",
    "job_offer": "Legitimate companies conduct proper interviews. Never pay upfront for job opportunities.",
    "bank_phishing": "Your bank will never ask for personal information via email/SMS. Always verify by calling.",
}

# UI titles for scam types
SCAM_UI_TITLES = {
    "upi_fraud": "⚠️ UPI Payment Fraud Attempt",
    "otp_phishing": "🔐 OTP/Banking Credential Theft",
    "digital_arrest": "⚖️ Fake Government Threat",
    "fake_lottery": "🎰 Lottery/Prize Scam",
    "parcel_delivery": "📦 Fake Delivery Notice",
    "electricity_scam": "⚡ Utility Bill Scam",
    "insurance_claim": "🛡️ Insurance Fraud",
    "crypto_investment": "💰 Cryptocurrency Investment Scam",
    "job_offer": "💼 Fake Job Offer",
    "bank_phishing": "🏦 Bank Phishing Attack",
}


def infer_scam_type_from_message(message: str) -> str:
    """
    Infer scam type from message content.
    
    Uses keyword matching as a fallback when LLM categorization fails.
    """
    message_lower = message.lower()
    
    keywords = {
        "upi_fraud": ["upi", "payment", "transfer", "wallet"],
        "otp_phishing": ["otp", "verify", "confirm", "login", "password"],
        "digital_arrest": ["arrest", "police", "fir", "case", "court"],
        "fake_lottery": ["lottery", "prize", "winning", "congratulations"],
        "parcel_delivery": ["parcel", "package", "delivery", "shipment"],
        "electricity_scam": ["electricity", "power", "disconnection", "bill"],
        "insurance_claim": ["insurance", "claim", "policy", "benefit"],
        "crypto_investment": ["bitcoin", "crypto", "investment", "returns"],
        "job_offer": ["job", "position", "hiring", "salary"],
        "bank_phishing": ["bank", "account", "balance", "login"],
    }
    
    for scam_type, keywords_list in keywords.items():
        if any(kw in message_lower for kw in keywords_list):
            return scam_type
    
    return "unknown_scam"  # Fallback


def generate_dynamic_amount(scam_type: str) -> float:
    """Generate realistic, random amount based on scam type."""
    amounts = SCAM_AMOUNTS.get(scam_type, [1000, 5000, 10000])
    return float(random.choice(amounts))


def generate_dynamic_tip(scam_type: str) -> str:
    """Get context-aware security tip for scam type."""
    tip = SCAM_TIPS.get(scam_type)
    if tip:
        return tip
    
    # Generic fallback if scam type unknown
    generic_tips = [
        "Never share personal information with unknown sources.",
        "Always verify through official channels before taking action.",
        "If something sounds too good to be true, it probably is.",
        "Be cautious of urgent requests for money or personal data.",
        "Verify phone numbers and websites directly from official sources.",
    ]
    return random.choice(generic_tips)


def generate_dynamic_ui_title(scam_type: str) -> str:
    """Get UI title for scam type."""
    title = SCAM_UI_TITLES.get(scam_type)
    return title or f"⚠️ {scam_type.replace('_', ' ').title()} Scam"


def generate_dynamic_ui_description(scam_type: str, message: str) -> str:
    """Generate context-aware UI description."""
    descriptions = {
        "upi_fraud": f"A suspicious payment request was detected. Amount: ₹{int(generate_dynamic_amount(scam_type))}",
        "otp_phishing": "Someone is trying to steal your banking credentials or OTP.",
        "digital_arrest": "A threatening fake government message was received.",
        "fake_lottery": "You've been offered a prize you never entered to win.",
        "parcel_delivery": "A fake courier notification arrived in your messages.",
        "electricity_scam": "A fake utility bill payment demand was received.",
        "insurance_claim": "A fraudulent insurance claim notification arrived.",
        "crypto_investment": "An unrealistic investment opportunity was offered.",
        "job_offer": "A suspicious job offer with questionable terms arrived.",
        "bank_phishing": "A message impersonating your bank arrived.",
    }
    
    desc = descriptions.get(scam_type)
    if desc:
        return desc
    
    # Generic fallback
    return f"A suspicious message ({scam_type.replace('_', ' ')}) was detected in your messages."


def generate_dynamic_actions(scam_type: str, message: str) -> list:
    """
    Generate context-aware recommended actions.
    
    Returns list of action dicts with icon, label, and type.
    """
    base_actions = [
        {
            "label": "🛑 Ignore & Report",
            "action_id": "ignore",
            "type": "warning"
        },
        {
            "label": "🔍 Inspect URL",
            "action_id": "analyze",
            "type": "cyber"
        },
        {
            "label": "⚠️ Mark as Spam",
            "action_id": "spam",
            "type": "danger"
        },
    ]
    
    # Type-specific primary action
    if "link" in message.lower() or "click" in message.lower():
        base_actions.insert(0, {
            "label": "🔗 Hover to See URL",
            "action_id": "hover",
            "type": "cyber"
        })
    
    if "otp" in message.lower() or "password" in message.lower():
        base_actions.insert(0, {
            "label": "🔐 Do Not Share Credentials",
            "action_id": "warn",
            "type": "danger"
        })
    
    return base_actions


# ────────────────────────────────────────────────────────────────────────────
# PROMPT FORMATTING
# ────────────────────────────────────────────────────────────────────────────

def get_json_schema_prompt(schema_dict: Dict[str, Any]) -> str:
    """
    Format a JSON schema into a clear prompt instruction.
    
    Args:
        schema_dict: Example JSON structure
        
    Returns:
        Formatted prompt instruction
    """
    import json
    schema_str = json.dumps(schema_dict, indent=2)
    return (
        "Return ONLY a valid JSON object matching this schema exactly, "
        "NO markdown formatting, NO backticks, NO extra text:\n"
        f"{schema_str}"
    )


# ────────────────────────────────────────────────────────────────────────────
# LOGGING & ERROR RECOVERY
# ────────────────────────────────────────────────────────────────────────────

def log_llm_error(endpoint: str, error: Exception, context: str = ""):
    """Log LLM processing errors in structured format."""
    logger.error(
        f"LLM processing error in {endpoint}",
        extra={
            "endpoint": endpoint,
            "error_type": type(error).__name__,
            "error_msg": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def create_fallback_scam_scenario(message: str) -> Dict[str, Any]:
    """
    Create a reasonable fallback scenario when LLM fails.
    
    This ensures the system degrades gracefully.
    """
    scam_type = infer_scam_type_from_message(message)
    amount = generate_dynamic_amount(scam_type)
    
    return {
        "scenario_type": scam_type,
        "message": message,
        "risk_level": "high",
        "ui_title": generate_dynamic_ui_title(scam_type),
        "ui_description": generate_dynamic_ui_description(scam_type, message),
        "recommended_actions": [
            {"label": "🔴 Pay & Verify", "action_id": "pay", "type": "danger"},
            {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
            {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
            {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
            {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
        ],
        "await_user_response": True,
        "next_step": "wait_for_user",
        "amount": amount,
        "tip": generate_dynamic_tip(scam_type),
    }


def create_fallback_health_score() -> Dict[str, Any]:
    """Create fallback health score when evaluation fails."""
    return {
        "score": 75,
        "alerts": [
            {
                "time": "Now",
                "text": "Mentor service temporarily unavailable",
                "type": "warning"
            }
        ]
    }
