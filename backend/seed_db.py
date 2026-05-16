import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database_models import User, LearningModule, SessionLocal, Base, engine

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if modules already exist
        if db.query(LearningModule).count() > 0:
            print("Database already seeded.")
            return

        modules = [
            LearningModule(
                id="phishing-101",
                category="Email Safety",
                title="Phishing 101: Spot the Hook",
                description="Learn the psychological triggers scammers use to steal your data.",
                difficulty="beginner",
                estimated_duration_minutes=15,
                xp_reward=100
            ),
            LearningModule(
                id="upi-safety",
                category="Financial Security",
                title="UPI & Digital Payment Safety",
                description="Never enter your PIN to 'receive' money. Learn how UPI scams work.",
                difficulty="beginner",
                estimated_duration_minutes=10,
                xp_reward=150
            ),
            LearningModule(
                id="social-engineering",
                category="Psychology",
                title="The Art of Social Engineering",
                description="Advanced tactics used by hackers to manipulate people into giving up secrets.",
                difficulty="intermediate",
                estimated_duration_minutes=25,
                xp_reward=250
            ),
            LearningModule(
                id="password-hygiene",
                category="Basic Hygiene",
                title="Fortress Passwords",
                description="How to create uncrackable passwords and the importance of 2FA.",
                difficulty="beginner",
                estimated_duration_minutes=12,
                xp_reward=120
            ),
            LearningModule(
                id="forensics-intro",
                category="Technical",
                title="Digital Forensics Introduction",
                description="Analyzing headers and metadata to trace the origin of a threat.",
                difficulty="advanced",
                estimated_duration_minutes=45,
                xp_reward=500
            )
        ]

        for m in modules:
            db.add(m)
        
        db.commit()
        print("Successfully seeded Learning Modules!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
