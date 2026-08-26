from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, literal
from app.models import User, Evaluation, Interview, Topic, LearningActivity
from app.services import insights_service, knowledge_gap_engine

def calculate_technical_mastery(db: Session, user_id: int):
    # Avg of evaluation AI scores and interview technical scores
    eval_avg = db.query(func.avg(Evaluation.ai_score)).filter(Evaluation.user_id == user_id, Evaluation.ai_score != None).scalar() or 0
    int_avg = db.query(func.avg(Interview.technical_score)).filter(Interview.user_id == user_id, Interview.technical_score != None).scalar() or 0
    
    if eval_avg > 0 and int_avg > 0:
        return round((eval_avg * 0.7) + (int_avg * 0.3))
    elif eval_avg > 0:
        return round(eval_avg)
    return round(int_avg)

def calculate_communication_score(db: Session, user_id: int):
    eval_avg = db.query(func.avg(Evaluation.communication_score)).filter(Evaluation.user_id == user_id, Evaluation.communication_score != None).scalar() or 0
    int_avg = db.query(func.avg(Interview.communication_score)).filter(Interview.user_id == user_id, Interview.communication_score != None).scalar() or 0
    
    if eval_avg > 0 and int_avg > 0:
        return round((eval_avg * 0.6) + (int_avg * 0.4))
    elif eval_avg > 0:
        return round(eval_avg)
    return round(int_avg)

def calculate_interview_readiness(db: Session, user_id: int):
    int_avg = db.query(func.avg(Interview.overall_score)).filter(Interview.user_id == user_id, Interview.overall_score != None).scalar() or 0
    return round(int_avg)

def calculate_learning_consistency(db: Session, user_id: int):
    streak = insights_service.calculate_streak(db, user_id)
    # Map streak to a 0-100 score. E.g. 14 days = 100%
    return min(100, round((streak / 14) * 100))

def get_recent_activity(db: Session, user_id: int, limit: int = 5):
    # Combine Evaluations and Interviews
    evals = db.query(
        Evaluation.id,
        Evaluation.created_at,
        Evaluation.ai_score.label('score'),
        Topic.name.label('title'),
        literal('evaluation').label('type')
    ).join(Topic, Topic.id == Evaluation.topic_id).filter(Evaluation.user_id == user_id).order_by(desc(Evaluation.created_at)).limit(limit).all()
    
    ints = db.query(
        Interview.id,
        Interview.created_at,
        Interview.overall_score.label('score'),
        Interview.target_role.label('title'),
        literal('interview').label('type')
    ).filter(Interview.user_id == user_id).order_by(desc(Interview.created_at)).limit(limit).all()
    
    activity = []
    for e in evals:
        activity.append({
            "id": e.id,
            "type": "evaluation",
            "title": f"Practiced {e.title}",
            "score": e.score,
            "date": e.created_at.isoformat()
        })
        
    for i in ints:
        activity.append({
            "id": i.id,
            "type": "interview",
            "title": f"Mock Interview: {i.title}",
            "score": i.score,
            "date": i.created_at.isoformat()
        })
        
    activity.sort(key=lambda x: x["date"], reverse=True)
    return activity[:limit]

import json
from app.models import User, Evaluation, Interview, Topic, LearningActivity, Resume, ResumeQuestion, ResumeInterview

