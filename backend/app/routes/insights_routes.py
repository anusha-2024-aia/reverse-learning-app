from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
from app.services import insights_service

router = APIRouter()

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_summary_stats(db, current_user.id)

@router.get("/score-trend")
def get_score_trend(days: int = 7, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.calculate_score_trend(db, current_user.id, days)

@router.get("/weak-topics")
def get_weak_topics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_weak_topics(db, current_user.id)

@router.get("/most-improved")
def get_most_improved(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_most_improved_topics(db, current_user.id)

@router.get("/strong-topics")
def get_strong_topics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_strong_topics(db, current_user.id)

@router.get("/ai-insight")
def get_ai_insight(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_ai_insight(db, current_user.id)

@router.get("/most-attempted")
def get_most_attempted(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_most_attempted_topics(db, current_user.id)

@router.get("/grammar-trend")
def get_grammar_trend(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_grammar_trend(db, current_user.id)

@router.get("/curriculum-stats")
def get_curriculum_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return insights_service.get_curriculum_stats(db, current_user.id)
