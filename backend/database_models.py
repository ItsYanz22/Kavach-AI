"""
Database models for Kavach AI - Users and Learning System.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

from backend.config import EnvConfig

# Database setup
engine = create_engine(
    EnvConfig.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in EnvConfig.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ────────────────────────────────────────────────────────────────────────────
# ENUMS
# ────────────────────────────────────────────────────────────────────────────

class UserLevel(str, enum.Enum):
    """User cybersecurity level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ScamCategory(str, enum.Enum):
    """Scam categories for learning modules."""
    PHISHING = "phishing"
    INVESTMENT = "investment"
    DELIVERY = "delivery"
    UTILITY = "utility"
    OTP = "otp"
    JOB = "job"
    ROMANCE = "romance"
    LOAN = "loan"
    DEEPFAKE = "deepfake"


class SimulationResult(str, enum.Enum):
    """Outcome of a simulation."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


# ────────────────────────────────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────────────────────────────────

class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Profile
    level = Column(Enum(UserLevel), default=UserLevel.BEGINNER)
    xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    security_score = Column(Float, default=0.0)  # 0-100
    
    # Stats
    simulations_attempted = Column(Integer, default=0)
    simulations_passed = Column(Integer, default=0)
    total_scams_detected = Column(Integer, default=0)
    total_mistakes = Column(Integer, default=0)
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("SimulationHistory", back_populates="user", cascade="all, delete-orphan")
    detections = relationship("DetectionHistory", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class LearningModule(Base):
    """Learning module/course."""
    __tablename__ = "learning_modules"
    
    id = Column(String(36), primary_key=True, index=True)
    category = Column(Enum(ScamCategory), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)  # Markdown or HTML
    
    # Metadata
    difficulty = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    estimated_duration_minutes = Column(Integer, default=15)
    xp_reward = Column(Integer, default=100)
    
    # Status
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="module")
    
    def __repr__(self):
        return f"<LearningModule {self.title}>"


class UserProgress(Base):
    """Track user progress through learning modules."""
    __tablename__ = "user_progress"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(String(36), ForeignKey("learning_modules.id"), nullable=False, index=True)
    
    # Progress
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)  # 0-100
    quiz_score = Column(Float, nullable=True)  # 0-100
    times_attempted = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("LearningModule", back_populates="progress")
    
    def __repr__(self):
        return f"<UserProgress {self.user_id} -> {self.module_id}>"


class SimulationHistory(Base):
    """Track simulation attempts and outcomes."""
    __tablename__ = "simulation_history"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Simulation details
    scenario_type = Column(String(100), nullable=False)
    scenario_message = Column(Text, nullable=False)
    
    # User response
    user_choice = Column(String(100), nullable=False)  # pay, ignore, analyze
    user_reasoning = Column(Text, nullable=True)
    
    # Result
    is_correct = Column(Boolean, nullable=False)
    result = Column(Enum(SimulationResult), nullable=False)
    xp_earned = Column(Integer, default=0)
    
    # Timing
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="simulations")
    
    def __repr__(self):
        return f"<SimulationHistory {self.id}>"


class Achievement(Base):
    """User achievements and badges."""
    __tablename__ = "achievements"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Achievement details
    badge_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(255))  # emoji or icon URL
    
    # When earned
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    
    def __repr__(self):
        return f"<Achievement {self.title}>"


class DetectionHistory(Base):
    """Persistent log of all message detections."""
    __tablename__ = "detection_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    classification = Column(String(50), nullable=False)
    confidence = Column(Float, default=0.0)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="detections")
    
    def __repr__(self):
        return f"<DetectionHistory {self.id} | {self.classification}>"


# ────────────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ────────────────────────────────────────────────────────────────────────────

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    from backend.logs_structured import log_database_event
    log_database_event("initialized", "all")


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
