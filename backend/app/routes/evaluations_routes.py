import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.ai_service.gemini_agent import evaluate_explanation
from app.services import achievement_service
from typing import List

router = APIRouter()

# Mocked auth dependency
def get_current_user():
    return 1

@router.post("/evaluate")
async def evaluate_user_explanation(evaluation: schemas.EvaluationCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # Verify topic exists
    topic = db.query(models.Topic).filter(models.Topic.id == evaluation.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    # Get AI Evaluation
    ai_result = await evaluate_explanation(
        topic=topic.name,
        user_explanation=evaluation.explanation,
        learning_mode=evaluation.learning_mode
    )
    # Calculate metrics
    explanation_length = len(evaluation.explanation.split())
    strengths_count = len(ai_result.get("strengths", []))
    weaknesses_count = len(ai_result.get("weaknesses", []))
    score = ai_result.get("score", 0)
    
    # Save to database
    db_evaluation = models.Evaluation(
        user_id=current_user,
        topic_id=evaluation.topic_id,
        explanation=evaluation.explanation,
        ai_score=score,
        ai_feedback_json=json.dumps(ai_result),
        explanation_length=explanation_length,
        strengths_count=strengths_count,
        weaknesses_count=weaknesses_count
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    # Check for newly unlocked achievements
    achievement_service.check_achievements_for_user(db, current_user)
    
    # Return structured response for frontend
    return {
        "evaluation_id": db_evaluation.id,
        "score": score,
        "summary": ai_result.get("summary", ""),
        "strengths": ai_result.get("strengths", []),
        "weaknesses": ai_result.get("weaknesses", []),
        "correct_version": ai_result.get("correct_version", ""),
        "follow_up_question": ai_result.get("follow_up_question", ""),
        "learning_suggestions": ai_result.get("learning_suggestions", []),
        "feedback_sections": ai_result.get("feedback_sections", []),
        "full_explanation_length": explanation_length
    }

@router.get("/evaluations/mine")
def get_my_evaluations(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    evals = db.query(models.Evaluation, models.Topic, models.Curriculum).join(
        models.Topic, models.Evaluation.topic_id == models.Topic.id
    ).join(
        models.Curriculum, models.Topic.curriculum_id == models.Curriculum.id
    ).filter(models.Evaluation.user_id == current_user).order_by(models.Evaluation.created_at.desc()).all()
    
    result = []
    for e, t, c in evals:
        result.append({
            "id": e.id,
            "topic_id": e.topic_id,
            "topic_name": t.name,
            "curriculum_name": c.name,
            "learning_mode": getattr(e, 'learning_mode', "general"),
            "ai_score": e.ai_score,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "ai_feedback_json": e.ai_feedback_json
        })
    return result
