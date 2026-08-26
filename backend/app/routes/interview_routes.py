import json
import os
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Interview, InterviewQuestion, InterviewAnswer, Resume
from app.services.resume_parser import ResumeParser
from app.services.activity_service import ActivityService
from app.services.adaptive_interview_service import AdaptiveInterviewService
from app.services.communication_coach_service import CommunicationCoachService

router = APIRouter(prefix="/interview")

class StartSessionRequest(BaseModel):
    target_role: Optional[str] = "Software Engineer"
    interview_type: Optional[str] = "technical"
    difficulty: Optional[str] = "MEDIUM"
    question_count: Optional[int] = 10
    use_resume: Optional[bool] = False
    resume_id: Optional[int] = None

class AnswerQuestionRequest(BaseModel):
    interview_id: int
    current_question_id: Optional[int] = None
    answer: str
    is_final: Optional[bool] = False

import uuid
MAX_RESUME_SIZE = 10 * 1024 * 1024 # 10MB

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Uploads and parses a resume. """
    raw_filename = os.path.basename(file.filename or "resume.pdf")
    ext = os.path.splitext(raw_filename)[1].lower().replace('.', '')

    if ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")

    content = await file.read()
    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit (10 MB).")

    if len(content) < 50:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or corrupted.")

    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    clean_name = "".join(c for c in raw_filename if c.isalnum() or c in "._-")
    temp_path = os.path.abspath(os.path.join(upload_dir, f"user_{current_user.id}_{uuid.uuid4().hex}_{clean_name}"))

    try:
        with open(temp_path, "wb") as f:
            f.write(content)
            
        parsed_data = await ResumeParser.parse_resume(temp_path)
        if not parsed_data:
            raise HTTPException(status_code=400, detail="Failed to parse resume.")
            
        resume = Resume(
            user_id=current_user.id,
            file_path=temp_path,
            parsed_skills=json.dumps(parsed_data.get("skills", [])),
            parsed_projects=json.dumps(parsed_data.get("projects", [])),
            parsed_experience=json.dumps(parsed_data.get("experience", []))
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return {"message": "Resume uploaded successfully.", "resume_id": resume.id, "parsed_data": parsed_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to process uploaded resume file.")

@router.post("/start")
async def start_interview(
    payload: Optional[dict] = Body(None),
    target_role: Optional[str] = None,
    difficulty: Optional[str] = None,
    interview_type: Optional[str] = None,
    question_count: Optional[int] = None,
    resume_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """ Starts a new personalized AI Adaptive Mock Interview. """
    data = payload or {}
    
    role = data.get("target_role") or target_role or current_user.target_role or "Software Engineer"
    itype = data.get("interview_type") or interview_type or "technical"
    diff = (data.get("difficulty") or difficulty or "MEDIUM").upper()
    q_count = int(data.get("question_count") or question_count or 10)
    res_id = data.get("resume_id") or resume_id

    if data.get("use_resume") and not res_id:
        active_resume = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        ).order_by(Resume.created_at.desc()).first()
        if active_resume:
            res_id = active_resume.id

    # Mark older IN_PROGRESS interviews as ABANDONED
    db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "IN_PROGRESS"
    ).update({"status": "ABANDONED"})
    db.commit()

    interview = Interview(
        user_id=current_user.id,
        resume_id=res_id,
        target_role=role,
        interview_type=itype,
        difficulty=diff,
        starting_difficulty=diff,
        current_difficulty=diff,
        question_count=q_count,
        current_question_number=1,
        status="IN_PROGRESS"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Generate first adaptive question
    first_q_data = await AdaptiveInterviewService.generate_adaptive_question(
        db=db,
        user_id=current_user.id,
        interview=interview,
        last_qa=None
    )

    q = InterviewQuestion(
        interview_id=interview.id,
        question_number=1,
        question_text=first_q_data["question"],
        category=first_q_data["category"],
        difficulty=first_q_data["difficulty"],
        is_followup=first_q_data["is_followup"],
        topic=first_q_data["topic"],
        source=first_q_data["source"]
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    return {
        "interview_id": interview.id,
        "question_id": q.id,
        "question": q.question_text,
        "category": q.category,
        "difficulty": q.difficulty,
        "topic": q.topic,
        "source": q.source,
        "current_step": 1,
        "total_questions": interview.question_count,
        "status": interview.status
    }

@router.post("/answer")
async def process_answer(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Processes candidate answer, evaluates performance, dynamically scales difficulty, and generates next question or report. """
    interview_id = payload.get("interview_id")
    current_question_id = payload.get("current_question_id")
    answer_text = payload.get("answer", "").strip()
    is_final_flag = payload.get("is_final", False)

    if not interview_id or not answer_text:
        raise HTTPException(status_code=400, detail="Invalid request payload. Interview ID and answer are required.")

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found or access denied.")

    # Find target question
    if current_question_id:
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == current_question_id,
            InterviewQuestion.interview_id == interview.id
        ).first()
    else:
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview.id
        ).order_by(InterviewQuestion.question_number.desc()).first()

    if not question:
        raise HTTPException(status_code=404, detail="Interview question not found.")

    # Multi-dimensional evaluation of single answer
    eval_result = await AdaptiveInterviewService.evaluate_single_answer(
        topic=question.topic or interview.target_role,
        question=question.question_text,
        answer=answer_text
    )

    # Save answer to DB
    existing_ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).first()
    if existing_ans:
        ans_record = existing_ans
        ans_record.answer_text = answer_text
        ans_record.technical_score = eval_result["technical_score"]
        ans_record.communication_score = eval_result["communication_score"]
        ans_record.completeness_score = eval_result["completeness_score"]
        ans_record.relevance_score = eval_result["relevance_score"]
        ans_record.overall_score = eval_result["overall_score"]
        ans_record.ai_score = eval_result["overall_score"]
        ans_record.feedback = eval_result["feedback"]
    else:
        ans_record = InterviewAnswer(
            question_id=question.id,
            answer_text=answer_text,
            technical_score=eval_result["technical_score"],
            communication_score=eval_result["communication_score"],
            completeness_score=eval_result["completeness_score"],
            relevance_score=eval_result["relevance_score"],
            overall_score=eval_result["overall_score"],
            ai_score=eval_result["overall_score"],
            feedback=eval_result["feedback"]
        )
        db.add(ans_record)
    
    db.commit()

    # Phase 10: AI Communication Coach Analysis
    duration_secs = payload.get("audio_duration_seconds") or payload.get("duration_seconds")
    comm_record = await CommunicationCoachService.process_and_save_communication_analysis(
        db=db,
        user_id=current_user.id,
        transcript=answer_text,
        question_text=question.question_text,
        interview_id=interview.id,
        answer_id=ans_record.id,
        duration_seconds=duration_secs
    )

    grammar_imps = []
    if comm_record.grammar_improvements_json:
        try:
            grammar_imps = json.loads(comm_record.grammar_improvements_json)
        except:
            pass

    filler_brk = {}
    if comm_record.filler_words_json:
        try:
            filler_brk = json.loads(comm_record.filler_words_json)
        except:
            pass

    comm_payload = {
        "communication_score": comm_record.communication_score,
        "clarity_score": comm_record.clarity_score,
        "grammar_score": comm_record.grammar_score,
        "vocabulary_score": comm_record.vocabulary_score,
        "structure_score": comm_record.structure_score,
        "speaking_pace": comm_record.speaking_pace,
        "words_per_minute": comm_record.words_per_minute,
        "pause_count": comm_record.pause_count,
        "filler_word_count": comm_record.filler_word_count,
        "filler_words": filler_brk,
        "grammar_feedback": comm_record.grammar_feedback,
        "grammar_improvements": grammar_imps,
        "vocabulary_feedback": comm_record.vocabulary_feedback,
        "clarity_feedback": comm_record.clarity_feedback,
        "structure_feedback": comm_record.structure_feedback,
        "ai_coach_recommendation": comm_record.ai_coach_recommendation
    }

    # Deterministic difficulty transition calculation (based on technical evaluation)
    old_diff = (interview.current_difficulty or "MEDIUM").upper()
    score = eval_result["overall_score"]
    next_diff = AdaptiveInterviewService.calculate_next_difficulty(old_diff, score)
    interview.current_difficulty = next_diff
    db.commit()

    diff_status = "MAINTAINED"
    if next_diff != old_diff:
        diff_status = "INCREASED" if score >= 80 else "DECREASED"

    # Check completion
    is_complete = is_final_flag or (interview.current_question_number >= interview.question_count)

    if is_complete:
        report = await AdaptiveInterviewService.evaluate_full_interview(
            db=db,
            user_id=current_user.id,
            interview_id=interview.id
        )
        return {
            "is_complete": True,
            "eval_result": eval_result,
            "communication_analysis": comm_payload,
            "difficulty_change": diff_status,
            "old_difficulty": old_diff,
            "new_difficulty": next_diff,
            "report": report
        }
    else:
        interview.current_question_number += 1
        db.commit()

        # Generate next question
        last_qa_payload = {
            "question": question.question_text,
            "answer": answer_text,
            "score": score
        }
        next_q_data = await AdaptiveInterviewService.generate_adaptive_question(
            db=db,
            user_id=current_user.id,
            interview=interview,
            last_qa=last_qa_payload
        )

        next_q = InterviewQuestion(
            interview_id=interview.id,
            question_number=interview.current_question_number,
            question_text=next_q_data["question"],
            category=next_q_data["category"],
            difficulty=next_q_data["difficulty"],
            is_followup=next_q_data["is_followup"],
            topic=next_q_data["topic"],
            source=next_q_data["source"]
        )
        db.add(next_q)
        db.commit()
        db.refresh(next_q)

        return {
            "is_complete": False,
            "eval_result": eval_result,
            "communication_analysis": comm_payload,
            "difficulty_change": diff_status,
            "old_difficulty": old_diff,
            "new_difficulty": next_diff,
            "next_question_id": next_q.id,
            "next_question": next_q.question_text,
            "next_category": next_q.category,
            "next_difficulty": next_q.difficulty,
            "next_topic": next_q.topic,
            "next_source": next_q.source,
            "is_followup": next_q.is_followup,
            "current_step": interview.current_question_number,
            "total_questions": interview.question_count
        }

