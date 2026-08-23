from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import json
from app.models import Evaluation, AchievementTemplate, UserAchievement, Interview, Topic
from app.services.activity_service import ActivityService
from app.services.knowledge_gap_engine import analyze_user_knowledge

DEFAULT_ACHIEVEMENTS = [
    {
        "slug": "first_explanation",
        "name": "First Explanation",
        "description": "Explained your first topic concept",
        "icon_name": "star",
        "criteria_type": "explanation_count",
        "criteria_threshold": 1,
        "points": 15
    },
    {
        "slug": "seven_day_learner",
        "name": "7 Day Learner",
        "description": "Maintained a 7-day learning streak",
        "icon_name": "zap",
        "criteria_type": "streak_days",
        "criteria_threshold": 7,
        "points": 75
    },
    {
        "slug": "fifty_concepts",
        "name": "50 Concepts",
        "description": "Learned and explained 50 distinct concepts",
        "icon_name": "book",
        "criteria_type": "concepts_count",
        "criteria_threshold": 50,
        "points": 100
    },
    {
        "slug": "knowledge_gap_hunter",
        "name": "Knowledge Gap Hunter",
        "description": "Successfully resolved a knowledge gap",
        "icon_name": "shield-check",
        "criteria_type": "resolved_gaps",
        "criteria_threshold": 1,
        "points": 50
    },
    {
        "slug": "ten_evaluations",
        "name": "10 Evaluations",
        "description": "Completed 10 total AI evaluations",
        "icon_name": "award",
        "criteria_type": "evaluation_count",
        "criteria_threshold": 10,
        "points": 50
    },
    {
        "slug": "interview_ready",
        "name": "Interview Ready",
        "description": "Completed an AI Mock Interview",
        "icon_name": "target",
        "criteria_type": "interview_count",
        "criteria_threshold": 1,
        "points": 50
    },
    {
        "slug": "perfect_score_single",
        "name": "Perfectionist",
        "description": "Scored 100% on an evaluation",
        "icon_name": "crown",
        "criteria_type": "perfect_score",
        "criteria_threshold": 1,
        "points": 50
    },
    {
        "slug": "streak_three_days",
        "name": "On Fire",
        "description": "3-day streak",
        "icon_name": "flame",
        "criteria_type": "streak_days",
        "criteria_threshold": 3,
        "points": 30
    }
]

def seed_achievements(db: Session):
    """
    Ensures all default achievement templates exist in the database.
    """
    for ach in DEFAULT_ACHIEVEMENTS:
        template = db.query(AchievementTemplate).filter(AchievementTemplate.slug == ach["slug"]).first()
        if not template:
            template = AchievementTemplate(**ach)
            db.add(template)
    db.commit()

def get_user_metrics(db: Session, user_id: int):
    """
    Calculates genuine user activity metrics for backend condition checks.
    """
    evals = db.query(Evaluation).filter(Evaluation.user_id == user_id).all()
    eval_count = len(evals)
    explanation_count = sum(1 for e in evals if e.explanation and len(e.explanation.strip()) > 0)
    
    distinct_concepts = db.query(func.count(func.distinct(Evaluation.topic_id))).filter(
        Evaluation.user_id == user_id
    ).scalar() or 0

    streak_info = ActivityService.get_streak_info(db, user_id)
    current_streak = streak_info.get("current_streak", 0)
    longest_streak = streak_info.get("longest_streak", 0)
    best_streak = max(current_streak, longest_streak)

    # Knowledge gap resolution logic
    gaps = analyze_user_knowledge(db, user_id)
    resolved_gaps = sum(1 for g in gaps if g.get("severity") == "RESOLVED" or g.get("mastery_score", 0) >= 85)

    interview_count = db.query(Interview).filter(Interview.user_id == user_id).count()

    perfect_scores = sum(1 for e in evals if (e.overall_score or e.ai_score or 0) >= 95)

    return {
        "evaluation_count": eval_count,
        "explanation_count": max(eval_count, explanation_count),
        "concepts_count": distinct_concepts,
        "streak_days": best_streak,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "resolved_gaps": resolved_gaps,
        "interview_count": interview_count,
        "perfect_score": perfect_scores
    }

def check_achievements_for_user(db: Session, user_id: int):
    """
    Evaluates backend condition rules and unlocks achievements for genuine activity.
    """
    seed_achievements(db)
    
    templates = db.query(AchievementTemplate).all()
    unlocked = {
        ua.achievement_id: ua 
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }
    
    metrics = get_user_metrics(db, user_id)
    new_unlocks = []
    
    for template in templates:
        if template.id in unlocked:
            continue
            
        unlocked_now = False
        criteria = template.criteria_type
        threshold = template.criteria_threshold or 1
        
        current_val = metrics.get(criteria, 0)
        
        if current_val >= threshold:
            unlocked_now = True

        if unlocked_now:
            ua = UserAchievement(
                user_id=user_id,
                achievement_id=template.id,
                unlocked_at=datetime.now(timezone.utc),
                notified=0
            )
            db.add(ua)
            new_unlocks.append(template)
            
    if new_unlocks:
        db.commit()

    return new_unlocks

def get_user_achievements(db: Session, user_id: int):
    """
    Returns achievements list with unlock status, progress bar values, total points, and streak info.
    """
    seed_achievements(db)
    check_achievements_for_user(db, user_id)
    
    templates = db.query(AchievementTemplate).all()
    unlocked = {
        ua.achievement_id: ua 
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }
    
    metrics = get_user_metrics(db, user_id)
    streak_info = ActivityService.get_streak_info(db, user_id)
    
    total_points = sum(t.points for t in templates if t.id in unlocked)
    
    achievements = []
    for t in templates:
        is_unlocked = t.id in unlocked
        current_val = metrics.get(t.criteria_type, 0)
        threshold = t.criteria_threshold or 1
        
        ach = {
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "description": t.description,
            "icon_name": t.icon_name,
            "points": t.points,
            "unlocked": is_unlocked,
            "criteria_type": t.criteria_type,
            "current_value": current_val if not is_unlocked else threshold,
            "target_value": threshold,
            "progress_percentage": min(100, int((current_val / threshold) * 100)) if not is_unlocked and threshold > 0 else 100
        }
        if is_unlocked:
            ach["unlocked_at"] = unlocked[t.id].unlocked_at.isoformat()
        achievements.append(ach)
        
    return {
        "total_points": total_points,
        "streak": streak_info,
        "unlocked_count": len(unlocked),
        "total_count": len(templates),
        "achievements": achievements
    }

def get_recent_unlocks(db: Session, user_id: int):
    """
    Returns newly unlocked achievements for popup notifications.
    """
    recent = db.query(UserAchievement).join(AchievementTemplate).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.notified == 0
    ).all()
    
    result = []
    for ua in recent:
        result.append({
            "id": ua.template.id,
            "name": ua.template.name,
            "icon_name": ua.template.icon_name,
            "points": ua.template.points,
            "unlocked_at": ua.unlocked_at.isoformat()
        })
        ua.notified = 1
        
    if recent:
        db.commit()
        
    return result
