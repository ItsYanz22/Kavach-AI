"""
Production-grade Pydantic schemas for Kavach AI API responses.
Ensures consistent, validated responses across all endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


# ────────────────────────────────────────────────────────────────────────────
# INPUT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class MessageInput(BaseModel):
    """User message for detection/explanation/action."""
    text: str = Field(..., min_length=1, max_length=5000, description="Message text to analyze")


class WarRoomMessage(BaseModel):
    """User response in WebSocket War Room interaction."""
    message: str = Field(..., min_length=1, description="User message in the conversation")
    session_id: Optional[str] = Field(None, description="Session identifier for state tracking")


# ────────────────────────────────────────────────────────────────────────────
# RESPONSE SCHEMA COMPONENTS (Reusable)
# ────────────────────────────────────────────────────────────────────────────

class ActionRecommendation(BaseModel):
    """A single recommended action for the user."""
    icon: Literal["Ban", "Phone", "Shield", "CheckCircle", "AlertTriangle", "Link", "Clock", "Building"] = "Ban"
    text: str = Field(..., description="Short actionable text")
    detail: str = Field(..., description="Detailed explanation")


class HighlightSegment(BaseModel):
    """A highlighted text segment in the scam message."""
    label: str = Field(..., description="Tactic/threat name (e.g., Suspicious Link)")
    color: Literal["danger", "warning", "cyber"] = "danger"
    icon: Literal["Link", "Clock", "Building", "AlertTriangle", "PhoneOff", "Eye"] = "AlertTriangle"
    tooltip: str = Field(..., description="Why this is suspicious")
    text: str = Field(..., description="The exact text being highlighted")


class MessagePart(BaseModel):
    """A part of the message (highlighted or plain)."""
    text: str = Field(..., description="Text content")
    highlight_index: Optional[int] = Field(None, description="Index into highlights array, null if plain text")


class HealthAlert(BaseModel):
    """An alert in the security health score."""
    time: str = Field(..., description="When the alert occurred (e.g., 'Just now')")
    text: str = Field(..., description="Alert message")
    type: Literal["safe", "warning", "danger"] = "warning"


class RecommendedUserAction(BaseModel):
    """An action option presented to the user in the UI."""
    label: str = Field(..., description="Button label (e.g., '🔗 Open Link')")
    action_id: str = Field(..., description="Action identifier (e.g., 'pay', 'ignore', 'analyze')")
    type: Literal["danger", "warning", "cyber", "safe"] = "warning"


# ────────────────────────────────────────────────────────────────────────────
# API RESPONSE ENVELOPES
# ────────────────────────────────────────────────────────────────────────────

class ApiResponse(BaseModel):
    """Standard API response envelope."""
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Dict[str, Any] = Field(..., description="Response payload")
    message: Optional[str] = Field(None, description="Additional message or error detail")


# ────────────────────────────────────────────────────────────────────────────
# DETECTION ENDPOINT
# ────────────────────────────────────────────────────────────────────────────

class DetectionResult(BaseModel):
    """Classification of a message as SCAM or SAFE."""
    classification: Literal["SCAM", "SAFE"] = Field(..., description="Message classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., description="Why this classification was made")


# ────────────────────────────────────────────────────────────────────────────
# EXPLANATION ENDPOINT
# ────────────────────────────────────────────────────────────────────────────

class ExplanationResult(BaseModel):
    """Detailed breakdown of why a message is a scam."""
    message_parts: List[MessagePart] = Field(..., description="Message segments with highlighting info")
    highlights: List[HighlightSegment] = Field(..., description="Highlighted threats/tactics")
    reasons: List[str] = Field(..., description="Detailed reasons why message is suspicious")


# ────────────────────────────────────────────────────────────────────────────
# ACTION ENDPOINT
# ────────────────────────────────────────────────────────────────────────────

class ActionResult(BaseModel):
    """Recommended user actions to take."""
    actions: List[ActionRecommendation] = Field(..., description="List of recommended actions")


# ────────────────────────────────────────────────────────────────────────────
# SCAM SIMULATION ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

class ScamSimulation(BaseModel):
    """A dynamically generated scam scenario."""
    scenario_type: str = Field(..., description="Type of scam (e.g., 'phishing', 'upi_fraud')")
    message: str = Field(..., description="The simulated scam message")
    risk_level: Literal["low", "medium", "high", "critical"] = "high"
    
    # UI presentation
    ui_title: str = Field(..., description="UI title for the scenario (e.g., '⚠ UPI Phishing')")
    ui_description: str = Field(..., description="Brief UI description")
    
    # User interaction
    recommended_actions: List[RecommendedUserAction] = Field(
        ..., description="Action buttons to present to user"
    )
    
    # Metadata
    await_user_response: bool = Field(
        True, description="Whether to wait for user response before continuing"
    )
    next_step: str = Field(..., description="Next action (e.g., 'wait_for_user')")
    
    # Dynamic values (generated per scenario)
    amount: Optional[float] = Field(None, description="Amount at risk (dynamic per scenario)")
    tip: str = Field(..., description="Helpful tip explaining the scam")


class SimulationResponse(BaseModel):
    """Response from /simulate or /auto-spam endpoints."""
    message: str = Field(..., description="The scam message text")
    amount: Optional[float] = Field(None, description="Amount at risk")
    tip: str = Field(..., description="Security tip")
    scam_type: str = Field(..., description="Type of scam")
    risk_level: Literal["low", "medium", "high", "critical"] = "high"
    ui_title: str = Field(..., description="UI title")
    ui_description: str = Field(..., description="UI description")
    recommended_actions: List[RecommendedUserAction] = Field(..., description="Action options")
    await_user_response: bool = Field(True, description="Wait for user response")
    next_step: str = Field(..., description="Next step in scenario")
    sender: str = Field(..., description="Who generated this (e.g., 'Infiltrator')")


# ────────────────────────────────────────────────────────────────────────────
# WEBSOCKET MESSAGE
# ────────────────────────────────────────────────────────────────────────────

class WebSocketMessage(BaseModel):
    """Message sent over WebSocket (War Room interaction)."""
    sender: Literal["Infiltrator", "User", "System"] = "Infiltrator"
    message: str = Field(..., description="Message text")
    amount: Optional[float] = Field(None, description="Amount at risk")
    tip: Optional[str] = Field(None, description="Security tip")
    scam_type: str = Field(..., description="Type of scam")
    risk_level: Literal["low", "medium", "high", "critical"] = "high"
    ui_title: str = Field(..., description="UI title")
    ui_description: str = Field(..., description="UI description")
    recommended_actions: List[RecommendedUserAction] = Field(..., description="User action options")
    await_user_response: bool = Field(True, description="Expect user response")
    next_step: str = Field(..., description="Next interaction step")


class WebSocketError(BaseModel):
    """Error message sent over WebSocket."""
    error: str = Field(..., description="Error description")
    session_state: Optional[str] = Field(None, description="Current session state for debugging")


# ────────────────────────────────────────────────────────────────────────────
# HEALTH & HISTORY
# ────────────────────────────────────────────────────────────────────────────

class HealthScore(BaseModel):
    """Overall security health evaluation."""
    score: int = Field(..., ge=0, le=100, description="Health score 0-100")
    alerts: List[HealthAlert] = Field(..., description="Recent alerts")


class HistoryEntry(BaseModel):
    """Past detection history entry."""
    id: int = Field(..., description="Entry ID")
    message: str = Field(..., description="Original message")
    classification: str = Field(..., description="SCAM or SAFE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    timestamp: datetime = Field(..., description="When detected")


class HistoryResponse(BaseModel):
    """Response from /history endpoint."""
    history: List[HistoryEntry] = Field(..., description="Detection history")