from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Curriculum(Base):
    __tablename__ = "curricula"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    topics = relationship("Topic", back_populates="curriculum")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    curriculum_id = Column(Integer, ForeignKey("curricula.id"), nullable=True)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=True)
    order_in_curriculum = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    curriculum = relationship("Curriculum", back_populates="topics")
    evaluations = relationship("Evaluation", back_populates="topic")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    user_id = Column(Integer, nullable=False, default=1) 
    score = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    grammar_issues = Column(Text, nullable=True)
    advanced_version = Column(Text, nullable=True)
    vocabulary_suggestions = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)
    learning_mode = Column(String, nullable=True, default="general")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    topic = relationship("Topic", back_populates="evaluations")

class AchievementTemplate(Base):
    __tablename__ = "achievement_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String, nullable=True)
    criteria_type = Column(String, nullable=False)
    criteria_threshold = Column(Integer, default=1)
    points = Column(Integer, default=10)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)
    achievement_id = Column(Integer, ForeignKey("achievement_templates.id"), nullable=False)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notified = Column(Integer, default=0) # using Integer as boolean for sqlite 0/1
    
    template = relationship("AchievementTemplate")
