from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Evaluation, Topic
import json

router = APIRouter()

USER_ID = 1 # Authenticated user identity

@router.get("/")
def get_weakest_topic_knowledge_gap(db: Session = Depends(get_db)):
    """
    Returns the single weakest topic based on the latest evaluation score.
    """
    # Get all distinct topics the user has evaluated
    evaluations = db.query(Evaluation).filter(
        Evaluation.user_id == USER_ID,
        Evaluation.ai_score != None
    ).order_by(desc(Evaluation.created_at)).all()
    
    if not evaluations:
        return {"has_gap": False}
        
    # Find the latest score for each topic
    latest_scores = {}
    for ev in evaluations:
        if ev.topic_id not in latest_scores:
            latest_scores[ev.topic_id] = ev
            
    # Find the topic with the absolute lowest latest score
    weakest_eval = min(latest_scores.values(), key=lambda e: e.ai_score)
    weakest_topic = db.query(Topic).filter(Topic.id == weakest_eval.topic_id).first()
    
    score = weakest_eval.ai_score
    
    # Status Thresholds
    if score < 60:
        status = "⚠️ Knowledge Gap Detected"
    elif score < 80:
        status = "🟡 Needs Improvement"
    else:
        status = "✅ No Major Knowledge Gap"
        
    # Extract Reason
    reason = "Your latest score indicates that this topic needs more practice."
    if weakest_eval.ai_feedback_json:
        try:
            feedback = json.loads(weakest_eval.ai_feedback_json)
            # Try to grab the first weakness
            if "weaknesses" in feedback and len(feedback["weaknesses"]) > 0:
                reason = feedback["weaknesses"][0]
        except:
            pass
            
    # Simple recommendation
    recommendation = f"Review {weakest_topic.name} and practice basic problems before explaining the topic again."
    
    return {
        "has_gap": True,
        "topic_id": weakest_topic.id,
        "topic": weakest_topic.name,
        "score": score,
        "status": status,
        "reason": reason,
        "recommendation": recommendation
    }
