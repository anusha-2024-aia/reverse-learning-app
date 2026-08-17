from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, UserMastery, Interview, Evaluation, LearningActivity
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Returns aggregated analytics for the user's dashboard.
    """
    # 1. Overall Mastery
    mastery_records = db.query(UserMastery).filter(UserMastery.user_id == current_user.id).all()
    if mastery_records:
        avg_mastery = sum([m.mastery_score for m in mastery_records]) / len(mastery_records)
        topics_mastered = sum([1 for m in mastery_records if m.mastery_score >= 80])
    else:
        avg_mastery = 0
        topics_mastered = 0
        
    # 2. Career Readiness (Aggregate score)
    # Based on Mastery, Recent Interview Scores, and Communication Scores
    recent_interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).limit(3).all()
    avg_interview = sum([i.overall_score for i in recent_interviews if i.overall_score]) / max(len(recent_interviews), 1)
    
    recent_evals = db.query(Evaluation).filter(Evaluation.user_id == current_user.id).order_by(Evaluation.created_at.desc()).limit(10).all()
    avg_communication = sum([e.communication_score for e in recent_evals if e.communication_score]) / max(len([e for e in recent_evals if e.communication_score]), 1)
    
    career_readiness = (avg_mastery * 0.4) + (avg_interview * 10 * 0.4) + (avg_communication * 0.2)
    career_readiness = min(max(career_readiness, 0), 100) # Clamp 0-100
    
    # 3. Weekly Activity Data for Charts
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=6)
    activities = db.query(LearningActivity).filter(
        LearningActivity.user_id == current_user.id,
        LearningActivity.date_logged >= start_date,
        LearningActivity.date_logged <= end_date
    ).all()
    
    weekly_data = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        count = sum([1 for a in activities if a.date_logged == day])
        weekly_data.append({
            "date": day.strftime("%a"),
            "activities": count
        })
        
    # 4. Performance Trends (Last 5 interviews)
    interview_trend = []
    for i in reversed(recent_interviews[:5]):
        interview_trend.append({
            "date": i.created_at.strftime("%b %d"),
            "score": i.overall_score or 0
        })

    return {
        "overall_mastery": round(avg_mastery, 1),
        "topics_mastered": topics_mastered,
        "career_readiness": round(career_readiness, 1),
        "avg_communication_score": round(avg_communication, 1),
        "weekly_activity": weekly_data,
        "interview_trend": interview_trend
    }
