from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TopicOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    topic_id: int

class SessionOut(BaseModel):
    id: int
    topic_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EvaluationCreate(BaseModel):
    session_id: int
    topic_id: int
    explanation: str
    learning_mode: str = "general"

class EvaluationOut(BaseModel):
    id: int
    topic_id: int
    ai_score: Optional[int] = None
    ai_feedback_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
