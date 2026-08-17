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
    
    # Voice Analysis specific fields
    communication_score = Column(Integer, nullable=True)
    speaking_pace_score = Column(Integer, nullable=True)
    clarity_score = Column(Integer, nullable=True)
    grammar_score = Column(Integer, nullable=True)
    vocabulary_score = Column(Integer, nullable=True)
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
    status = Column(String, default="active") # active, completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    items = relationship("RoadmapItem", back_populates="roadmap")

class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    topic_name = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, in_progress, completed
    priority = Column(Integer, default=1)
    difficulty = Column(String, nullable=True)
    order_index = Column(Integer, default=0)
    
    roadmap = relationship("Roadmap", back_populates="items")

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
    file_path = Column(String, nullable=False)
    parsed_skills = Column(Text, nullable=True) # JSON string
    parsed_projects = Column(Text, nullable=True) # JSON string
    parsed_experience = Column(Text, nullable=True) # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    interview_type = Column(String, nullable=False) # technical, hr, behavioral
    overall_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    technical_score = Column(Integer, nullable=True)
    feedback_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    questions = relationship("InterviewQuestion", back_populates="interview")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    ai_score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    
    question = relationship("InterviewQuestion", back_populates="answers")

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
