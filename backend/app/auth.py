import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

# Configuration
SECRET_KEY = (os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or "").strip()
if not SECRET_KEY:
    raise RuntimeError(
        "JWT secret is not configured. Set the JWT_SECRET environment variable before starting the application."
    )
ALGORITHM = "HS256"

# Parse JWT_EXPIRES_IN (e.g. '1d', '24h', '60m' or integer minutes)
def _get_expiration_minutes() -> int:
    env_val = os.getenv("JWT_EXPIRES_IN", "1d").strip().lower()
    if env_val.endswith("d"):
        try:
            return int(env_val[:-1]) * 24 * 60
        except ValueError:
            pass
    elif env_val.endswith("h"):
        try:
            return int(env_val[:-1]) * 60
        except ValueError:
            pass
    elif env_val.endswith("m"):
        try:
            return int(env_val[:-1])
        except ValueError:
            pass
    try:
        return int(env_val)
    except ValueError:
        return 1440 # Default to 1 day

ACCESS_TOKEN_EXPIRE_MINUTES = _get_expiration_minutes()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    sub_str = str(sub)
    if sub_str.isdigit():
        user = db.query(models.User).filter(models.User.id == int(sub_str)).first()
    else:
        user = db.query(models.User).filter(
            (models.User.username == sub_str) | (models.User.email == sub_str)
        ).first()

    if user is None:
        raise credentials_exception
    return user
