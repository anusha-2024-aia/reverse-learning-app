from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import achievement_service, insights_service

router = APIRouter()

USER_ID = 1 # Mocked auth

@router.get("/mine")
def get_mine(db: Session = Depends(get_db)):
    return achievement_service.get_user_achievements(db, USER_ID)

@router.get("/recent-unlocks")
def get_recent_unlocks(db: Session = Depends(get_db)):
    return achievement_service.get_recent_unlocks(db, USER_ID)

@router.get("/streak")
def get_streak(db: Session = Depends(get_db)):
    current_streak = insights_service.calculate_streak(db, USER_ID)
    # Mocking longest streak for now
    longest_streak = current_streak if current_streak > 0 else 0
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_active_date": None
    }
