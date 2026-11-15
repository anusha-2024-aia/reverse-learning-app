import math
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Literal

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
    learning_mode: Literal["general", "technical", "fluency", "explain"] = "general"

    @field_validator("learning_mode", mode="before")
    @classmethod
    def validate_learning_mode(cls, v):
        if v is None:
            return "general"
        if not isinstance(v, str):
            raise ValueError("learning_mode must be a string")
        clean = v.strip().lower()
        allowed = {"general", "technical", "fluency", "explain"}
        if clean not in allowed:
            raise ValueError(f"Invalid learning_mode. Must be one of: {sorted(allowed)}")
        return clean

class DimensionDetail(BaseModel):
    score: int
    feedback: str

class ConceptCoverageDetail(BaseModel):
    concept: str
    covered: bool
    matched_evidence: Optional[str] = None

class ConceptCoverageOut(BaseModel):
    required_count: int
    covered_count: int
    coverage_percentage: Optional[float] = None
    covered_concepts: list[str] = []
    missing_concepts: list[str] = []
    details: list[ConceptCoverageDetail] = []

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
    concept_coverage: Optional[ConceptCoverageOut] = None
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

class SubmitAnswerRequest(BaseModel):
    interview_id: int
    current_question_id: Optional[int] = None
    answer: str
    is_final: Optional[bool] = False
    duration_seconds: Optional[float] = None

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def validate_duration(cls, v):
        if v is None or isinstance(v, bool):
            return None
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val) or val <= 0:
                return None
            return val
        except (ValueError, TypeError):
            return None
