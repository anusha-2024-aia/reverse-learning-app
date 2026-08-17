from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.services.adaptive_engine import AdaptiveEngine

router = APIRouter()

@router.get("/recommendations/weak-topics")
def get_weak_topics(limit: int = 3, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns the user's weakest topics along with recommendations.
    """
    topics = AdaptiveEngine.get_weak_topics(db, current_user.id, limit)
    return {"weak_topics": topics}

@router.get("/recommendations/strong-topics")
def get_strong_topics(limit: int = 3, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns the user's strongest topics.
    """
    topics = AdaptiveEngine.get_strong_topics(db, current_user.id, limit)
    return {"strong_topics": topics}
