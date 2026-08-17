from sqlalchemy.orm import Session
from app.models import LearningActivity, Streak, User
from datetime import datetime, timezone, date, timedelta

class ActivityService:
    @staticmethod
    def log_activity(db: Session, user_id: int, activity_type: str):
        """
        Logs a learning activity and updates the user's streak.
        """
        today = datetime.now(timezone.utc).date()
        
        # Check if activity already logged today
        existing_activity = db.query(LearningActivity).filter(
            LearningActivity.user_id == user_id,
            LearningActivity.date_logged == today
        ).first()
        
        if not existing_activity:
            activity = LearningActivity(user_id=user_id, activity_type=activity_type, date_logged=today)
            db.add(activity)
            db.commit()
            
            ActivityService.update_streak(db, user_id, today)
            
    @staticmethod
    def update_streak(db: Session, user_id: int, today: date):
        streak = db.query(Streak).filter(Streak.user_id == user_id).first()
        
        if not streak:
            streak = Streak(user_id=user_id, current_streak=1, longest_streak=1, last_activity_date=today)
            db.add(streak)
        else:
            if streak.last_activity_date == today:
                # Already updated today
                return streak
            
            yesterday = today - timedelta(days=1)
            
            if streak.last_activity_date == yesterday:
                streak.current_streak += 1
            else:
                streak.current_streak = 1 # Reset streak
                
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
                
            streak.last_activity_date = today
            
        db.commit()
        db.refresh(streak)
        return streak

    @staticmethod
    def get_streak_info(db: Session, user_id: int):
        streak = db.query(Streak).filter(Streak.user_id == user_id).first()
        if not streak:
            return {"current_streak": 0, "longest_streak": 0, "last_activity_date": None}
            
        # If last activity was more than a day ago, current streak is logically 0
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        
        current = streak.current_streak
        if streak.last_activity_date and streak.last_activity_date < yesterday:
            current = 0
            
        return {
            "current_streak": current,
            "longest_streak": streak.longest_streak,
            "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None
        }
