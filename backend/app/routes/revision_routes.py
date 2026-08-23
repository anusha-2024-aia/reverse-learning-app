from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.smart_revision_service import SmartRevisionService
from app.routes.evaluations_routes import evaluate_user_explanation

router = APIRouter()

@router.get("/revisions")
def get_user_revisions(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns categorized revision items (Overdue, Due Today, Tomorrow, Upcoming, History, Summary)
    for the authenticated user.
    """
    return SmartRevisionService.get_user_revisions(db, current_user.id)

@router.get("/revisions/summary")
def get_revisions_summary(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns summary statistics for Smart Revision (used by Dashboard & UI headers).
    """
    data = SmartRevisionService.get_user_revisions(db, current_user.id)
    return data.get("summary", {})

@router.get("/revisions/today")
def get_revisions_due_today(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns revisions due today for the authenticated user.
    """
    data = SmartRevisionService.get_user_revisions(db, current_user.id)
    return data.get("due_today", [])

@router.get("/revisions/overdue")
def get_revisions_overdue(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns overdue revisions for the authenticated user.
    """
    data = SmartRevisionService.get_user_revisions(db, current_user.id)
    return data.get("overdue", [])

@router.get("/revisions/upcoming")
def get_revisions_upcoming(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns upcoming revisions for the authenticated user.
    """
    data = SmartRevisionService.get_user_revisions(db, current_user.id)
    return {
        "tomorrow": data.get("tomorrow", []),
        "upcoming": data.get("upcoming", []),
        "grouped_upcoming": data.get("grouped_upcoming", {})
    }

@router.get("/revisions/{topic_id}/history")
def get_topic_revision_history(
    topic_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns attempt & score history for a specific topic for the authenticated user.
    """
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    all_history = SmartRevisionService.get_user_revision_history_all(db, current_user.id)
    topic_history = next((h for h in all_history if h["topic_id"] == topic_id), None)
    
    if not topic_history:
        return {
            "topic_id": topic_id,
            "topic_name": topic.name,
            "total_attempts": 0,
            "first_score": 0,
            "latest_score": 0,
            "improvement": 0,
            "scores_progression": "No attempts yet",
            "history_attempts": []
        }
        
    return topic_history

@router.post("/revisions/{topic_id}/start")
def start_revision_session(
    topic_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Prepares briefing details for starting a focused revision session.
    """
    briefing = SmartRevisionService.get_revision_briefing(db, current_user.id, topic_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Topic or revision data not found")
    return briefing

@router.post("/revisions/{topic_id}/complete")
async def complete_revision_session(
    topic_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Processes completed revision session, runs evaluation, updates schedule,
    and returns revision completion results (+X% improvement, next review date).
    """
    explanation = payload.get("explanation", "").strip()
    learning_mode = payload.get("learning_mode", "technical")
    
    if not explanation or len(explanation) < 5:
        raise HTTPException(status_code=400, detail="Explanation is too short")
        
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Fetch previous mastery score
    existing_sched = db.query(models.RevisionSchedule).filter(
        models.RevisionSchedule.user_id == current_user.id,
        models.RevisionSchedule.topic_id == topic_id
    ).first()
    
    previous_mastery = round(existing_sched.current_mastery_score, 1) if existing_sched else 0.0

    # Execute evaluation pipeline
    eval_create = schemas.EvaluationCreate(
        topic_id=topic_id,
        explanation=explanation,
        learning_mode=learning_mode
    )
    
    eval_result = await evaluate_user_explanation(
        evaluation=eval_create,
        db=db,
        current_user=current_user
    )
    
    new_mastery = float(eval_result.get("overall_score", 0))

    # Update RevisionSchedule
    updated_sched = SmartRevisionService.update_revision_schedule(
        db=db,
        user_id=current_user.id,
        topic_id=topic_id,
        new_mastery_score=new_mastery
    )

    improvement = round(new_mastery - previous_mastery, 1)
    interval_days = SmartRevisionService.calculate_revision_interval(new_mastery)

    next_review_str = "In 1 day" if interval_days == 1 else f"In {interval_days} days"

    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "previous_mastery": previous_mastery,
        "new_mastery": new_mastery,
        "improvement": improvement,
        "improvement_formatted": f"+{improvement}%" if improvement > 0 else f"{improvement}%",
        "next_revision_days": interval_days,
        "next_revision_formatted": next_review_str,
        "next_review_at": updated_sched.next_review_at.isoformat() if updated_sched.next_review_at else None,
        "ai_insight": eval_result.get("ai_insight") or eval_result.get("summary") or "Keep practicing to solidify your knowledge!",
        "evaluation": eval_result
    }
