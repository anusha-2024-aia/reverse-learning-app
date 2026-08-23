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
    topic_id: int
    explanation: str
    learning_mode: str = "general"

class DimensionDetail(BaseModel):
    score: int
    feedback: str

class MultiDimensionalEvaluation(BaseModel):
    technicalAccuracy: DimensionDetail
    conceptUnderstanding: DimensionDetail
    completeness: DimensionDetail
    examples: DimensionDetail
    relevance: DimensionDetail
    communication: DimensionDetail
    grammar: DimensionDetail
    vocabulary: DimensionDetail
    strengths: list[str] = []
    weaknesses: list[str] = []
    knowledgeGaps: list[dict] = [] # list of {"concept": str, "severity": str, "evidence": str}
    overallInsight: Optional[str] = None

class EvaluationOut(BaseModel):
    id: int
    topic_id: int
    ai_score: Optional[int] = None
    overall_score: Optional[int] = None
    technical_score: Optional[int] = None
    concept_score: Optional[int] = None
    completeness_score: Optional[int] = None
    examples_score: Optional[int] = None
    relevance_score: Optional[int] = None
    communication_score: Optional[int] = None
    grammar_score: Optional[int] = None
    vocabulary_score: Optional[int] = None
    attempt_number: Optional[int] = 1
    ai_insight: Optional[str] = None
    ai_feedback_json: Optional[str] = None
    created_at: datetime
    explanation_length: Optional[int] = None
    strengths_count: Optional[int] = None
    weaknesses_count: Optional[int] = None

    class Config:
        from_attributes = True

class AdaptiveRecommendationOut(BaseModel):
    id: int
    user_id: int
    topic_id: int
    action_type: str
    priority_score: float
    reason: Optional[str] = None
    target_concept: Optional[str] = None
    difficulty: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    topic: Optional[TopicOut] = None

    class Config:
        from_attributes = True

class AdaptiveRecommendationUpdate(BaseModel):
    status: str
