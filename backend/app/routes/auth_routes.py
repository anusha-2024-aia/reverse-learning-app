from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from app.database import get_db
from app import models, auth
from app.rate_limiter import rate_limit_ip

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_rate_limit = rate_limit_ip(default_limit=10, window_seconds=60, env_var_name="AUTH_RATE_LIMIT")

class UserCreate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: Optional[str] = None

    @validator('name', 'username', pre=True, always=True)
    def sanitize_strings(cls, v):
        if v and isinstance(v, str):
            return v.strip()
        return v

class UserLogin(BaseModel):
    username_or_email: Optional[str] = None
    email: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    username: str
    email: str
    target_role: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/register", dependencies=[Depends(auth_rate_limit)])
def register(user: UserCreate, db: Session = Depends(get_db)):
    display_name = (user.name or user.username or user.email.split('@')[0]).strip()
    username = (user.username or user.email.split('@')[0]).strip()

    if not display_name:
        raise HTTPException(status_code=400, detail="Name is required.")

    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    if user.confirm_password is not None and user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Check for duplicate email
    db_email = db.query(models.User).filter(models.User.email == user.email.lower()).first()
    if db_email:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    # Ensure unique username
    base_username = username
    counter = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    hashed_password = auth.hash_password(user.password)
    new_user = models.User(
        name=display_name,
        username=username,
        email=user.email.lower(),
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": str(new_user.id)})

    return {
        "user_id": new_user.id,
        "name": new_user.name,
        "username": new_user.username,
        "email": new_user.email,
        "token": access_token,
        "access_token": access_token
    }

@router.post("/login", response_model=Token, dependencies=[Depends(auth_rate_limit)])
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    identifier = (user_credentials.email or user_credentials.username_or_email or "").strip().lower()
    if not identifier or not user_credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(
        (models.User.email == identifier) | (models.User.username == identifier)
    ).first()

    if not user or not auth.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """
    1-Click demo authentication providing an isolated, realistic sandbox
    under student persona Maya Lin without altering any real user accounts.
    """
    from app.services.demo_service import get_or_create_demo_user
    demo_user = get_or_create_demo_user(db)
    access_token = auth.create_access_token(data={"sub": str(demo_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_role: Optional[str] = None
    skill_level: Optional[str] = None
    learning_goals: Optional[str] = None
    hours_per_day: Optional[float] = None
    days_per_week: Optional[int] = None
    experience_level: Optional[str] = None
    current_skills: Optional[str] = None
    preferred_areas: Optional[str] = None

@router.get("/profile")
def get_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "target_role": current_user.target_role or "Software Engineer",
        "skill_level": current_user.skill_level or "INTERMEDIATE",
        "learning_goals": current_user.learning_goals or "",
        "hours_per_day": current_user.hours_per_day or 2.0,
        "days_per_week": current_user.days_per_week or 6,
        "experience_level": current_user.experience_level or "BEGINNER",
        "current_skills": current_user.current_skills or "[]",
        "preferred_areas": current_user.preferred_areas or "[]",
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.put("/profile")
def update_user_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if profile_data.name is not None:
        current_user.name = profile_data.name.strip()
    if profile_data.target_role is not None:
        current_user.target_role = profile_data.target_role.strip()
    if profile_data.skill_level is not None:
        current_user.skill_level = profile_data.skill_level.strip()
    if profile_data.learning_goals is not None:
        current_user.learning_goals = profile_data.learning_goals.strip()
    if profile_data.hours_per_day is not None:
        current_user.hours_per_day = profile_data.hours_per_day
    if profile_data.days_per_week is not None:
        current_user.days_per_week = profile_data.days_per_week
    if profile_data.experience_level is not None:
        current_user.experience_level = profile_data.experience_level
    if profile_data.current_skills is not None:
        current_user.current_skills = profile_data.current_skills
    if profile_data.preferred_areas is not None:
        current_user.preferred_areas = profile_data.preferred_areas

    db.commit()
    db.refresh(current_user)
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "username": current_user.username,
            "email": current_user.email,
            "target_role": current_user.target_role,
            "hours_per_day": current_user.hours_per_day,
            "days_per_week": current_user.days_per_week
        }
    }

import secrets
from datetime import datetime, timezone, timedelta
from app.core.logging_config import logger

RECOVERY_TOKENS = {}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == clean_email).first()

    token = f"{secrets.randbelow(900000) + 100000}"
    RECOVERY_TOKENS[clean_email] = {
        "token": token,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    logger.info(f"Password recovery token generated for {clean_email}")

    return {
        "message": "If an account exists for this email, a verification recovery code has been generated.",
        "token": token
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    recovery = RECOVERY_TOKENS.get(clean_email)

    if not recovery or recovery["token"] != req.token.strip():
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")

    if datetime.now(timezone.utc) > recovery["expires_at"]:
        RECOVERY_TOKENS.pop(clean_email, None)
        raise HTTPException(status_code=400, detail="Verification token has expired. Please request a new one.")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    user = db.query(models.User).filter(models.User.email == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    user.password_hash = auth.hash_password(req.new_password)
    db.commit()
    RECOVERY_TOKENS.pop(clean_email, None)
    return {"message": "Password updated successfully. You can now log in with your new password."}
