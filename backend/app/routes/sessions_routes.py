from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter()

# Mocked auth dependency
def get_current_user():
    return 1

@router.get("/topics", response_model=List[schemas.TopicOut])
def get_topics(db: Session = Depends(get_db)):
    return db.query(models.Topic).all()

@router.post("/sessions", response_model=schemas.SessionOut)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    topic = db.query(models.Topic).filter(models.Topic.id == session.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    db_session = models.StudySession(user_id=current_user, topic_id=session.topic_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions/mine", response_model=List[schemas.SessionOut])
def get_my_sessions(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return db.query(models.StudySession).filter(models.StudySession.user_id == current_user).all()
