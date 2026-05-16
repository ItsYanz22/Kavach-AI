"""
Learning platform endpoints for Kavach AI.
Manages modules, progress, simulations, and achievements.
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database_models import (
    get_db, User, LearningModule, UserProgress, SimulationHistory,
    Achievement, ScamCategory, SimulationResult, UserLevel
)
from backend.schemas import ApiResponse
from backend.auth.auth import get_current_user
from backend.fallback_scenarios import fallback_engine
from backend.logs_structured import log_database_event
from backend.services import agent_service

router = APIRouter(prefix="/api/learning", tags=["learning"])


# ────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class ModuleResponse(BaseModel):
    """Learning module response."""
    id: str
    category: str
    title: str
    description: str
    difficulty: str
    estimated_duration_minutes: int
    xp_reward: int
    
    class Config:
        from_attributes = True


class ModuleDetailResponse(ModuleResponse):
    """Detailed module response with content."""
    content: str


class ProgressResponse(BaseModel):
    """User progress response."""
    module_id: str
    is_completed: bool
    completion_percentage: float
    quiz_score: Optional[float]
    times_attempted: int
    last_accessed: datetime


class SimulationRequest(BaseModel):
    """Start a simulation scenario."""
    scenario_type: Optional[str] = None  # If None, random


class SimulationResponse(BaseModel):
    """Simulation scenario response."""
    scenario_id: str
    scenario_type: str
    message: str
    amount: int
    tip: str
    risk_level: str
    ui_title: str
    ui_description: str
    recommended_actions: List[dict]


class SimulationSubmitRequest(BaseModel):
    """Submit simulation response."""
    scenario_id: str
    choice: str = Field(..., description="pay, ignore, analyze, block, or report")
    reasoning: Optional[str] = None


class ExplainRequest(BaseModel):
    """Request analysis for a message."""
    message: str


class AchievementResponse(BaseModel):
    """Achievement/badge response."""
    badge_id: str
    title: str
    description: str
    icon: str
    earned_at: datetime


class DashboardResponse(BaseModel):
    """User dashboard summary."""
    user_name: str
    level: str
    xp: int
    total_xp: int
    security_score: float
    streak_days: int
    
    # Stats
    simulations_attempted: int
    simulations_passed: int
    scams_detected: int
    accuracy_percentage: float
    
    # Progress
    modules_completed: int
    modules_total: int
    current_streak_xp: int
    achievements_earned: int


# ────────────────────────────────────────────────────────────────────────────
# LEARNING MODULES
# ────────────────────────────────────────────────────────────────────────────

@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List available learning modules.
    
    - **category**: Filter by scam category
    - **difficulty**: Filter by difficulty level
    """
    query = db.query(LearningModule).filter(LearningModule.is_published == True)
    
    if category:
        query = query.filter(LearningModule.category == category)
    
    if difficulty:
        query = query.filter(LearningModule.difficulty == difficulty)
    
    modules = query.all()
    
    return [ModuleResponse.from_orm(m) for m in modules]


@router.get("/modules/{module_id}", response_model=ModuleDetailResponse)
async def get_module(
    module_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed module information."""
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    
    if not module or not module.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return ModuleDetailResponse.from_orm(module)


@router.get("/progress", response_model=List[ProgressResponse])
async def get_user_progress(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress on all modules."""
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == current_user["user_id"]
    ).all()
    
    return [ProgressResponse.from_orm(p) for p in progress_records]