def get_resume_summary(db: Session, user_id: int):
    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == True
    ).order_by(Resume.created_at.desc()).first()

    if not resume:
        return {
            "has_resume": False,
            "file_name": None,
            "projects_count": 0,
            "skills_count": 0,
            "questions_count": 0,
            "last_interview_score": None,
            "recommended_prep": None
        }

    projects = json.loads(resume.parsed_projects or "[]")
    skills = json.loads(resume.parsed_skills or "[]")

    questions_count = db.query(ResumeQuestion).filter(
        ResumeQuestion.resume_id == resume.id,
        ResumeQuestion.user_id == user_id
    ).count()

    last_interview = db.query(ResumeInterview).filter(
        ResumeInterview.user_id == user_id,
        ResumeInterview.resume_id == resume.id
    ).order_by(ResumeInterview.created_at.desc()).first()

    last_score = last_interview.overall_score if last_interview else None
    rec_prep = None
    if last_interview and last_interview.feedback_json:
        try:
            fb = json.loads(last_interview.feedback_json)
            preps = fb.get("recommended_preparation", [])
            if preps:
                rec_prep = preps[0]
        except:
            pass

    if not rec_prep and resume.analysis_summary_json:
        try:
            sum_data = json.loads(resume.analysis_summary_json)
            rec_focus = sum_data.get("recommended_focus", [])
            if rec_focus:
                rec_prep = rec_focus[0]
        except:
            pass

    return {
        "has_resume": True,
        "file_name": resume.file_name,
        "projects_count": len(projects),
        "skills_count": len(skills),
        "questions_count": questions_count,
        "last_interview_score": last_score,
        "recommended_prep": rec_prep or "Database Design"
    }

def generate_dashboard_data(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    
    technical = calculate_technical_mastery(db, user_id)
    communication = calculate_communication_score(db, user_id)
    interview = calculate_interview_readiness(db, user_id)
    consistency = calculate_learning_consistency(db, user_id)
    streak = insights_service.calculate_streak(db, user_id)
    
    # Calculate Overall
    total_weights = 0
    overall = 0
    if technical > 0:
        overall += technical * 0.40
        total_weights += 0.40
    if communication > 0:
        overall += communication * 0.20
        total_weights += 0.20
    if interview > 0:
        overall += interview * 0.30
        total_weights += 0.30
    overall += consistency * 0.10
    total_weights += 0.10
    
    overall = round(overall / total_weights) if total_weights > 0 else 0
    
    # Get existing logic for other parts
    strong_topics = insights_service.get_strong_topics(db, user_id, 3).get("strong_topics", [])
    weak_topics = insights_service.get_weak_topics(db, user_id, 3).get("weak_topics", [])
    progress = insights_service.calculate_score_trend(db, user_id, 30).get("trend", [])
    ai_insight = insights_service.get_ai_insight(db, user_id).get("insight", "")
    recent = get_recent_activity(db, user_id)
    
    # Next Action
    next_action_data = knowledge_gap_engine.get_next_best_action(db, user_id)
    
    # Roadmap Summary
    roadmap_info = None
    try:
        from app.services.roadmap_service import RoadmapService
        roadmap_info = RoadmapService.get_my_roadmap(db, user_id)
    except Exception as rm_err:
        print(f"Dashboard roadmap info error: {rm_err}")
    
    return {
        "user": {
            "name": (user.name or user.username) if user else "Student",
            "target_role": user.target_role if user else None,
            "onboarding_completed": bool(user.onboarding_completed) if user else False
        },
        "summary": {
            "overallScore": overall,
            "technicalMastery": technical,
            "communicationScore": communication,
            "interviewReadiness": interview,
            "learningConsistency": consistency,
            "streak": streak
        },
        "strongestTopics": strong_topics,
        "weakestTopics": weak_topics,
        "progress": progress,
        "recentActivity": recent,
        "aiInsight": {
            "text": ai_insight
        },
        "recommendedAction": next_action_data,
        "roadmapSummary": {
            "target_role": roadmap_info.get("target_role") if roadmap_info else (user.target_role if user else "Full Stack Developer"),
            "progress": roadmap_info.get("progress", 0.0) if roadmap_info else 0.0,
            "estimated_hours": roadmap_info.get("estimated_hours", 0) if roadmap_info else 0,
            "estimated_days": roadmap_info.get("estimated_days", 0) if roadmap_info else 0,
            "current_focus": roadmap_info.get("current_focus") if roadmap_info else None,
            "latest_change": roadmap_info.get("history", [{}])[0] if roadmap_info and roadmap_info.get("history") else None
        } if roadmap_info and roadmap_info.get("roadmap_id") else None,
        "revisionSummary": (lambda: __import__('app.services.smart_revision_service', fromlist=['SmartRevisionService']).SmartRevisionService.get_user_revisions(db, user_id))(),
        "resumeSummary": get_resume_summary(db, user_id)
    }


