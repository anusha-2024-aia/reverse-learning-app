from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from app.database import get_db
from app.auth import get_current_user
from app.rate_limiter import rate_limit_authenticated
from app.models import User, Roadmap, RoadmapItem, Topic, Evaluation
from app.services.roadmap_service import RoadmapService

from app.core.logging_config import logger

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

roadmap_rate_limit = rate_limit_authenticated(default_limit=3, window_seconds=60, env_var_name="ROADMAP_RATE_LIMIT")

class OnboardingRequest(BaseModel):
    target_role: str = Field(..., example="Full Stack Developer")
    current_skills: Optional[List[str]] = []
    experience_level: str = Field("BEGINNER", example="BEGINNER")
    career_goal: Optional[str] = "Get placed as a software developer"
    hours_per_day: float = Field(2.0, example=2.0)
    days_per_week: int = Field(6, example=6)
    preferred_areas: Optional[List[str]] = []

class PreferencesUpdateRequest(BaseModel):
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    career_goal: Optional[str] = None
    hours_per_day: Optional[float] = None
    days_per_week: Optional[int] = None
    preferred_areas: Optional[List[str]] = None

@router.post("/onboarding")
async def process_onboarding(data: OnboardingRequest, db: Session = Depends(get_db), current_user: User = Depends(roadmap_rate_limit)):
    """
    Saves onboarding choices (Role, Skills, Experience, Goal, Time, Preferences)
    and generates the student's initial personalized AI roadmap.
    """
    try:
        onboarding_dict = data.dict()
        result = await RoadmapService.generate_initial_roadmap(db, current_user, onboarding_dict)
        return result
    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        raise HTTPException(status_code=500, detail="Unable to process onboarding right now.")

@router.get("/mine")
def get_my_roadmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets the current user's active personalized roadmap, complete with progress,
    estimated days, current focus topic, daily learning plan, and change history.
    """
    try:
        result = RoadmapService.get_my_roadmap(db, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error fetching roadmap: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch roadmap right now.")

@router.post("/generate")
async def generate_roadmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Re-generates initial AI roadmap structure using Gemini based on stored user profile.
    """
    try:
        onboarding_dict = {
            "target_role": current_user.target_role or "Full Stack Developer",
            "experience_level": current_user.experience_level or "BEGINNER",
            "career_goal": current_user.learning_goals or "Career placement",
            "hours_per_day": current_user.hours_per_day or 2.0,
            "days_per_week": current_user.days_per_week or 6,
            "current_skills": current_user.current_skills or "[]",
            "preferred_areas": current_user.preferred_areas or "[]"
        }
        result = await RoadmapService.generate_initial_roadmap(db, current_user, onboarding_dict)
        return result
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Unable to generate roadmap right now.")

@router.post("/recalculate")
def recalculate_roadmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Runs the deterministic dynamic engine to update topic priorities, statuses,
    prerequisite surfacing, progress %, and change tracking based on latest evaluations.
    """
    try:
        result = RoadmapService.recalculate_roadmap(db, current_user.id)
        if not result or not result.get("roadmap_id"):
            raise HTTPException(status_code=404, detail="No active roadmap found. Please complete onboarding first.")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Unable to recalculate roadmap right now.")

@router.get("/current-focus")
def get_current_focus(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets the current focus topic and next best action.
    """
    return RoadmapService.get_current_focus(db, current_user.id)

@router.get("/summary")
def get_roadmap_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns lightweight high-level roadmap metrics for dashboard/home widgets.
    """
    return RoadmapService.get_roadmap_summary(db, current_user.id)

@router.get("/items/{item_id}")
def get_roadmap_item_detail(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns details for a single roadmap item verifying ownership.
    """
    item = db.query(RoadmapItem).join(Roadmap).filter(
        RoadmapItem.id == item_id,
        Roadmap.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found or access denied.")

    return {
        "id": item.id,
        "topic_id": item.topic_id,
        "title": item.title,
        "category": item.category,
        "sequence_order": item.sequence_order,
        "estimated_hours": item.estimated_hours,
        "status": item.status,
        "priority_score": item.priority_score,
        "mastery_level": item.mastery_level,
        "unlock_requirements": item.unlock_requirements,
        "reason_added": item.reason_added
    }

@router.put("/preferences")
async def update_preferences(data: PreferencesUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates target role, hours per day, career goal, or preferences.
    Triggers re-generation if target role changes; otherwise recalculates.
    """
    try:
        prefs_dict = {k: v for k, v in data.dict().items() if v is not None}
        result = await RoadmapService.update_preferences(db, current_user.id, prefs_dict)
        return result
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Unable to update preferences right now.")
