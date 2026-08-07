from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import io
import fitz # PyMuPDF
import docx
from app.ai_service.gemini_agent import generate_interview_question, evaluate_interview_performance

router = APIRouter(prefix="/interview", tags=["Interview"])

class QA(BaseModel):
    question: str
    answer: str

class StartInterviewResponse(BaseModel):
    question: str
    extracted_text: str

class AnswerRequest(BaseModel):
    notes: str
    previous_qa: List[QA]
    is_final: bool

class AnswerResponse(BaseModel):
    next_question: Optional[str] = None
    evaluation: Optional[dict] = None

@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(file: UploadFile = File(...)):
    filename = file.filename.lower()
    content = await file.read()
    
    extracted_text = ""
    try:
        if filename.endswith(".txt"):
            extracted_text = content.decode("utf-8")
        elif filename.endswith(".pdf"):
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text()
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .txt, .pdf, or .docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the file.")
    
    question = await generate_interview_question(extracted_text, [])
    return StartInterviewResponse(question=question, extracted_text=extracted_text)

@router.post("/answer", response_model=AnswerResponse)
async def process_answer(req: AnswerRequest):
    if req.is_final:
        evaluation = await evaluate_interview_performance(req.notes, [qa.model_dump() for qa in req.previous_qa])
        return AnswerResponse(evaluation=evaluation)
    else:
        next_question = await generate_interview_question(req.notes, [qa.model_dump() for qa in req.previous_qa])
        return AnswerResponse(next_question=next_question)
