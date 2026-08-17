import json
import io
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Interview, InterviewQuestion, InterviewAnswer, Resume
from app.ai_service.gemini_agent import generate_interview_question, evaluate_interview_performance
from app.services.resume_parser import ResumeParser
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/interview")

class QA(BaseModel):
    question: str
    answer: str

class AnswerRequest(BaseModel):
    interview_id: int
    current_question_id: int
    answer: str
    is_final: bool

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Uploads and parses a resume. """
    filename = file.filename.lower()
    
    # Save file temporarily to extract text using the parser
    temp_path = f"/tmp/{current_user.id}_{filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_interview(
    target_role: str = Form(...),
    difficulty: str = Form(...),
    interview_type: str = Form(...),
    resume_id: Optional[int] = Form(None),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """ Starts a new personalized mock interview. """
    interview = Interview(
        user_id=current_user.id,
        target_role=target_role,
        difficulty=difficulty,
        interview_type=interview_type
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    notes = f"Role: {target_role}, Difficulty: {difficulty}, Type: {interview_type}"
    if resume_id:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
        if resume:
            notes += f"\nResume Skills: {resume.parsed_skills}\nProjects: {resume.parsed_projects}\nExperience: {resume.parsed_experience}"

    question_text = await generate_interview_question(notes, [])
    
    q = InterviewQuestion(interview_id=interview.id, question_text=question_text)
    db.add(q)
    db.commit()
    db.refresh(q)
    
    return {"interview_id": interview.id, "question_id": q.id, "question": question_text}

@router.post("/answer")
async def process_answer(req: AnswerRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Processes an answer and returns the next question or the final evaluation. """
    interview = db.query(Interview).filter(Interview.id == req.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    ans = InterviewAnswer(question_id=req.current_question_id, answer_text=req.answer)
    db.add(ans)
    db.commit()
    
    # Reconstruct history
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview.id).order_by(InterviewQuestion.id.asc()).all()
    previous_qa = []
    for q in questions:
        a = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        if a:
            previous_qa.append({"question": q.question_text, "answer": a.answer_text})
            
    # Load notes context
    notes = f"Role: {interview.target_role}, Difficulty: {interview.difficulty}, Type: {interview.interview_type}"
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    if resume:
        notes += f"\nResume Skills: {resume.parsed_skills}\nProjects: {resume.parsed_projects}\nExperience: {resume.parsed_experience}"

    if req.is_final:
        evaluation = await evaluate_interview_performance(notes, previous_qa)
        
        # Save evaluation to db
        interview.overall_score = evaluation.get("overall_score", 0)
        interview.communication_score = evaluation.get("communication_score", 0)
        interview.technical_score = evaluation.get("technical_score", 0)
        interview.feedback_json = json.dumps(evaluation)
        db.commit()
        
        ActivityService.log_activity(db, current_user.id, "interview")
        
        return {"evaluation": evaluation}
    else:
        next_question_text = await generate_interview_question(notes, previous_qa)
        new_q = InterviewQuestion(interview_id=interview.id, question_text=next_question_text)
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        return {"next_question": next_question_text, "question_id": new_q.id}

@router.get("/history")
def get_interview_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).all()
    result = []
    for i in interviews:
        result.append({
            "id": i.id,
            "target_role": i.target_role,
            "difficulty": i.difficulty,
            "overall_score": i.overall_score,
            "communication_score": i.communication_score,
            "technical_score": i.technical_score,
            "created_at": i.created_at.isoformat() if i.created_at else None
        })
    return result
