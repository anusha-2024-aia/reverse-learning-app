from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.services import achievement_service, activity_service

router = APIRouter()

@router.get("/mine")
def get_mine(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns achievements, unlocked counts, progress metrics, and streak info for current authenticated user.
    """
    return achievement_service.get_user_achievements(db, current_user.id)

@router.get("/recent-unlocks")
def get_recent_unlocks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns newly unlocked achievement badges for popups and notification banners.
    """
    return achievement_service.get_recent_unlocks(db, current_user.id)

@router.get("/streak")
def get_streak(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns current active streak and personal best longest streak for current authenticated user.
    """
    return activity_service.ActivityService.get_streak_info(db, current_user.id)
