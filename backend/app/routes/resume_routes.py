import os
import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.rate_limiter import rate_limit_authenticated
from app.services.resume_intelligence_service import ResumeIntelligenceService

router = APIRouter()

doc_rate_limit = rate_limit_authenticated(default_limit=3, window_seconds=60, env_var_name="DOCUMENT_RATE_LIMIT")

import uuid

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(doc_rate_limit)
):
    """
    Uploads PDF or DOCX resume, validates format and size, extracts text,
    structures JSON via Gemini, and generates personalized interview questions.
    """
    raw_filename = os.path.basename(file.filename or "resume.pdf")
    ext = os.path.splitext(raw_filename)[1].lower().replace('.', '')

    if ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit (10 MB).")

    if len(contents) < 50:
        raise HTTPException(status_code=400, detail="Uploaded file is empty or corrupted.")

    # Save to upload folder safely
    upload_dir = "./uploads/resumes"
    os.makedirs(upload_dir, exist_ok=True)
    clean_name = "".join(c for c in raw_filename if c.isalnum() or c in "._-")
    safe_filename = f"user_{current_user.id}_{uuid.uuid4().hex}_{clean_name}"
    file_path = os.path.abspath(os.path.join(upload_dir, safe_filename))

    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text
    try:
        extracted_text = ResumeIntelligenceService.extract_text(file_path, ext)
    except Exception as parse_err:
        raise HTTPException(status_code=400, detail=str(parse_err))

    # Deactivate older resumes
    db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).update({"is_active": False})
    db.commit()

    # Structure data via Gemini
    try:
        structured_data = await ResumeIntelligenceService.analyze_and_structure_resume(extracted_text)
    except Exception as ai_err:
        print(f"Error in resume analysis (using rule-based parser): {ai_err}")
        structured_data = ResumeIntelligenceService.fallback_rule_based_parse(extracted_text)

    # Save new active Resume record
    new_resume = models.Resume(
        user_id=current_user.id,
        file_name=raw_filename,
        file_type=ext,
        file_path=file_path,
        extracted_text=extracted_text,
        is_active=True,
        parsed_skills=json.dumps(structured_data.get("skills", [])),
        parsed_projects=json.dumps(structured_data.get("projects", [])),
        parsed_experience=json.dumps(structured_data.get("experience", [])),
        parsed_education=json.dumps(structured_data.get("education", [])),
        parsed_certifications=json.dumps(structured_data.get("certifications", [])),
        analysis_summary_json=json.dumps(structured_data)
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    # Generate personalized questions
    generated_questions = await ResumeIntelligenceService.generate_personalized_questions(
        db=db,
        user_id=current_user.id,
        resume_id=new_resume.id
    )

    return {
        "message": "Resume uploaded and analyzed successfully",
        "resume_id": new_resume.id,
        "file_name": raw_filename,
        "analysis_summary": structured_data,
        "questions_generated_count": len(generated_questions)
    }

@router.get("/resume/active")
def get_active_resume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns active resume details, parsed skills, projects, and generated questions for current user.
    """
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.created_at.desc()).first()

    if not resume:
        return {"has_resume": False}

    try:
        structured = json.loads(resume.analysis_summary_json) if resume.analysis_summary_json else {}
    except:
        structured = {}

    questions = db.query(models.ResumeQuestion).filter(
        models.ResumeQuestion.resume_id == resume.id,
        models.ResumeQuestion.user_id == current_user.id
    ).all()

    q_list = [{
        "id": q.id,
        "category": q.category,
        "question": q.question_text,
        "difficulty": q.difficulty,
        "source": q.target_project_or_skill,
        "target": q.target_project_or_skill
    } for q in questions]

    # Fetch last interview
    last_interview = db.query(models.ResumeInterview).filter(
        models.ResumeInterview.user_id == current_user.id,
        models.ResumeInterview.resume_id == resume.id
    ).order_by(models.ResumeInterview.created_at.desc()).first()

    return {
        "has_resume": True,
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "file_type": resume.file_type,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "analysis_summary": structured,
        "questions": q_list,
        "questions_count": len(q_list),
        "last_interview_score": last_interview.overall_score if last_interview else None
    }

@router.get("/resume/{resume_id}")
def get_resume_by_id(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns specific resume details verifying user ownership.
    """
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied.")

    try:
        structured = json.loads(resume.analysis_summary_json) if resume.analysis_summary_json else {}
    except:
        structured = {}

    questions = db.query(models.ResumeQuestion).filter(
        models.ResumeQuestion.resume_id == resume.id,
        models.ResumeQuestion.user_id == current_user.id
    ).all()

    q_list = [{
        "id": q.id,
        "category": q.category,
        "question": q.question_text,
        "difficulty": q.difficulty,
        "source": q.target_project_or_skill,
        "target": q.target_project_or_skill
    } for q in questions]

    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "file_type": resume.file_type,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "analysis_summary": structured,
        "skills": json.loads(resume.parsed_skills or "[]"),
        "projects": json.loads(resume.parsed_projects or "[]"),
        "experience": json.loads(resume.parsed_experience or "[]"),
        "education": json.loads(resume.parsed_education or "[]"),
        "questions": q_list
    }

