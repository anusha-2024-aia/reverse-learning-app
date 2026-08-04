from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import json
from app.models import Evaluation, AchievementTemplate, UserAchievement
from app.services import insights_service

def check_achievements_for_user(db: Session, user_id: int):
    templates = db.query(AchievementTemplate).all()
    unlocked = {
        ua.achievement_id: ua 
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }
    
    new_unlocks = []
    
    evals = db.query(Evaluation).filter(Evaluation.user_id == user_id).all()
    eval_count = len(evals)
    
    for template in templates:
        if template.id in unlocked:
            continue
            
        unlocked_now = False
        
        if template.criteria_type == "evaluation_count":
            if eval_count >= template.criteria_threshold:
                unlocked_now = True
                
        elif template.criteria_type == "perfect_score":
            perfects = sum(1 for e in evals if e.score == 10)
            if perfects >= template.criteria_threshold:
                unlocked_now = True
                
        elif template.criteria_type == "streak_days":
            streak = insights_service.calculate_streak(db, user_id)
            if streak >= template.criteria_threshold:
                unlocked_now = True
                
        elif template.criteria_type == "grammar_perfect":
            error_free = 0
            for e in evals:
                try:
                    issues = json.loads(e.grammar_issues) if e.grammar_issues else []
                    if len(issues) == 0:
                        error_free += 1
                except:
                    pass
            if error_free >= template.criteria_threshold:
                unlocked_now = True
                
        elif template.criteria_type == "topic_perfect":
            if any(e.score == 10 for e in evals):
                unlocked_now = True
                
        elif template.criteria_type == "midnight_eval":
            if any(e.created_at.hour >= 23 or e.created_at.hour < 4 for e in evals):
                unlocked_now = True
                
        elif template.criteria_type == "weekend_eval":
            if any(e.created_at.weekday() >= 5 for e in evals):
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

def get_user_achievements(db: Session, user_id: int):
    templates = db.query(AchievementTemplate).all()
    unlocked = {
        ua.achievement_id: ua 
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }
    
    total_points = sum(t.points for t in templates if t.id in unlocked)
    
    achievements = []
    for t in templates:
        is_unlocked = t.id in unlocked
        ach = {
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "description": t.description,
            "icon_name": t.icon_name,
            "points": t.points,
            "unlocked": is_unlocked
        }
        if is_unlocked:
            ach["unlocked_at"] = unlocked[t.id].unlocked_at.isoformat()
        achievements.append(ach)
        
    return {
        "total_points": total_points,
        "achievements": achievements
    }

def get_recent_unlocks(db: Session, user_id: int):
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
