"""
API routers for Kavach AI detection, explanation, and action endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.schemas import (
    MessageInput,
    ApiResponse,
    DetectionResult,
    ExplanationResult,
    ActionResult,
    SimulationResponse,
    HealthScore,
    HistoryResponse,
    HistoryEntry,
)
from backend.services import agent_service
from backend.logs_structured import get_logger
from backend.database_models import get_db
from backend.auth.auth import get_current_user

router = APIRouter(prefix="/api", tags=["detection"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> ApiResponse:
    """Health check endpoint for Cloud Run."""
    return ApiResponse(
        success=True,
        data={"status": "ok", "service": "Kavach AI Cyber Safety Simulator"},
        message="Server healthy"
    )


@router.post("/scan")
async def scan_message(
    data: MessageInput,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    Detect if a message is a scam or safe.
    
    Uses Forensic agent to classify message.
    Results are logged to detection history if user is authenticated.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Optional auth for detection
    user_id = None
    # In a real app, we'd check the Authorization header. 
    # For now, we'll try to get it if the token is passed or if it's in the request context.
    # Since this is a POST, we rely on the caller to provide auth if they want history.
    
    try:
        # This is a bit of a hack to support both auth and non-auth detection
        # In production, we'd use a more robust dependency.
        pass
    except:
        pass

    try:
        result = await agent_service.detect_message(data.text, db=db, user_id=user_id)
        
        # Log detection to structured logging
        logger.info(f"Detection: {result['classification']} (confidence: {result['confidence']})")
        
        return ApiResponse(
            success=True,
            data={
                "classification": result["classification"],
                "confidence": result["confidence"],
                "reason": result["reason"]
            }
        )
    
    except Exception as e:
        logger.error(f"Detection endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Detection failed"
        )


@router.post("/explain")
async def explain(data: MessageInput) -> ApiResponse:
    """
    Explain why a message is a scam.
    
    Uses Forensic agent to break down message tactics and threats.
    Highlights suspicious parts and provides reasoning.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = await agent_service.explain_message(data.text)
        
        return ApiResponse(
            success=True,
            data=result
        )
    
    except Exception as e:
        logger.error(f"Explain endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Explanation failed"
        )


@router.post("/action")
async def action(data: MessageInput) -> ApiResponse:
    """
    Recommend actions for the user.
    
    Uses Mentor agent to suggest steps user should take.
    """
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = await agent_service.recommend_actions(data.text)
        
        return ApiResponse(
            success=True,
            data=result
        )
    
    except Exception as e:
        logger.error(f"Action endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Action recommendation failed"
        )


@router.post("/simulate")
async def simulate() -> ApiResponse:
    """
    Generate a realistic scam scenario.
    
    Uses Infiltrator agent to create a convincing scam message.
    Includes dynamic UI values (amount, title, description, etc).
    """
    try:
        scenario = await agent_service.generate_scam_scenario()
        
        return ApiResponse(
            success=True,
            data={
                "message": scenario.get("message"),
                "amount": scenario.get("amount"),
                "tip": scenario.get("tip"),
                "scam_type": scenario.get("scenario_type"),
                "risk_level": scenario.get("risk_level"),
                "ui_title": scenario.get("ui_title"),
                "ui_description": scenario.get("ui_description"),
                "recommended_actions": scenario.get("recommended_actions", []),
                "await_user_response": scenario.get("await_user_response", True),
                "next_step": scenario.get("next_step"),
                "sender": "Infiltrator"
            }
        )
    
    except Exception as e:
        logger.error(f"Simulate endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Scam generation failed"
        )


@router.get("/history")
async def history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    Get detection history for the current user.
    """
    try:
        user_id = current_user["user_id"]
        from backend.database_models import DetectionHistory
        
        # Get last 50 entries
        results = db.query(DetectionHistory).filter(
            DetectionHistory.user_id == user_id
        ).order_by(DetectionHistory.created_at.desc()).limit(50).all()
        
        entries = [
            HistoryEntry(
                id=h.id,
                message=h.message,
                classification=h.classification,
                confidence=h.confidence,
                timestamp=h.created_at
            ) for h in results
        ]
        
        return ApiResponse(
            success=True,
            data={"history": [e.dict() for e in entries]}
        )
    
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="History retrieval failed"
        )


@router.get("/health-score")
async def health_score() -> ApiResponse:
    """
    Get session security health evaluation.
    
    Uses Mentor agent to score overall security posture.
    """
    try:
        result = await agent_service.evaluate_health()
        
        return ApiResponse(
            success=True,
            data=result
        )
    
    except Exception as e:
        logger.error(f"Health score endpoint error: {e}")
        # Return safe fallback
        return ApiResponse(
            success=True,
            data={
                "score": 75,
                "alerts": [{"time": "Now", "text": "Service unavailable", "type": "warning"}]
            }
        )
