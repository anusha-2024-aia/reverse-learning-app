import json
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, CommunicationAnalysis
from app.services.communication_coach_service import CommunicationCoachService

router = APIRouter(prefix="/communication")

class SingleAnalysisRequest(BaseModel):
    transcript: str
    question_text: Optional[str] = ""
    duration_seconds: Optional[float] = None
    interview_id: Optional[int] = None
    answer_id: Optional[int] = None

@router.post("/analyze")
async def analyze_communication(
    payload: SingleAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Analyzes voice transcript communication metrics and stores results. """
    if not payload.transcript or not payload.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is required for communication analysis.")

    record = await CommunicationCoachService.process_and_save_communication_analysis(
        db=db,
        user_id=current_user.id,
        transcript=payload.transcript,
        question_text=payload.question_text or "",
        interview_id=payload.interview_id,
        answer_id=payload.answer_id,
        duration_seconds=payload.duration_seconds
    )

    grammar_improvements = []
    if record.grammar_improvements_json:
        try:
            grammar_improvements = json.loads(record.grammar_improvements_json)
        except:
            pass

    filler_breakdown = {}
    if record.filler_words_json:
        try:
            filler_breakdown = json.loads(record.filler_words_json)
        except:
            pass

    return {
        "analysis_id": record.id,
        "communication_score": record.communication_score,
        "clarity_score": record.clarity_score,
        "grammar_score": record.grammar_score,
        "vocabulary_score": record.vocabulary_score,
        "structure_score": record.structure_score,
        "speaking_pace": record.speaking_pace,
        "words_per_minute": record.words_per_minute,
        "pause_count": record.pause_count,
        "filler_word_count": record.filler_word_count,
        "filler_words_breakdown": filler_breakdown,
        "grammar_feedback": record.grammar_feedback,
        "grammar_improvements": grammar_improvements,
        "vocabulary_feedback": record.vocabulary_feedback,
        "clarity_feedback": record.clarity_feedback,
        "structure_feedback": record.structure_feedback,
        "ai_coach_recommendation": record.ai_coach_recommendation
    }

@router.get("/history")
def get_communication_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Fetches past communication records for logged-in user. """
    records = db.query(CommunicationAnalysis).filter(
        CommunicationAnalysis.user_id == current_user.id
    ).order_by(CommunicationAnalysis.created_at.desc()).all()

    result = []
    for r in records:
        result.append({
            "id": r.id,
            "interview_id": r.interview_id,
            "answer_id": r.answer_id,
            "communication_score": r.communication_score,
            "clarity_score": r.clarity_score,
            "grammar_score": r.grammar_score,
            "vocabulary_score": r.vocabulary_score,
            "structure_score": r.structure_score,
            "speaking_pace": r.speaking_pace,
            "words_per_minute": r.words_per_minute,
            "filler_word_count": r.filler_word_count,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return result

@router.get("/progress")
def get_communication_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Returns communication progress metrics, line chart trend data, and Before vs. Latest comparison. """
    return CommunicationCoachService.get_communication_progress(db, current_user.id)

@router.get("/summary")
def get_communication_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Returns candidate Communication Profile and AI Coach recommendations. """
    return CommunicationCoachService.get_personalized_coach_summary(db, current_user.id)
