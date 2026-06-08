"""
Production configuration for Kavach AI.
Centralizes all environment settings with validation.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load from .env regardless of cwd
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)
    logger.info(f"✅ Loaded .env from {_env_path}")
else:
    logger.warning(f"⚠️  .env not found at {_env_path} - using environment variables only")


class EnvConfig:
    """Environment configuration with validation and logging."""
    
    # API Keys
    GROQ_API_KEYS: list = []
    GROQ_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./kavach.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MONGODB_URI: Optional[str] = None
    MONGODB_DATABASE: str = "kavach_ai"
    
    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # Server
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = False
    ENVIRONMENT: str = "local"
    
    # Cloud Run
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_SESSION_TIMEOUT: int = 1800  # 30 minutes
    
    # AI
    AI_REQUEST_TIMEOUT: int = 30  # seconds
    AI_FALLBACK_ENABLED: bool = True
    
    @classmethod
    def load(cls):
        """Load and validate all environment variables."""
        logger.info("=" * 80)
        logger.info("🔧 ENVIRONMENT CONFIGURATION")
        logger.info("=" * 80)
        
        # GROQ API Keys
        groq_keys_raw = os.environ.get("GROQ_API_KEYS", os.environ.get("GROQ_API_KEY", ""))
        cls.GROQ_API_KEYS = [k.strip().strip('"').strip("'") for k in groq_keys_raw.split(",") if k.strip()]
        cls.GROQ_API_KEY = cls.GROQ_API_KEYS[0] if cls.GROQ_API_KEYS else None
        
        if cls.GROQ_API_KEY:
            masked_key = cls.GROQ_API_KEY[:8] + "..." + cls.GROQ_API_KEY[-4:] if len(cls.GROQ_API_KEY) > 12 else "***"
            logger.info(f"✅ GROQ_API_KEY loaded: {masked_key}")
            logger.info(f"✅ Total GROQ keys available: {len(cls.GROQ_API_KEYS)}")
        else:
            logger.warning("⚠️  GROQ_API_KEY not set - AI agents will use fallback mode")
        
        # Database
        cls.DATABASE_URL = os.environ.get("DATABASE_URL", cls.DATABASE_URL)
        logger.info(f"📊 DATABASE_URL: {cls.DATABASE_URL}")
        
        # MongoDB
        cls.MONGODB_URI = os.environ.get("MONGODB_URI")
        cls.MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "kavach_ai")
        if cls.MONGODB_URI:
            masked_uri = cls.MONGODB_URI[:20] + "..." if len(cls.MONGODB_URI) > 20 else "***"
            logger.info(f"✅ MONGODB_URI loaded: {masked_uri}")
            logger.info(f"📦 MONGODB_DATABASE: {cls.MONGODB_DATABASE}")
        else:
            logger.warning("⚠️  MONGODB_URI not set - using SQLite only")
        
        # JWT
        cls.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", cls.JWT_SECRET_KEY)
        if cls.JWT_SECRET_KEY == "dev-secret-key-change-in-production":
            logger.warning("⚠️  JWT_SECRET_KEY is using development default - CHANGE IN PRODUCTION!")
        else:
            logger.info("✅ JWT_SECRET_KEY configured")
        
        # Environment
        cls.ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
        logger.info(f"🌍 ENVIRONMENT: {cls.ENVIRONMENT}")
        
        # Debug
        cls.DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
        cls.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
        logger.info(f"🔍 DEBUG_MODE: {cls.DEBUG_MODE}")
        logger.info(f"📝 LOG_LEVEL: {cls.LOG_LEVEL}")
        
        # Cloud Run
        cls.PORT = int(os.environ.get("PORT", 8080))
        logger.info(f"🚀 PORT: {cls.PORT}")
        
        logger.info("=" * 80)
        logger.info("✅ Configuration loaded successfully\n")
        
        return cls
    
    @classmethod
    def validate_startup(cls) -> tuple[bool, list[str]]:
        """
        Validate that critical systems are ready.
        Returns (is_ready, list_of_warnings)
        """
        warnings = []
        
        if not cls.GROQ_API_KEY:
            warnings.append("GROQ_API_KEY not configured - using fallback scenarios")
        
        if cls.JWT_SECRET_KEY == "dev-secret-key-change-in-production":
            warnings.append("JWT_SECRET_KEY using development default")
        
        return len(warnings) == 0, warnings


# Load configuration on import
EnvConfig.load()
