from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # New Profile Fields
    target_role = Column(String, nullable=True)
    skill_level = Column(String, nullable=True)
    learning_goals = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=True)
    
    # Phase 5 Roadmap Onboarding Profile Fields
    hours_per_day = Column(Float, default=2.0)
    days_per_week = Column(Integer, default=6)
    experience_level = Column(String, default="BEGINNER")
    current_skills = Column(Text, nullable=True) # JSON list string
    preferred_areas = Column(Text, nullable=True) # JSON list string
    onboarding_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Curriculum(Base):
    __tablename__ = "curricula"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    
    topics = relationship("Topic", back_populates="curriculum")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer, ForeignKey("curricula.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    order_in_curriculum = Column(Integer, nullable=True)
    
    curriculum = relationship("Curriculum", back_populates="topics")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    explanation = Column(Text, nullable=True)
    ai_score = Column(Integer, nullable=True)
    ai_feedback_json = Column(Text, nullable=True)
    explanation_length = Column(Integer, nullable=True)
    strengths_count = Column(Integer, nullable=True)
    weaknesses_count = Column(Integer, nullable=True)
    
    # Multi-Dimensional Evaluation 2.0 fields
    overall_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    concept_score = Column(Integer, nullable=True)
    completeness_score = Column(Integer, nullable=True)
    examples_score = Column(Integer, nullable=True)
    relevance_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    grammar_score = Column(Integer, nullable=True)
    vocabulary_score = Column(Integer, nullable=True)
    
    attempt_number = Column(Integer, default=1)
    ai_insight = Column(Text, nullable=True)
    
    # Voice Analysis specific fields
    speaking_pace_score = Column(Integer, nullable=True)
    clarity_score = Column(Integer, nullable=True)
    filler_words = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# ------------ NEW TIER 3 MODELS ------------

class UserMastery(Base):
    __tablename__ = "user_mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    mastery_score = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    last_review = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)

class Roadmap(Base):
    __tablename__ = "roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String, nullable=False)
    career_goal = Column(Text, nullable=True)
    experience_level = Column(String, nullable=True)
    hours_per_day = Column(Float, default=2.0)
    days_per_week = Column(Integer, default=6)
    preferred_areas = Column(Text, nullable=True) # JSON string
    version = Column(Integer, default=1)
    progress = Column(Float, default=0.0)
    estimated_hours = Column(Integer, default=0)
    status = Column(String, default="active") # active, completed, archived
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")
    changes = relationship("RoadmapChange", back_populates="roadmap", cascade="all, delete-orphan")

class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    importance = Column(String, default="HIGH") # HIGH, MEDIUM, LOW
    difficulty = Column(String, nullable=True) # BEGINNER, INTERMEDIATE, ADVANCED
    prerequisites = Column(Text, nullable=True) # JSON list of prerequisite topic names
    estimated_hours = Column(Integer, default=10)
    mastery_score = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    status = Column(String, default="NOT_STARTED") # LOCKED, NOT_STARTED, IN_PROGRESS, WEAK, REVIEW, PRACTICE, STRONG, MASTERED
    reason = Column(Text, nullable=True)
    skills_gained = Column(Text, nullable=True) # JSON list
    order_index = Column(Integer, default=0)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    last_evaluated_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    roadmap = relationship("Roadmap", back_populates="items")

class RoadmapChange(Base):
    __tablename__ = "roadmap_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_type = Column(String, nullable=False) # REORDERED, STATUS_CHANGED, ROLE_CHANGED, PREREQUISITE_INSERTED, TIME_UPDATED
    topic_name = Column(String, nullable=True)
    old_position = Column(Integer, nullable=True)
    new_position = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    roadmap = relationship("Roadmap", back_populates="changes")

class LearningActivity(Base):
    __tablename__ = "learning_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False) # explanation, interview, revision
    date_logged = Column(Date, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Streak(Base):
    __tablename__ = "streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True) # pdf, docx
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    parsed_skills = Column(Text, nullable=True) # JSON list
    parsed_projects = Column(Text, nullable=True) # JSON list of dicts
    parsed_experience = Column(Text, nullable=True) # JSON list of dicts
    parsed_education = Column(Text, nullable=True) # JSON list of dicts
    parsed_certifications = Column(Text, nullable=True) # JSON list
    analysis_summary_json = Column(Text, nullable=True) # JSON dict
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ResumeQuestion(Base):
    __tablename__ = "resume_questions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False) # Technical, Project, Experience, Behavioral, Verification
    question_text = Column(Text, nullable=False)
    difficulty = Column(String, default="Medium") # Easy, Medium, Hard
    target_project_or_skill = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ResumeInterview(Base):
    __tablename__ = "resume_interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    overall_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    project_knowledge_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    problem_solving_score = Column(Integer, nullable=True)
    resume_understanding_score = Column(Integer, nullable=True)
    feedback_json = Column(Text, nullable=True) # JSON dict with strengths, weaknesses, recommended prep
    status = Column(String, default="IN_PROGRESS") # IN_PROGRESS, COMPLETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

class Interview(Base):

    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    target_role = Column(String, nullable=False)
    difficulty = Column(String, nullable=False, default="MEDIUM")
    interview_type = Column(String, nullable=False) # technical, hr, behavioral, resume, mixed
    starting_difficulty = Column(String, default="MEDIUM")
    current_difficulty = Column(String, default="MEDIUM")
    question_count = Column(Integer, default=10)
    current_question_number = Column(Integer, default=1)
    status = Column(String, default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, ABANDONED
    overall_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    project_knowledge_score = Column(Integer, nullable=True)
    problem_solving_score = Column(Integer, nullable=True)
    feedback_json = Column(Text, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    questions = relationship("InterviewQuestion", back_populates="interview")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_number = Column(Integer, default=1)
    question_text = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    difficulty = Column(String, default="MEDIUM")
    is_followup = Column(Boolean, default=False)
    topic = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    ai_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    completeness_score = Column(Integer, nullable=True)
    relevance_score = Column(Integer, nullable=True)
    overall_score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    question = relationship("InterviewQuestion", back_populates="answers")

class CommunicationAnalysis(Base):
    __tablename__ = "communication_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    answer_id = Column(Integer, ForeignKey("interview_answers.id"), nullable=True)
    
    communication_score = Column(Integer, nullable=False, default=70) # 0-100
    clarity_score = Column(Integer, nullable=False, default=70) # 0-100
    grammar_score = Column(Integer, nullable=False, default=70) # 0-100
    vocabulary_score = Column(Integer, nullable=False, default=70) # 0-100
    structure_score = Column(Integer, nullable=False, default=70) # 0-100
    
    speaking_pace = Column(String, default="Good") # Slow, Good, Fast
    words_per_minute = Column(Integer, nullable=True) # Only if audio duration reliably provided
    pause_count = Column(Integer, nullable=True) # Only if audio data supports it
    filler_word_count = Column(Integer, default=0)
    filler_words_json = Column(Text, nullable=True) # e.g. {"um": 3, "like": 2}
    
    grammar_feedback = Column(Text, nullable=True)
    grammar_improvements_json = Column(Text, nullable=True) # e.g. [{"incorrect": "...", "improved": "..."}]
    vocabulary_feedback = Column(Text, nullable=True)
    clarity_feedback = Column(Text, nullable=True)
    structure_feedback = Column(Text, nullable=True)
    ai_coach_recommendation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AchievementTemplate(Base):
    __tablename__ = "achievement_templates"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon_name = Column(String, nullable=False)
    points = Column(Integer, default=0)
    criteria_type = Column(String, nullable=False)
    criteria_threshold = Column(Integer, default=1)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievement_templates.id"), nullable=False)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notified = Column(Integer, default=0)
    
    template = relationship("AchievementTemplate")

class AdaptiveRecommendation(Base):
    __tablename__ = "adaptive_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    action_type = Column(String, nullable=False) # LEARN, REVIEW, EXPLAIN, PRACTICE, RETAKE, MOVE_FORWARD
    priority_score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    target_concept = Column(String, nullable=True) # E.g., specific knowledge gap
    difficulty = Column(String, default="EASY")
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, SKIPPED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    topic = relationship("Topic")

class RevisionSchedule(Base):
    __tablename__ = "revision_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    last_mastery_score = Column(Float, default=0.0)
    current_mastery_score = Column(Float, default=0.0)
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    status = Column(String, default="UPCOMING") # DUE, UPCOMING, OVERDUE, COMPLETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    topic = relationship("Topic")

