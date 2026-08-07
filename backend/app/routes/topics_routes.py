from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Topic, Curriculum

router = APIRouter()

@router.get("/topics")
def get_topics(curriculum_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Topic)
    if curriculum_id:
        query = query.filter(Topic.curriculum_id == curriculum_id)
        
    topics = query.all()
    result = []
    for t in topics:
        result.append({
            "id": t.id,
            "name": t.name,
            "curriculum_id": t.curriculum_id,
            "description": t.description
        })
    return {"topics": result}

@router.get("/topics/{topic_id}")
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    c = db.query(Curriculum).filter(Curriculum.id == t.curriculum_id).first()
    
    return {
        "id": t.id,
        "name": t.name,
        "curriculum_id": t.curriculum_id,
        "curriculum_name": c.name if c else None,
        "description": t.description
    }
