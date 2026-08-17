from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap, RoadmapItem
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

@router.post("/generate")
async def generate_roadmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generates a personalized roadmap using Gemini based on the user's profile.
    """
    try:
        result = await RoadmapService.generate_roadmap_for_user(db, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mine")
def get_my_roadmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Gets the current user's active roadmap.
    """
    roadmap = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).first()
    if not roadmap:
        return {"roadmap": None}
        
    items = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.order_index.asc()).all()
    
    return {
        "roadmap_id": roadmap.id,
        "target_role": roadmap.target_role,
        "status": roadmap.status,
        "items": [
            {
                "id": item.id,
                "topic_name": item.topic_name,
                "status": item.status,
                "priority": item.priority,
                "difficulty": item.difficulty,
                "order_index": item.order_index
            } for item in items
        ]
    }