@router.get("/active")
def get_active_interview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Returns active IN_PROGRESS interview session for user if present. """
    interview = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "IN_PROGRESS"
    ).order_by(Interview.created_at.desc()).first()

    if not interview:
        return {"has_active": False}

    last_q = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id
    ).order_by(InterviewQuestion.question_number.desc()).first()

    return {
        "has_active": True,
        "interview_id": interview.id,
        "target_role": interview.target_role,
        "interview_type": interview.interview_type,
        "current_difficulty": interview.current_difficulty,
        "current_step": interview.current_question_number,
        "total_questions": interview.question_count,
        "last_question": {
            "id": last_q.id,
            "question": last_q.question_text,
            "category": last_q.category,
            "difficulty": last_q.difficulty,
            "topic": last_q.topic,
            "source": last_q.source
        } if last_q else None
    }

@router.get("/{interview_id}/report")
async def get_interview_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Retrieves final report for completed interview. """
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found or access denied.")

    if interview.feedback_json:
        try:
            return json.loads(interview.feedback_json)
        except:
            pass

    return await AdaptiveInterviewService.evaluate_full_interview(db, current_user.id, interview_id)

@router.get("/history")
def get_interview_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).all()

    result = []
    for i in interviews:
        result.append({
            "id": i.id,
            "target_role": i.target_role,
            "interview_type": i.interview_type,
            "starting_difficulty": i.starting_difficulty,
            "current_difficulty": i.current_difficulty,
            "overall_score": i.overall_score,
            "technical_score": i.technical_score,
            "communication_score": i.communication_score,
            "status": i.status,
            "created_at": i.created_at.isoformat() if i.created_at else None
        })
    return result
