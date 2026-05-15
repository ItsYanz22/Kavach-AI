import re
import random

def detect_logic(text: str):
    text_lower = text.lower()

    score = 0
    reasons = []

    # Rule-based dynamic checks (NOT static dataset)
    if "urgent" in text_lower or "immediately" in text_lower:
        score += 30
        reasons.append("Contains urgency language")

    if "otp" in text_lower:
        score += 40
        reasons.append("Asks for OTP")

    if "click" in text_lower or "link" in text_lower:
        score += 20
        reasons.append("Contains suspicious link request")

    if re.search(r"http[s]?://", text_lower):
        score += 30
        reasons.append("Contains URL")

    if "bank" in text_lower or "account" in text_lower:
        score += 20
        reasons.append("Impersonation of financial entity")

    # Dynamic classification
    if score >= 70:
        classification = "SCAM"
    elif score >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "SAFE"

    confidence = min(score, 100)

    reason = ", ".join(reasons) if reasons else "No major threat detected"

    return classification, confidence, reason


def explain_logic(text: str):
    indicators = []

    if "urgent" in text.lower():
        indicators.append({"type": "urgency", "reason": "Creates panic"})

    if "otp" in text.lower():
        indicators.append({"type": "sensitive_info", "reason": "Requests OTP"})

    if "http" in text.lower():
        indicators.append({"type": "link", "reason": "May contain phishing URL"})

    return indicators


def action_logic(classification: str):
    if classification == "SCAM":
        return [
            "Do not click any links",
            "Block the sender",
            "Report to cybercrime 1930"
        ]
    elif classification == "SUSPICIOUS":
        return [
            "Verify sender identity",
            "Avoid sharing personal info"
        ]
    else:
        return ["No action needed"]


def simulate_logic():
    templates = [
        "URGENT: Your bank account will be blocked! Click here: http://fake-link.com",
        "Your OTP is required to complete transaction. Share immediately.",
        "Congratulations! You won a prize. Click link to claim.",
        "Electricity bill unpaid. Pay now to avoid disconnection."
    ]

    return random.choice(templates)