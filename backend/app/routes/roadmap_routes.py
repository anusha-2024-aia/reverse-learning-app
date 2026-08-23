from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap, RoadmapItem, Topic, Evaluation
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

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
async def process_onboarding(data: OnboardingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Saves onboarding choices (Role, Skills, Experience, Goal, Time, Preferences)
    and generates the student's initial personalized AI roadmap.
    """
    try:
        onboarding_dict = data.dict()
        result = await RoadmapService.generate_initial_roadmap(db, current_user, onboarding_dict)
        return result
    except Exception as e:
        print(f"Onboarding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        print(f"Error fetching roadmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        print(f"Error generating roadmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        print(f"Error recalculating roadmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-focus")
def get_current_focus(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets the current focus topic and next best action.
    """
    result = RoadmapService.get_current_focus(db, current_user.id)
    if not result:
        return {"current_focus": None}
    return result

@router.get("/daily-plan")
def get_daily_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets today's structured learning plan based on available daily hours.
    """
    roadmap_data = RoadmapService.get_my_roadmap(db, current_user.id)
    if not roadmap_data or not roadmap_data.get("daily_plan"):
        return {"daily_plan": None}
    return {"daily_plan": roadmap_data.get("daily_plan")}

@router.get("/history")
def get_roadmap_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets change timeline of roadmap adaptations.
    """
    history = RoadmapService.get_roadmap_history(db, current_user.id)
    return {"history": history}

@router.get("/topic/{topic_id}")
def get_roadmap_topic_detail(topic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets detailed evaluation history and prerequisite status for a specific topic item.
    """
    item = db.query(RoadmapItem).filter(RoadmapItem.id == topic_id, RoadmapItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap topic item not found")

    evals = []
    if item.topic_id:
        evals = db.query(Evaluation).filter(Evaluation.user_id == current_user.id, Evaluation.topic_id == item.topic_id).order_by(Evaluation.created_at.desc()).all()

    return {
        "item": {
            "id": item.id,
            "topic_name": item.topic_name,
            "category": item.category,
            "description": item.description,
            "importance": item.importance,
            "difficulty": item.difficulty,
            "mastery_score": item.mastery_score,
            "status": item.status,
            "reason": item.reason,
            "estimated_hours": item.estimated_hours,
            "topic_id": item.topic_id
        },
        "evaluations_count": len(evals),
        "recent_evaluations": [
            {
                "id": e.id,
                "overall_score": e.overall_score or e.ai_score,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in evals[:5]
        ]
    }

@router.patch("/preferences")
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
        print(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))
