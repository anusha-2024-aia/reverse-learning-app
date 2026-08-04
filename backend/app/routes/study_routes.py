from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.ai_service.gemini_agent import evaluate_explanation, stream_evaluate_explanation
from app.database import get_db
from app.models import Evaluation, Topic
from app.services import achievement_service

router = APIRouter()

class EvaluationRequest(BaseModel):
    topic_id: int
    topic: str
    explanation: str
    learning_mode: str = "general"

@router.post("/evaluate")
async def evaluate_user_study(request: EvaluationRequest, db: Session = Depends(get_db)):
    """
    Endpoint to evaluate a user's explanation of a topic.
    """
    if not request.topic_id or not request.explanation:
        raise HTTPException(status_code=400, detail="Topic ID and explanation are required")
    
    # Check if topic exists
    topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    result = await evaluate_explanation(request.topic, request.explanation, request.learning_mode)
    
    # Save to db
    eval_record = Evaluation(
        topic_id=request.topic_id,
        user_id=1, # Mock auth
        score=result.get("score"),
        summary=result.get("summary"),
        grammar_issues=json.dumps(result.get("grammar_issues", [])),
        advanced_version=result.get("advanced_version"),
        vocabulary_suggestions=json.dumps(result.get("vocabulary_suggestions", [])),
        follow_up_question=result.get("follow_up_question"),
        learning_mode=request.learning_mode
    )
    db.add(eval_record)
    db.commit()
    
    # Check for newly unlocked achievements
    achievement_service.check_achievements_for_user(db, 1)
    
    return result

@router.post("/evaluate-stream")
async def evaluate_user_study_stream(request: EvaluationRequest):
    """
    Endpoint to evaluate a user's explanation with real-time streaming feedback.
    (Note: Streaming does not save to DB immediately in this version, requires a separate save endpoint or sync after complete)
    """
    if not request.topic or not request.explanation:
        raise HTTPException(status_code=400, detail="Topic and explanation are required")

    return StreamingResponse(
        stream_evaluate_explanation(request.topic, request.explanation, request.learning_mode),
        media_type="text/plain"
    )
