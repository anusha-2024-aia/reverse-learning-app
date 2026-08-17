from sqlalchemy.orm import Session
from app.models import UserMastery, Topic, Evaluation
from datetime import datetime, timezone
from app.services.spaced_repetition import SpacedRepetition

class AdaptiveEngine:
    @staticmethod
    def update_mastery(db: Session, user_id: int, topic_id: int, evaluation_score: int):
        """
        Updates or creates a UserMastery record based on an evaluation.
        """
        mastery = db.query(UserMastery).filter(
            UserMastery.user_id == user_id, 
            UserMastery.topic_id == topic_id
        ).first()

        if not mastery:
            mastery = UserMastery(
                user_id=user_id,
                topic_id=topic_id,
                attempts=0,
                successful_attempts=0,
                failed_attempts=0,
                mastery_score=0.0
            )
            db.add(mastery)
        
        mastery.attempts += 1
        
        # Consider score >= 7 as success
        if evaluation_score >= 7:
            mastery.successful_attempts += 1
        else:
            mastery.failed_attempts += 1
            
        mastery.last_review = datetime.now(timezone.utc)
        
        # Simple mastery calculation: weighted moving average or success rate
        # Let's use an exponential moving average for mastery score
        alpha = 0.3
        normalized_score = evaluation_score * 10 # 0-100 scale
        
        if mastery.attempts == 1:
            mastery.mastery_score = normalized_score
        else:
            mastery.mastery_score = (alpha * normalized_score) + ((1 - alpha) * mastery.mastery_score)
            
        # Update Spaced Repetition next_review date
        mastery.next_review = SpacedRepetition.calculate_next_review(mastery.mastery_score, mastery.attempts, evaluation_score)
            
        db.commit()
        db.refresh(mastery)
        return mastery

    @staticmethod
    def get_weak_topics(db: Session, user_id: int, limit: int = 3):
        """
        Identifies weak topics based on mastery score and failure rate.
        """
        # Fetch mastery records ordered by mastery_score ascending, prioritizing those with at least 1 failed attempt
        weak_masteries = db.query(UserMastery).filter(
            UserMastery.user_id == user_id,
            UserMastery.failed_attempts > 0
        ).order_by(UserMastery.mastery_score.asc()).limit(limit).all()
        
        results = []
        for m in weak_masteries:
            topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
            if topic:
                results.append({
                    "topic_id": m.topic_id,
                    "topic_name": topic.name,
                    "mastery_score": round(m.mastery_score, 2),
                    "attempts": m.attempts,
                    "success_rate": round(m.successful_attempts / m.attempts * 100) if m.attempts > 0 else 0,
                    "recommendation": f"Your performance on '{topic.name}' is low (Mastery: {round(m.mastery_score, 1)}/100). Consider reviewing this before moving on."
                })
        
        return results

    @staticmethod
    def get_strong_topics(db: Session, user_id: int, limit: int = 3):
        """
        Identifies strong topics based on mastery score.
        """
        strong_masteries = db.query(UserMastery).filter(
            UserMastery.user_id == user_id,
            UserMastery.mastery_score >= 80.0
        ).order_by(UserMastery.mastery_score.desc()).limit(limit).all()
        
        results = []
        for m in strong_masteries:
            topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
            if topic:
                results.append({
                    "topic_id": m.topic_id,
                    "topic_name": topic.name,
                    "mastery_score": round(m.mastery_score, 2)
                })
        return results
