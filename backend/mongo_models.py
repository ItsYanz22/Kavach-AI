"""
MongoDB models for Kavach AI user sessions and persistence.
Stores user login history, session data, and achievements.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.config import EnvConfig

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


class UserSessionModel(BaseModel):
    """MongoDB model for user login sessions."""
    email: str
    username: str
    user_id: int
    login_time: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_active: bool = True
    
    class Config:
        arbitrary_types_allowed = True


class UserAchievementModel(BaseModel):
    """MongoDB model for user achievements."""
    user_id: int
    email: str
    badge_id: str
    title: str
    description: str
    icon: str
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    points: int = 0
    
    class Config:
        arbitrary_types_allowed = True


class UserProgressModel(BaseModel):
    """MongoDB model for user learning progress."""
    user_id: int
    email: str
    simulations_attempted: int = 0
    simulations_passed: int = 0
    total_scams_detected: int = 0
    security_score: float = 50.0
    total_xp: int = 0
    level: int = 1
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


async def init_mongodb():
    """Initialize MongoDB connection."""
    global client, db
    
    if not EnvConfig.MONGODB_URI:
        return False
    
    try:
        client = AsyncIOMotorClient(EnvConfig.MONGODB_URI)
        db = client[EnvConfig.MONGODB_DATABASE]
        
        # Create collections and indexes
        await db.user_sessions.create_index("email", unique=True, sparse=True)
        await db.user_sessions.create_index("login_time")
        
        await db.user_achievements.create_index("user_id")
        await db.user_achievements.create_index("email")
        await db.user_achievements.create_index("earned_at")
        
        await db.user_progress.create_index("user_id", unique=True)
        await db.user_progress.create_index("email")
        
        # Test connection
        await db.admin.command("ping")
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


async def save_user_session(session_data: UserSessionModel):
    """Save or update user login session."""
    if not db:
        return False
    
    try:
        await db.user_sessions.update_one(
            {"email": session_data.email},
            {
                "$set": session_data.dict(),
                "$inc": {"login_count": 1}
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Error saving session: {e}")
        return False


async def get_user_sessions(email: str) -> List[dict]:
    """Retrieve all login sessions for a user."""
    if not db:
        return []
    
    try:
        sessions = await db.user_sessions.find({"email": email}).to_list(None)
        return sessions
    except Exception as e:
        print(f"❌ Error retrieving sessions: {e}")
        return []


async def save_user_achievement(achievement: UserAchievementModel):
    """Save user achievement."""
    if not db:
        return False
    
    try:
        await db.user_achievements.insert_one(achievement.dict())
        return True
    except Exception as e:
        print(f"❌ Error saving achievement: {e}")
        return False


async def get_user_achievements(user_id: int) -> List[dict]:
    """Retrieve all achievements for a user."""
    if not db:
        return []
    
    try:
        achievements = await db.user_achievements.find(
            {"user_id": user_id}
        ).sort("earned_at", -1).to_list(None)
        return achievements
    except Exception as e:
        print(f"❌ Error retrieving achievements: {e}")
        return []


async def save_user_progress(progress: UserProgressModel):
    """Save or update user progress."""
    if not db:
        return False
    
    try:
        await db.user_progress.update_one(
            {"user_id": progress.user_id},
            {"$set": progress.dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Error saving progress: {e}")
        return False


async def get_user_progress(user_id: int) -> Optional[dict]:
    """Retrieve user progress."""
    if not db:
        return None
    
    try:
        progress = await db.user_progress.find_one({"user_id": user_id})
        return progress
    except Exception as e:
        print(f"❌ Error retrieving progress: {e}")
        return None


async def close_mongodb():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")
