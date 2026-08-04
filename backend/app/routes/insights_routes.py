from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import insights_service

router = APIRouter()

USER_ID = 1 # Mocked auth for Phase 3

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return insights_service.get_summary_stats(db, USER_ID)

@router.get("/score-trend")
def get_score_trend(days: int = 7, db: Session = Depends(get_db)):
    return insights_service.calculate_score_trend(db, USER_ID, days)

@router.get("/weak-topics")
def get_weak_topics(db: Session = Depends(get_db)):
    return insights_service.get_weak_topics(db, USER_ID)

@router.get("/most-improved")
def get_most_improved(db: Session = Depends(get_db)):
    return insights_service.get_most_improved_topics(db, USER_ID)

@router.get("/most-attempted")
def get_most_attempted(db: Session = Depends(get_db)):
    return insights_service.get_most_attempted_topics(db, USER_ID)

@router.get("/grammar-trend")
def get_grammar_trend(db: Session = Depends(get_db)):
    return insights_service.get_grammar_trend(db, USER_ID)

@router.get("/curriculum-stats")
def get_curriculum_stats(db: Session = Depends(get_db)):
    return insights_service.get_curriculum_stats(db, USER_ID)
