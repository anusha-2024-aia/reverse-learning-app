from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta, timezone
from app.models import Evaluation, Topic, Curriculum
import json

def calculate_streak(db: Session, user_id: int):
    evals = db.query(func.date(Evaluation.created_at)).filter(
        Evaluation.user_id == user_id
    ).distinct().order_by(desc(func.date(Evaluation.created_at))).all()
    
    if not evals:
        return 0
        
    streak = 0
    current_date = datetime.now(timezone.utc).date()
    
    # Check if they evaluated today or yesterday
    last_eval_date = datetime.strptime(evals[0][0], "%Y-%m-%d").date()
    if (current_date - last_eval_date).days > 1:
        return 0
        
    check_date = last_eval_date
    for eval_date_str in evals:
        eval_date = datetime.strptime(eval_date_str[0], "%Y-%m-%d").date()
        if eval_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
            
    return streak

def get_summary_stats(db: Session, user_id: int):
    total_evals = db.query(Evaluation).filter(Evaluation.user_id == user_id).count()
    if total_evals == 0:
        return {
            "total_evaluations": 0, "average_score": 0, "total_sessions": 0,
            "days_active": 0, "current_streak": 0, "best_score": 0, "worst_score": 0,
            "most_studied_curriculum": None, "most_studied_topic": None
        }
        
    avg_score = db.query(func.avg(Evaluation.ai_score)).filter(
        Evaluation.user_id == user_id, Evaluation.ai_score != None
    ).scalar() or 0
    
    days_active = db.query(func.count(func.distinct(func.date(Evaluation.created_at)))).filter(
        Evaluation.user_id == user_id
    ).scalar() or 0
    
    best_score = db.query(func.max(Evaluation.ai_score)).filter(Evaluation.user_id == user_id).scalar() or 0
    worst_score = db.query(func.min(Evaluation.ai_score)).filter(Evaluation.user_id == user_id, Evaluation.ai_score != None).scalar() or 0
    
    # Most studied topic
    most_topic = db.query(Topic.name, func.count(Evaluation.id).label('count')).join(
        Evaluation, Topic.id == Evaluation.topic_id
    ).filter(Evaluation.user_id == user_id).group_by(Topic.name).order_by(desc('count')).first()
    
    # Most studied curriculum
    most_curr = db.query(Curriculum.name, func.count(Evaluation.id).label('count')).join(
        Topic, Curriculum.id == Topic.curriculum_id
    ).join(
        Evaluation, Topic.id == Evaluation.topic_id
    ).filter(Evaluation.user_id == user_id).group_by(Curriculum.name).order_by(desc('count')).first()
    
    return {
        "total_evaluations": total_evals,
        "average_score": round(avg_score, 1),
        "total_sessions": total_evals, # Simplifying sessions as evals for now
        "days_active": days_active,
        "current_streak": calculate_streak(db, user_id),
        "best_score": best_score,
        "worst_score": worst_score,
        "most_studied_curriculum": most_curr[0] if most_curr else None,
        "most_studied_topic": most_topic[0] if most_topic else None
    }

