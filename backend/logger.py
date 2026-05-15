"""
Logging utilities for Kavach AI cybersecurity agent system.
Tracks user decisions, detected scams, response times, and agent outputs.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure logging directories exist
LOGS_DIR = Path(__file__).parent / "logs"
ANALYTICS_DIR = Path(__file__).parent / "analytics"
THREAT_HISTORY_DIR = LOGS_DIR / "threat_history"

for directory in [LOGS_DIR, ANALYTICS_DIR, THREAT_HISTORY_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("kavach_ai")


def log_detection(
    user_input: str,
    classification: str,
    confidence: float,
    agent: str = "Forensic",
    additional_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log threat detection event.
    
    Args:
        user_input: The message analyzed
        classification: SCAM or SAFE classification
        confidence: Confidence score (0-1)
        agent: Which agent made the detection
        additional_data: Extra metadata
    """
    detection_event = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "user_input": user_input[:500],  # Limit to 500 chars
        "classification": classification,
        "confidence": confidence,
        "metadata": additional_data or {}
    }
    
    # Log to threat history
    threat_file = THREAT_HISTORY_DIR / f"threats_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
    with open(threat_file, "a") as f:
        f.write(json.dumps(detection_event) + "\n")
    
    logger.info(f"Detection: {classification} (confidence: {confidence:.2f})")


def log_user_decision(
    threat_id: str,
    user_action: str,
    agent_recommendation: str,
    user_choice: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user decision vs agent recommendation (for training data).
    
    Args:
        threat_id: Unique threat identifier
        agent_recommendation: What agent recommended
        user_choice: What user actually did
        metadata: Extra context
    """
    decision_event = {
        "timestamp": datetime.utcnow().isoformat(),
        "threat_id": threat_id,
        "user_action": user_action,
        "agent_recommendation": agent_recommendation,
        "user_choice": user_choice,
        "metadata": metadata or {}
    }
    
    decision_file = ANALYTICS_DIR / f"decisions_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
    with open(decision_file, "a") as f:
        f.write(json.dumps(decision_event) + "\n")
    
    logger.info(f"User decision logged: {user_action} -> {user_choice}")


def log_agent_output(
    agent_name: str,
    prompt: str,
    response: str,
    response_time_ms: float,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log individual agent outputs and response times.
    Useful for performance monitoring and training data generation.
    
    Args:
        agent_name: Name of agent (e.g., "Infiltrator", "Forensic", "Mentor")
        prompt: Input prompt to agent
        response: Agent's response
        response_time_ms: Response time in milliseconds
        metadata: Extra metadata
    """
    agent_event = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "prompt": prompt[:500],
        "response": response[:1000],
        "response_time_ms": response_time_ms,
        "metadata": metadata or {}
    }
    
    agent_file = ANALYTICS_DIR / f"agent_outputs_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
    with open(agent_file, "a") as f:
        f.write(json.dumps(agent_event) + "\n")
    
    logger.info(f"Agent {agent_name} output logged (response time: {response_time_ms:.2f}ms)")


def get_analytics_summary(days: int = 7) -> Dict[str, Any]:
    """
    Get analytics summary for specified number of days.
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Summary statistics
    """
    total_detections = 0
    scam_count = 0
    safe_count = 0
    avg_confidence = 0.0
    
    threat_files = sorted(THREAT_HISTORY_DIR.glob("threats_*.jsonl"))
    
    for threat_file in threat_files[-days:]:
        try:
            with open(threat_file, "r") as f:
                for line in f:
                    event = json.loads(line)
                    total_detections += 1
                    if event["classification"].upper() == "SCAM":
                        scam_count += 1
                    else:
                        safe_count += 1
                    avg_confidence += event["confidence"]
        except Exception as e:
            logger.error(f"Error reading {threat_file}: {e}")
    
    if total_detections > 0:
        avg_confidence /= total_detections
    
    return {
        "total_detections": total_detections,
        "scam_count": scam_count,
        "safe_count": safe_count,
        "average_confidence": round(avg_confidence, 3),
        "scam_percentage": round((scam_count / total_detections * 100), 2) if total_detections > 0 else 0
    }


if __name__ == "__main__":
    # Test logging
    log_detection("Test message", "SCAM", 0.95)
    log_user_decision("threat_001", "flag", "ignore", "flag")
    log_agent_output("Forensic", "Analyze this", "Response", 150.5)
    
    print("\nAnalytics Summary:")
    print(json.dumps(get_analytics_summary(days=1), indent=2))
