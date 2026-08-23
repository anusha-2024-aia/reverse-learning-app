from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.models import Evaluation, Topic
import statistics

def calculate_consistency(scores):
    if len(scores) < 2:
        return 100 # Perfectly consistent if only one score
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
    # Map std dev to 0-100 scale inversely. High std dev (e.g. 40) = low consistency (20)
    consistency = max(0, 100 - (std_dev * 2))
    return consistency

def calculate_improvement(scores):
    if len(scores) < 2:
        return 50 # Neutral if no history to compare
    first = scores[0]
    last = scores[-1]
    diff = last - first
    # Map diff (-100 to 100) to a 0-100 scale, where 0 diff = 50
    improvement = max(0, min(100, 50 + diff))
    return improvement

def determine_severity_and_trend(mastery, scores):
    # Trend
    if len(scores) < 2:
        trend = "STABLE"
    else:
        recent_avg = sum(scores[-2:]) / len(scores[-2:])
        old_avg = sum(scores[:-2]) / max(1, len(scores[:-2])) if len(scores) > 2 else scores[0]
        
        if recent_avg > old_avg + 5:
            trend = "IMPROVING"
        elif recent_avg < old_avg - 5:
            trend = "DECLINING"
        else:
            trend = "STABLE"

    # Severity
    if mastery < 55:
        if trend == "DECLINING":
            severity = "CRITICAL"
        else:
            severity = "HIGH"
    elif mastery < 70:
        severity = "MEDIUM"
    elif mastery < 85:
        severity = "LOW"
    else:
        severity = "RESOLVED"
        
    return severity, trend

def generate_recommendation(severity, trend, topic_name):
    if severity == "CRITICAL":
        return f"URGENT: Review {topic_name} fundamentals immediately. Focus on core concepts before practicing."
    elif severity == "HIGH":
        return f"Review {topic_name} and complete 3 beginner problems to solidify your understanding."
    elif severity == "MEDIUM":
        return f"Practice intermediate {topic_name} problems to fix minor knowledge gaps."
    elif severity == "LOW":
        if trend == "DECLINING":
            return f"Your {topic_name} score is slipping. Do a quick revision session."
        return f"Solidify your {topic_name} knowledge with advanced problems."
    else:
        return f"Excellent mastery of {topic_name}! Ready for complex interviews."

def analyze_user_knowledge(db: Session, user_id: int):
    # Get all evaluations for user, grouped by topic
    topics = db.query(Topic).join(Evaluation).filter(Evaluation.user_id == user_id, Evaluation.ai_score != None).distinct().all()
    
    gaps = []
    for topic in topics:
        evals = db.query(Evaluation).filter(
            Evaluation.user_id == user_id, 
            Evaluation.topic_id == topic.id,
            Evaluation.ai_score != None
        ).order_by(asc(Evaluation.created_at)).all()
        
        if not evals:
            continue
            
        scores = [e.ai_score for e in evals]
        recent = scores[-1]
        average = sum(scores) / len(scores)
        consistency = calculate_consistency(scores)
        improvement = calculate_improvement(scores)
        
        # Mastery Formula
        mastery = (recent * 0.45) + (average * 0.30) + (consistency * 0.15) + (improvement * 0.10)
        mastery = round(mastery)
        
        severity, trend = determine_severity_and_trend(mastery, scores)
        recommendation = generate_recommendation(severity, trend, topic.name)
        
        gaps.append({
            "topic_id": topic.id,
            "topic_name": topic.name,
            "mastery_score": mastery,
            "recent_score": recent,
            "average_score": round(average),
            "attempts": len(scores),
            "severity": severity,
            "trend": trend,
            "recommendation": recommendation
        })
    
    # Sort by severity (CRITICAL first, then HIGH, etc)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "RESOLVED": 4}
    gaps.sort(key=lambda x: severity_order.get(x["severity"], 5))
    
    return gaps

def get_next_best_action(db: Session, user_id: int):
    gaps = analyze_user_knowledge(db, user_id)
    if not gaps:
        return None
    return gaps[0]
