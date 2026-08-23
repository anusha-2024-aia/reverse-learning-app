import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.ai_service.gemini_agent import evaluate_explanation, generate_improvement_insight
from app.services import achievement_service
from app.services.adaptive_engine import AdaptiveEngine
from app.services.adaptive_learning_engine import calculate_next_recommendation
from app.services.activity_service import ActivityService
from app.services.roadmap_service import RoadmapService
from app.services.smart_revision_service import SmartRevisionService
from app.auth import get_current_user
from typing import List, Optional

router = APIRouter()


def extract_score(dim_dict):
    if isinstance(dim_dict, dict):
        val = dim_dict.get("score", 0)
    elif isinstance(dim_dict, (int, float)):
        val = dim_dict
    else:
        val = 0
    return max(0, min(100, int(val)))

def extract_feedback(dim_dict):
    if isinstance(dim_dict, dict):
        return dim_dict.get("feedback", "")
    return str(dim_dict) if dim_dict else ""

@router.post("/evaluate")
async def evaluate_user_explanation(evaluation: schemas.EvaluationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify topic exists
    topic = db.query(models.Topic).filter(models.Topic.id == evaluation.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    # Get previous attempts for attempt number & comparison
    previous_evals = db.query(models.Evaluation).filter(
        models.Evaluation.user_id == current_user.id,
        models.Evaluation.topic_id == evaluation.topic_id
    ).order_by(models.Evaluation.created_at.asc()).all()
    
    attempt_number = len(previous_evals) + 1
    
    # Get AI Evaluation
    ai_result = await evaluate_explanation(
        topic=topic.name,
        user_explanation=evaluation.explanation,
        learning_mode=evaluation.learning_mode
    )
    
    # Extract 8 dimension scores safely
    tech = extract_score(ai_result.get("technicalAccuracy"))
    concept = extract_score(ai_result.get("conceptUnderstanding"))
    comp = extract_score(ai_result.get("completeness"))
    ex = extract_score(ai_result.get("examples"))
    rel = extract_score(ai_result.get("relevance"))
    comm = extract_score(ai_result.get("communication"))
    gram = extract_score(ai_result.get("grammar"))
    vocab = extract_score(ai_result.get("vocabulary"))
    
    # Calculate deterministic overall score
    overall_score = int(round(
        tech * 0.20 +
        concept * 0.20 +
        comp * 0.10 +
        ex * 0.10 +
        rel * 0.10 +
        comm * 0.10 +
        gram * 0.10 +
        vocab * 0.10
    ))
    
    # Generate Longitudinal Improvement Insight if attempt > 1
    ai_insight = None
    improvement_points = None
    if previous_evals:
        last_eval = previous_evals[-1]
        prev_overall = last_eval.overall_score if last_eval.overall_score is not None else (last_eval.ai_score or 0)
        improvement_points = overall_score - prev_overall
        
        attempt_history = []
        for idx, prev in enumerate(previous_evals):
            attempt_history.append({
                "attempt": idx + 1,
                "overall": prev.overall_score or prev.ai_score or 0,
                "technicalAccuracy": prev.technical_score or 0,
                "conceptUnderstanding": prev.concept_score or 0,
                "completeness": prev.completeness_score or 0,
                "examples": prev.examples_score or 0,
                "relevance": prev.relevance_score or 0,
                "communication": prev.communication_score or 0,
                "grammar": prev.grammar_score or 0,
                "vocabulary": prev.vocabulary_score or 0,
            })
        attempt_history.append({
            "attempt": attempt_number,
            "overall": overall_score,
            "technicalAccuracy": tech,
            "conceptUnderstanding": concept,
            "completeness": comp,
            "examples": ex,
            "relevance": rel,
            "communication": comm,
            "grammar": gram,
            "vocabulary": vocab,
        })
        ai_insight = await generate_improvement_insight(attempt_history)
        
    explanation_length = len(evaluation.explanation.split())
    strengths = ai_result.get("strengths", [])
    weaknesses = ai_result.get("weaknesses", [])
    knowledge_gaps = ai_result.get("knowledgeGaps", [])
    
    # Save to database
    db_evaluation = models.Evaluation(
        user_id=current_user.id,
        topic_id=evaluation.topic_id,
        explanation=evaluation.explanation,
        ai_score=overall_score, # maintain backwards compatibility
        overall_score=overall_score,
        technical_score=tech,
        concept_score=concept,
        completeness_score=comp,
        examples_score=ex,
        relevance_score=rel,
        communication_score=comm,
        grammar_score=gram,
        vocabulary_score=vocab,
        attempt_number=attempt_number,
        ai_insight=ai_insight,
        ai_feedback_json=json.dumps(ai_result),
        explanation_length=explanation_length,
        strengths_count=len(strengths),
        weaknesses_count=len(weaknesses)
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    # Update mastery score via Adaptive Engine & recalculate recommendation
    AdaptiveEngine.update_mastery(db, current_user.id, evaluation.topic_id, overall_score)
    
    # Update Smart Revision Scheduler
    try:
        SmartRevisionService.update_revision_schedule(db, current_user.id, evaluation.topic_id, overall_score)
    except Exception as rev_err:
        print(f"SmartRevisionService update error: {rev_err}")

    next_rec = calculate_next_recommendation(db, current_user.id)

    
    # Recalculate Dynamic Personalized Roadmap
    try:
        RoadmapService.recalculate_roadmap(db, current_user.id)
    except Exception as r_err:
        print(f"Roadmap recalculation after eval error: {r_err}")
    
    # Log activity for streak
    ActivityService.log_activity(db, current_user.id, "evaluation")
    
    # Check for newly unlocked achievements
    achievement_service.check_achievements_for_user(db, current_user.id)
    
    # Structured response
    dimensions = {
        "technicalAccuracy": {"score": tech, "feedback": extract_feedback(ai_result.get("technicalAccuracy"))},
        "conceptUnderstanding": {"score": concept, "feedback": extract_feedback(ai_result.get("conceptUnderstanding"))},
        "completeness": {"score": comp, "feedback": extract_feedback(ai_result.get("completeness"))},
        "examples": {"score": ex, "feedback": extract_feedback(ai_result.get("examples"))},
        "relevance": {"score": rel, "feedback": extract_feedback(ai_result.get("relevance"))},
        "communication": {"score": comm, "feedback": extract_feedback(ai_result.get("communication"))},
        "grammar": {"score": gram, "feedback": extract_feedback(ai_result.get("grammar"))},
        "vocabulary": {"score": vocab, "feedback": extract_feedback(ai_result.get("vocabulary"))}
    }
    
    return {
        "evaluation_id": db_evaluation.id,
        "overall_score": overall_score,
        "score": overall_score, # backwards compatibility
        "attempt_number": attempt_number,
        "improvement_points": improvement_points,
        "ai_insight": ai_insight,
        "dimensions": dimensions,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "knowledge_gaps": knowledge_gaps,
        "summary": ai_result.get("summary", ""),
        "correct_version": ai_result.get("correct_version", ""),
        "follow_up_question": ai_result.get("follow_up_question", ""),
        "learning_suggestions": ai_result.get("learning_suggestions", []),
        "next_recommendation": {
            "topic_id": next_rec.topic_id,
            "topic_name": next_rec.topic.name if next_rec.topic else "Next Topic",
            "action_type": next_rec.action_type,
            "reason": next_rec.reason,
            "target_concept": next_rec.target_concept,
            "difficulty": next_rec.difficulty
        } if next_rec else None
    }

@router.get("/evaluations/mine")
def get_my_evaluations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    evals = db.query(models.Evaluation, models.Topic, models.Curriculum).join(
        models.Topic, models.Evaluation.topic_id == models.Topic.id
    ).join(
        models.Curriculum, models.Topic.curriculum_id == models.Curriculum.id
    ).filter(models.Evaluation.user_id == current_user.id).order_by(models.Evaluation.created_at.desc()).all()
    
    result = []
    for e, t, c in evals:
        result.append({
            "id": e.id,
            "topic_id": e.topic_id,
            "topic_name": t.name,
            "curriculum_name": c.name,
            "overall_score": e.overall_score or e.ai_score,
            "attempt_number": e.attempt_number or 1,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "ai_feedback_json": e.ai_feedback_json
        })
    return result

@router.get("/evaluations/topic/{topic_id}")
def get_topic_evaluation_history(topic_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    evals = db.query(models.Evaluation).filter(
        models.Evaluation.user_id == current_user.id,
        models.Evaluation.topic_id == topic_id
    ).order_by(models.Evaluation.created_at.asc()).all()
    
    history = []
    for idx, e in enumerate(evals):
        history.append({
            "attempt": idx + 1,
            "id": e.id,
            "overall_score": e.overall_score or e.ai_score or 0,
            "technical_score": e.technical_score or 0,
            "concept_score": e.concept_score or 0,
            "completeness_score": e.completeness_score or 0,
            "examples_score": e.examples_score or 0,
            "relevance_score": e.relevance_score or 0,
            "communication_score": e.communication_score or 0,
            "grammar_score": e.grammar_score or 0,
            "vocabulary_score": e.vocabulary_score or 0,
            "ai_insight": e.ai_insight,
            "created_at": e.created_at.isoformat() if e.created_at else None
        })
        
    first_score = history[0]["overall_score"] if history else 0
    latest_score = history[-1]["overall_score"] if history else 0
    total_improvement = latest_score - first_score
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "total_attempts": len(history),
        "first_score": first_score,
        "latest_score": latest_score,
        "total_improvement": total_improvement,
        "history": history
    }

