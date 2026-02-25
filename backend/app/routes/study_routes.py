from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.ai_service.gemini_agent import evaluate_explanation, stream_evaluate_explanation

router = APIRouter()

class EvaluationRequest(BaseModel):
    topic: str
    explanation: str
    learning_mode: str = "general"

@router.post("/evaluate")
async def evaluate_user_study(request: EvaluationRequest):
    """
    Endpoint to evaluate a user's explanation of a topic.
    """
    if not request.topic or not request.explanation:
        raise HTTPException(status_code=400, detail="Topic and explanation are required")
    
    result = await evaluate_explanation(request.topic, request.explanation, request.learning_mode)
    return result

@router.post("/evaluate-stream")
async def evaluate_user_study_stream(request: EvaluationRequest):
    """
    Endpoint to evaluate a user's explanation with real-time streaming feedback.
    """
    if not request.topic or not request.explanation:
        raise HTTPException(status_code=400, detail="Topic and explanation are required")

    return StreamingResponse(
        stream_evaluate_explanation(request.topic, request.explanation, request.learning_mode),
        media_type="text/plain"
    )
