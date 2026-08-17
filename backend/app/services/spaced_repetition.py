from datetime import datetime, timedelta, timezone

class SpacedRepetition:
    @staticmethod
    def calculate_next_review(mastery_score: float, attempts: int, current_score: int) -> datetime:
        """
        Simple SM-2 inspired spaced repetition logic.
        """
        base_interval_hours = 24
        
        # If they scored poorly, review sooner
        if current_score < 6:
            interval_multiplier = 0.5 # 12 hours
        elif current_score < 8:
            interval_multiplier = 1.0 # 1 day
        else:
            # Good score, extend interval based on previous mastery
            interval_multiplier = 1.5 + (mastery_score / 50.0) # 1.5 to 3.5 days
            
        # Scale with number of attempts (if they've seen it many times, interval grows)
        attempt_multiplier = 1.0 + (attempts * 0.2)
        
        total_hours = base_interval_hours * interval_multiplier * attempt_multiplier
        
        # Cap interval at 30 days
        if total_hours > 720:
            total_hours = 720
            
        return datetime.now(timezone.utc) + timedelta(hours=total_hours)
