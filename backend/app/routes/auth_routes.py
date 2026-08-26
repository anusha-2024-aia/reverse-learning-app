from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from app.database import get_db
from app import models, auth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

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

@router.post("/register")
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

@router.post("/login", response_model=Token)
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