@router.post("/modules/{module_id}/start")
async def start_module(
    module_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start or resume a learning module."""
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    
    if not module or not module.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Find or create progress record
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user["user_id"],
        UserProgress.module_id == module_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            id=str(uuid.uuid4()),
            user_id=current_user["user_id"],
            module_id=module_id,
            started_at=datetime.utcnow(),
        )
        db.add(progress)
    
    progress.times_attempted += 1
    progress.last_accessed = datetime.utcnow()
    db.commit()
    
    log_database_event("module_started", "user_progress", user_id=current_user["user_id"], module_id=module_id)
    
    return {
        "status": "ok",
        "module_id": module_id,
        "progress": progress.completion_percentage
    }


# ────────────────────────────────────────────────────────────────────────────
# SIMULATIONS
# ────────────────────────────────────────────────────────────────────────────

@router.post("/simulate", response_model=SimulationResponse)
async def start_simulation(
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new scam simulation.
    
    - **scenario_type**: Optional specific type to simulate (phishing, investment, etc.)
    
    Returns a scenario to respond to.
    """
    # Generate scenario
    if request.scenario_type:
        scenario = fallback_engine.generate_scenario_by_type(request.scenario_type)
    else:
        scenario = fallback_engine.generate_random_scenario()
    
    scenario_id = str(uuid.uuid4())
    
    log_database_event(
        "simulation_started",
        "simulation_history",
        user_id=current_user["user_id"],
        scenario_type=scenario.get("scenario_type")
    )
    
    return SimulationResponse(
        scenario_id=scenario_id,
        scenario_type=scenario.get("scenario_type", "unknown"),
        message=scenario.get("message", ""),
        amount=scenario.get("amount", 0),
        tip=scenario.get("tip", ""),
        risk_level=scenario.get("risk_level", "medium"),
        ui_title=scenario.get("ui_title", "Scam Alert"),
        ui_description=scenario.get("ui_description", ""),
        recommended_actions=scenario.get("recommended_actions", []),
    )


@router.post("/simulate/submit")
async def submit_simulation_response(
    request: SimulationSubmitRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit user response to a simulation.
    
    - **scenario_id**: The scenario ID from start_simulation
    - **choice**: User's choice (pay, ignore, analyze)
    - **reasoning**: Optional explanation of their choice
    """
    if request.choice not in ["pay", "ignore", "analyze", "block", "report"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid choice - must be 'pay', 'ignore', 'analyze', 'block', or 'report'"
        )
    
    # Determine if correct
    # "ignore" is always correct for scams
    # "analyze" shows good caution
    # "pay" is always wrong
    
    is_correct = request.choice in ["ignore", "analyze", "block", "report"]
    result_type = SimulationResult.CORRECT if is_correct else SimulationResult.INCORRECT
    
    # Dynamic XP reward
    xp_map = {
        "block": 100,
        "report": 75,
        "ignore": 50,
        "analyze": 25,
        "pay": 0
    }
    xp_earned = xp_map.get(request.choice, 10)
    
    # Create history record
    history = SimulationHistory(
        id=str(uuid.uuid4()),
        user_id=current_user["user_id"],
        scenario_type="unknown",
        scenario_message="",
        user_choice=request.choice,
        user_reasoning=request.reasoning,
        is_correct=is_correct,
        result=result_type,
        xp_earned=xp_earned,
    )
    
    db.add(history)
    
    # Update user stats
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if user:
        user.simulations_attempted += 1
        if is_correct:
            user.simulations_passed += 1
        if request.choice == "analyze":
            user.total_scams_detected += 1
        else:
            user.total_mistakes += 1
        
        # Update XP
        user.xp += xp_earned
        user.total_xp += xp_earned
        
        # Update security score (0-100)
        total_sims = user.simulations_attempted
        if total_sims > 0:
            accuracy = (user.simulations_passed / total_sims) * 100
            user.security_score = min(100.0, accuracy)
    
    db.commit()
    
    log_database_event(
        "simulation_submitted",
        "simulation_history",
        user_id=current_user["user_id"],
        is_correct=is_correct,
        xp_earned=xp_earned
    )
    
    return ApiResponse(
        success=True,
        data={
            "is_correct": is_correct,
            "xp_earned": xp_earned,
            "message": f"Great choice! Action: {request.choice.upper()}" if is_correct else "That was a scam!",
        }
    )


@router.post("/simulate/explain")
async def explain_simulation_message(
    request: ExplainRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get forensic analysis for a specific message.
    Used by the 'Analyse Message' button in War Room.
    """
    analysis = await agent_service.explain_message(request.message)
    return ApiResponse(
        success=True,
        data=analysis
    )


# ────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ────────────────────────────────────────────────────────────────────────────

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's earned achievements."""
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user["user_id"]
    ).all()
    
    return [AchievementResponse.from_orm(a) for a in achievements]


# ────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's learning dashboard."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate stats
    modules_completed = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.is_completed == True
    ).count()
    
    modules_total = db.query(LearningModule).filter(
        LearningModule.is_published == True
    ).count()
    
    achievements_earned = db.query(Achievement).filter(
        Achievement.user_id == user.id
    ).count()
    
    accuracy = (user.simulations_passed / user.simulations_attempted * 100) if user.simulations_attempted > 0 else 0
    
    return DashboardResponse(
        user_name=user.name,
        level=user.level,
        xp=user.xp,
        total_xp=user.total_xp,
        security_score=user.security_score,
        streak_days=user.streak_days,
        simulations_attempted=user.simulations_attempted,
        simulations_passed=user.simulations_passed,
        scams_detected=user.total_scams_detected,
        accuracy_percentage=accuracy,
        modules_completed=modules_completed,
        modules_total=modules_total,
        current_streak_xp=user.xp,
        achievements_earned=achievements_earned,
    )
