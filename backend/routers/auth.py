"""
Authentication endpoints for Kavach AI.
Handles signup, login, logout, token refresh, and user management.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from backend.database_models import get_db, User, init_db
from backend.auth.auth import PasswordManager, TokenManager, get_current_user
from backend.logs_structured import log_auth_event
from backend.mongo_models import save_user_session, UserSessionModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize database on import
try:
    init_db()
except:
    pass


# ────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ────────────────────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    """User signup request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, max_length=255, description="Full name")


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    name: str
    level: str
    xp: int
    total_xp: int
    security_score: float
    streak_days: int
    simulations_attempted: int
    simulations_passed: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User's email address (must be unique)
    - **password**: At least 8 characters
    - **name**: User's full name
    
    Returns access and refresh tokens.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        log_auth_event("signup_failed", error="email_already_exists", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = PasswordManager.hash_password(request.password)
        
        new_user = User(
            id=user_id,
            email=request.email,
            password_hash=hashed_password,
            name=request.name,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens
        tokens = TokenManager.generate_tokens(user_id, request.email)
        
        log_auth_event("signup_success", user_id=user_id, email=request.email)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
    
    except Exception as e:
        db.rollback()
        log_auth_event("signup_error", error=str(e)[:200], email=request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db), http_request: Request = None):
    """
    Authenticate user and return tokens.
    Also saves login session to MongoDB for user history tracking.
    
    - **email**: User's email
    - **password**: User's password
    
    Returns access and refresh tokens.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        log_auth_event("login_failed", error="user_not_found", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not PasswordManager.verify_password(request.password, user.password_hash):
        log_auth_event("login_failed", error="invalid_password", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        log_auth_event("login_failed", error="account_disabled", user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    try:
        # Update last login in SQLite
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Save session to MongoDB
        ip_address = http_request.client.host if http_request else None
        user_agent = http_request.headers.get("user-agent") if http_request else None
        
        session = UserSessionModel(
            email=user.email,
            username=user.name,
            user_id=int(user.id) if user.id.isdigit() else hash(user.id) % 10000,
            ip_address=ip_address,
            user_agent=user_agent,
            session_active=True
        )
        
        await save_user_session(session)
        
        # Generate tokens
        tokens = TokenManager.generate_tokens(user.id, user.email)
        
        log_auth_event("login_success", user_id=user.id, email=user.email)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
    
    except Exception as e:
        db.rollback()
        log_auth_event("login_error", user_id=user.id, error=str(e)[:200])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.
    
    - **refresh_token**: Valid refresh token from login/signup
    
    Returns new access token.
    """
    try:
        tokens = TokenManager.refresh_access_token(request.refresh_token)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=request.refresh_token,  # Same refresh token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information.
    Requires valid access token.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user (invalidates token).
    Note: JWT is stateless, so logout is just a client-side operation.
    """
    log_auth_event("logout", user_id=current_user["user_id"])
    
    return {
        "message": "Successfully logged out",
        "status": "ok"
    }


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if name:
        user.name = name
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    log_auth_event("profile_updated", user_id=user.id)
    
    return UserResponse.from_orm(user)
