from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.auth import get_current_user
from app.models import User, AdaptiveRecommendation
from app.schemas import AdaptiveRecommendationOut, AdaptiveRecommendationUpdate
from app.services.adaptive_learning_engine import calculate_next_recommendation, generate_user_learning_path
from datetime import datetime, timezone
# Keep existing imports if needed, but the prompt says to replace the adaptive logic with the new one.
from app.services.adaptive_engine import AdaptiveEngine

router = APIRouter()

# --- Legacy routes (kept for compatibility) ---
@router.get("/recommendations/weak-topics")
def get_weak_topics(limit: int = 3, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    topics = AdaptiveEngine.get_weak_topics(db, current_user.id, limit)
    return {"weak_topics": topics}

@router.get("/recommendations/strong-topics")
def get_strong_topics(limit: int = 3, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    topics = AdaptiveEngine.get_strong_topics(db, current_user.id, limit)
    return {"strong_topics": topics}

# --- New Adaptive Learning Engine Routes ---

@router.get("/adaptive-learning/recommendation", response_model=AdaptiveRecommendationOut)
def get_current_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = db.query(AdaptiveRecommendation).filter(
        AdaptiveRecommendation.user_id == current_user.id,
        AdaptiveRecommendation.status == "PENDING"
    ).order_by(AdaptiveRecommendation.priority_score.desc()).first()
    
    if not rec:
        rec = calculate_next_recommendation(db, current_user.id)
        
    if not rec:
        raise HTTPException(status_code=404, detail="No adaptive recommendations available yet.")
        
    return rec

@router.get("/adaptive-learning/path")
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    path = generate_user_learning_path(db, current_user.id)
    return {"path": path}

@router.post("/adaptive-learning/recalculate", response_model=AdaptiveRecommendationOut)
def recalculate_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = calculate_next_recommendation(db, current_user.id)
    if not rec:
        raise HTTPException(status_code=404, detail="Could not generate new recommendation.")
    return rec

@router.put("/adaptive-learning/recommendation/{rec_id}/status", response_model=AdaptiveRecommendationOut)
def update_recommendation_status(
    rec_id: int,
    status_update: AdaptiveRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = db.query(AdaptiveRecommendation).filter(
        AdaptiveRecommendation.id == rec_id,
        AdaptiveRecommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "SKIPPED", "OBSOLETE"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    rec.status = status_update.status
    if status_update.status in ["COMPLETED", "SKIPPED"]:
        rec.completed_at = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(rec)
    return rec