def calculate_score_trend(db: Session, user_id: int, days: int = 7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    daily_stats = db.query(
        func.date(Evaluation.created_at).label('date'),
        func.avg(Evaluation.ai_score).label('avg_score'),
        func.count(Evaluation.id).label('count')
    ).filter(
        Evaluation.user_id == user_id,
        Evaluation.created_at >= cutoff,
        Evaluation.ai_score != None
    ).group_by('date').order_by('date').all()
    
    trend_data = [{"date": stat.date, "average_score": round(stat.avg_score, 1), "count": stat.count} for stat in daily_stats]
    
    overall_trend = "stable"
    if len(trend_data) > 1:
        first_half_avg = sum(d["average_score"] for d in trend_data[:len(trend_data)//2]) / (len(trend_data)//2)
        second_half_avg = sum(d["average_score"] for d in trend_data[len(trend_data)//2:]) / (len(trend_data) - len(trend_data)//2)
        if second_half_avg > first_half_avg + 0.5:
            overall_trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            overall_trend = "declining"
            
    return {"trend": trend_data, "overall_trend": overall_trend}

def get_weak_topics(db: Session, user_id: int, limit: int = 5):
    weak = db.query(
        Topic.id.label('topic_id'),
        Topic.name.label('topic_name'),
        func.avg(Evaluation.ai_score).label('avg_score'),
        func.count(Evaluation.id).label('attempts'),
        func.max(Evaluation.ai_score).label('best_score')
    ).join(
        Evaluation, Topic.id == Evaluation.topic_id
    ).filter(
        Evaluation.user_id == user_id,
        Evaluation.ai_score != None
    ).group_by(Topic.id, Topic.name).order_by(asc('avg_score')).limit(limit).all()
    
    return {"weak_topics": [{"topic_id": w.topic_id, "topic_name": w.topic_name, "avg_score": round(w.avg_score, 1), "attempts": w.attempts, "best_score": w.best_score} for w in weak]}

def get_most_improved_topics(db: Session, user_id: int, limit: int = 5):
    # This requires looking at first attempt vs latest attempt.
    # We will do this mostly in Python since SQL for first/last in SQLite is tricky.
    topics = db.query(Topic).join(Evaluation).filter(Evaluation.user_id == user_id).distinct().all()
    
    improvements = []
    for t in topics:
        evals = db.query(Evaluation).filter(
            Evaluation.topic_id == t.id, 
            Evaluation.user_id == user_id,
            Evaluation.ai_score != None
        ).order_by(Evaluation.created_at).all()
        
        if len(evals) >= 2:
            first = evals[0].ai_score
            latest = evals[-1].ai_score
            diff = latest - first
            if diff > 0:
                improvements.append({
                    "topic_id": t.id,
                    "topic_name": t.name,
                    "first_score": first,
                    "latest_score": latest,
                    "improvement": diff,
                    "attempts": len(evals)
                })
                
    improvements.sort(key=lambda x: x["improvement"], reverse=True)
    return {"improved_topics": improvements[:limit]}

def get_most_attempted_topics(db: Session, user_id: int, limit: int = 5):
    most = db.query(
        Topic.id.label('topic_id'),
        Topic.name.label('topic_name'),
        func.count(Evaluation.id).label('attempts'),
        func.avg(Evaluation.ai_score).label('avg_score')
    ).join(
        Evaluation, Topic.id == Evaluation.topic_id
    ).filter(
        Evaluation.user_id == user_id
    ).group_by(Topic.id, Topic.name).order_by(desc('attempts')).limit(limit).all()
    
    return {"most_attempted": [{"topic_id": m.topic_id, "topic_name": m.topic_name, "attempts": m.attempts, "average_score": round(m.avg_score or 0, 1)} for m in most]}

def get_grammar_trend(db: Session, user_id: int, days: int = 30):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    evals = db.query(Evaluation).filter(
        Evaluation.user_id == user_id,
        Evaluation.created_at >= cutoff
    ).order_by(Evaluation.created_at).all()
    
    daily_stats = {}
    for e in evals:
        date_str = e.created_at.date().isoformat()
        if date_str not in daily_stats:
            daily_stats[date_str] = {"total": 0, "error_free": 0}
        
        daily_stats[date_str]["total"] += 1
        
        try:
            issues = json.loads(e.grammar_issues) if e.grammar_issues else []
            if len(issues) == 0:
                daily_stats[date_str]["error_free"] += 1
        except:
            pass # ignore parse errors
            
    trend_data = []
    for date_str, stats in daily_stats.items():
        pct = (stats["error_free"] / stats["total"]) * 100
        trend_data.append({"date": date_str, "error_free_percentage": round(pct)})
        
    trend_data.sort(key=lambda x: x["date"])
    
    current_pct = trend_data[-1]["error_free_percentage"] if trend_data else 0
    
    trend = "stable"
    if len(trend_data) > 1:
        if trend_data[-1]["error_free_percentage"] > trend_data[0]["error_free_percentage"] + 10:
            trend = "improving"
        elif trend_data[-1]["error_free_percentage"] < trend_data[0]["error_free_percentage"] - 10:
            trend = "declining"
            
    return {
        "grammar_score_over_time": trend_data,
        "current_error_free_percentage": current_pct,
        "trend": trend
    }

def get_curriculum_stats(db: Session, user_id: int):
    curricula = db.query(Curriculum).all()
    result = []
    
    for c in curricula:
        topics = db.query(Topic).filter(Topic.curriculum_id == c.id).all()
        total_topics = len(topics)
        
        completed_topics = 0
        topic_scores = []
        last_studied = None
        
        for t in topics:
            evals = db.query(Evaluation).filter(
                Evaluation.topic_id == t.id, 
                Evaluation.user_id == user_id
            ).all()
            
            if evals:
                completed_topics += 1
                topic_scores.extend([e.ai_score for e in evals if e.ai_score is not None])
                
                latest_eval = max([e.created_at for e in evals])
                if not last_studied or latest_eval > last_studied:
                    last_studied = latest_eval
                    
        avg_score = sum(topic_scores) / len(topic_scores) if topic_scores else 0
        
        if completed_topics > 0: # Only include if they started it
            result.append({
                "curriculum_id": c.id,
                "curriculum_name": c.name,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "average_score": round(avg_score, 1),
                "last_studied": last_studied.date().isoformat() if last_studied else None
            })
            
    return {"curriculums": result}
