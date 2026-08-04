from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Curriculum, Topic, Evaluation

router = APIRouter()

@router.get("/curricula")
def get_curricula(db: Session = Depends(get_db)):
    curricula = db.query(Curriculum).all()
    result = []
    for c in curricula:
        topic_count = db.query(func.count(Topic.id)).filter(Topic.curriculum_id == c.id).scalar()
        result.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "difficulty": c.difficulty,
            "topic_count": topic_count
        })
    return {"curricula": result}

@router.get("/curricula/{curriculum_id}")
def get_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
        
    topics = db.query(Topic).filter(Topic.curriculum_id == c.id).order_by(Topic.order_in_curriculum).all()
    topic_list = []
    for t in topics:
        topic_list.append({
            "id": t.id,
            "name": t.name,
            "order": t.order_in_curriculum,
            "description": t.description
        })
        
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "topics": topic_list
    }

@router.get("/curricula/{curriculum_id}/progress")
def get_curriculum_progress(curriculum_id: int, db: Session = Depends(get_db)):
    user_id = 1 # Mock auth
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
        
    topics = db.query(Topic).filter(Topic.curriculum_id == c.id).order_by(Topic.order_in_curriculum).all()
    topic_progress = []
    
    for t in topics:
        evals = db.query(Evaluation).filter(Evaluation.topic_id == t.id, Evaluation.user_id == user_id).all()
        best_score = max([e.score for e in evals if e.score is not None], default=None) if evals else None
        attempts_count = len(evals)
        last_attempt = max([e.created_at for e in evals], default=None) if evals else None
        
        topic_progress.append({
            "id": t.id,
            "name": t.name,
            "best_score": best_score,
            "attempts": attempts_count,
            "last_attempt": last_attempt.isoformat() if last_attempt else None
        })
        
    return {
        "curriculum_id": curriculum_id,
        "topics": topic_progress
    }
