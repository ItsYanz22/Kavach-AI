"""
Authentication system for Kavach AI.
Handles user registration, login, JWT tokens, and session management.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import EnvConfig
from backend.logs_structured import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


class PasswordManager:
    """Handle password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class TokenManager:
    """Generate and validate JWT tokens."""
    
    @staticmethod
    def generate_tokens(user_id: str, email: str) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        now = datetime.now(timezone.utc)
        
        # Access token (short-lived)
        access_payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(hours=EnvConfig.JWT_EXPIRATION_HOURS),
        }
        
        access_token = jwt.encode(
            access_payload,
            EnvConfig.JWT_SECRET_KEY,
            algorithm=EnvConfig.JWT_ALGORITHM
        )
        
        # Refresh token (long-lived)
        refresh_payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=EnvConfig.JWT_REFRESH_EXPIRATION_DAYS),
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            EnvConfig.JWT_SECRET_KEY,
            algorithm=EnvConfig.JWT_ALGORITHM
        )
        
        logger.info_event(
            "tokens_generated",
            user_id=user_id,
            email=email
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                EnvConfig.JWT_SECRET_KEY,
                algorithms=[EnvConfig.JWT_ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """Generate a new access token from a refresh token."""
        try:
            payload = jwt.decode(
                refresh_token,
                EnvConfig.JWT_SECRET_KEY,
                algorithms=[EnvConfig.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            
            # Generate new access token
            now = datetime.now(timezone.utc)
            access_payload = {
                "sub": user_id,
                "type": "access",
                "iat": now,
                "exp": now + timedelta(hours=EnvConfig.JWT_EXPIRATION_HOURS),
            }
            
            access_token = jwt.encode(
                access_payload,
                EnvConfig.JWT_SECRET_KEY,
                algorithm=EnvConfig.JWT_ALGORITHM
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
            }
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        payload = TokenManager.verify_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "user_id": user_id,
            "email": payload.get("email"),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error_event("token_verification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_optional_user(request) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise None."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        token = auth_header.replace("Bearer ", "")
        payload = TokenManager.verify_token(token)
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
        }
    except:
        return None


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class TokenError(Exception):
    """Custom token error."""
    pass

