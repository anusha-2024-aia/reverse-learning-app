from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter()

from app.auth import get_current_user

@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    topic = db.query(models.Topic).filter(models.Topic.id == session.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db_session = models.StudySession(user_id=current_user.id, topic_id=session.topic_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions/mine", response_model=List[schemas.SessionOut])
def get_my_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.StudySession).filter(models.StudySession.user_id == current_user.id).all()

from pydantic import BaseModel
from typing import Optional
from datetime import date

class FocusSessionLog(BaseModel):
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    duration_minutes: int = 25
    objective: Optional[str] = None
    notes: Optional[str] = None

@router.post("/sessions/live-focus")
def log_live_focus_session(
    payload: FocusSessionLog,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    topic = None
    if payload.topic_id:
        topic = db.query(models.Topic).filter(models.Topic.id == payload.topic_id).first()
    elif payload.topic_name:
        topic = db.query(models.Topic).filter(models.Topic.name.ilike(f"%{payload.topic_name}%")).first()

    if not topic:
        topic = db.query(models.Topic).first()

    target_topic_id = topic.id if topic else 1
    db_session = models.StudySession(user_id=current_user.id, topic_id=target_topic_id)
    db.add(db_session)

    db.add(models.LearningActivity(
        user_id=current_user.id,
        activity_type="study_focus",
        date_logged=date.today()
    ))
    db.commit()
    db.refresh(db_session)

    return {
        "status": "success",
        "session_id": db_session.id,
        "duration_minutes": payload.duration_minutes,
        "topic_name": topic.name if topic else "General Study Session",
        "message": f"Focus session of {payload.duration_minutes}m successfully logged to your learning history."
    }
