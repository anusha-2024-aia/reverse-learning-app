import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.ai_service.gemini_agent import evaluate_explanation
from typing import List

router = APIRouter()

# Mocked auth dependency
def get_current_user():
    return 1

@router.post("/evaluate", response_model=schemas.EvaluationOut)
async def evaluate_user_explanation(evaluation: schemas.EvaluationCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Verify topic exists
    topic = db.query(models.Topic).filter(models.Topic.id == evaluation.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    # Verify session exists and belongs to user
    session = db.query(models.StudySession).filter(
        models.StudySession.id == evaluation.session_id,
        models.StudySession.user_id == current_user
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found or does not belong to user")
        
    # Get AI Evaluation
    ai_result = await evaluate_explanation(
        topic=topic.name,
        user_explanation=evaluation.explanation,
        learning_mode=evaluation.learning_mode
    )
    
    # Extract score
    score = ai_result.get("score", 0)
    
    # Save to database
    db_evaluation = models.Evaluation(
        user_id=current_user,
        topic_id=evaluation.topic_id,
        explanation=evaluation.explanation,
        ai_score=score,
        ai_feedback_json=json.dumps(ai_result)
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    return db_evaluation

@router.get("/evaluations/mine", response_model=List[schemas.EvaluationOut])
def get_my_evaluations(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return db.query(models.Evaluation).filter(models.Evaluation.user_id == current_user).all()