@router.post("/resume/analyze")
async def reanalyze_resume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(doc_rate_limit)
):
    """
    Re-runs Gemini analysis and question generation on the active resume.
    """
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.created_at.desc()).first()

    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")

    if not resume.extracted_text:
        extracted_text = ResumeIntelligenceService.extract_text(resume.file_path, resume.file_type)
        resume.extracted_text = extracted_text
        db.commit()

    structured_data = await ResumeIntelligenceService.analyze_and_structure_resume(resume.extracted_text)
    resume.parsed_skills = json.dumps(structured_data.get("skills", []))
    resume.parsed_projects = json.dumps(structured_data.get("projects", []))
    resume.parsed_experience = json.dumps(structured_data.get("experience", []))
    resume.parsed_education = json.dumps(structured_data.get("education", []))
    resume.parsed_certifications = json.dumps(structured_data.get("certifications", []))
    resume.analysis_summary_json = json.dumps(structured_data)
    db.commit()

    questions = await ResumeIntelligenceService.generate_personalized_questions(
        db=db,
        user_id=current_user.id,
        resume_id=resume.id
    )

    return {
        "message": "Resume re-analyzed successfully",
        "analysis_summary": structured_data,
        "questions_count": len(questions)
    }

@router.post("/resume/interview/start")
def start_resume_interview(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Starts a new personalized resume-based mock interview session.
    """
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id,
        models.Resume.is_active == True
    ).order_by(models.Resume.created_at.desc()).first()

    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found. Please upload a resume first.")

    questions = db.query(models.ResumeQuestion).filter(
        models.ResumeQuestion.resume_id == resume.id,
        models.ResumeQuestion.user_id == current_user.id
    ).all()

    if not questions:
        raise HTTPException(status_code=400, detail="No personalized questions found for this resume. Please analyze resume first.")

    interview = models.ResumeInterview(
        user_id=current_user.id,
        resume_id=resume.id,
        status="IN_PROGRESS"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    first_q = questions[0]

    return {
        "interview_id": interview.id,
        "question_id": first_q.id,
        "question": first_q.question_text,
        "category": first_q.category,
        "difficulty": first_q.difficulty,
        "target": first_q.target_project_or_skill,
        "total_questions": min(5, len(questions)),
        "current_step": 1
    }

@router.post("/resume/interview/answer")
async def answer_resume_interview_question(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Processes candidate answer during resume interview, returns follow-up question or final evaluation report.
    """
    interview_id = payload.get("interview_id")
    answer_text = payload.get("answer", "").strip()
    is_final = payload.get("is_final", False)
    qa_history = payload.get("qa_history", [])

    if not interview_id or not answer_text:
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    interview = db.query(models.ResumeInterview).filter(
        models.ResumeInterview.id == interview_id,
        models.ResumeInterview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Resume interview session not found")

    resume = db.query(models.Resume).filter(models.Resume.id == interview.resume_id).first()
    target_role = current_user.target_role or "Software Engineer"

    if is_final:
        eval_report = await ResumeIntelligenceService.evaluate_resume_interview(
            db=db,
            user_id=current_user.id,
            interview_id=interview_id,
            qa_history=qa_history
        )
        return {
            "is_complete": True,
            "report": eval_report
        }
    else:
        # Generate follow-up question
        follow_up_text = await ResumeIntelligenceService.generate_followup_question(
            target_role=target_role,
            previous_qa=qa_history
        )

        return {
            "is_complete": False,
            "follow_up_question": follow_up_text,
            "next_step": len(qa_history) + 1
        }

@router.get("/resume/interview/history")
def get_resume_interview_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns candidate's resume interview history.
    """
    interviews = db.query(models.ResumeInterview, models.Resume).join(
        models.Resume, models.ResumeInterview.resume_id == models.Resume.id
    ).filter(models.ResumeInterview.user_id == current_user.id).order_by(models.ResumeInterview.created_at.desc()).all()

    result = []
    for i, r in interviews:
        try:
            feedback = json.loads(i.feedback_json) if i.feedback_json else {}
        except:
            feedback = {}

        result.append({
            "id": i.id,
            "resume_name": r.file_name,
            "overall_score": i.overall_score,
            "technical_score": i.technical_score,
            "project_knowledge_score": i.project_knowledge_score,
            "communication_score": i.communication_score,
            "problem_solving_score": i.problem_solving_score,
            "status": i.status,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "strengths": feedback.get("strengths", []),
            "weaknesses": feedback.get("weaknesses", [])
        })

    return result
