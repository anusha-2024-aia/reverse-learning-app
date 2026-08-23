import os
import sys
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app import models
from app.services import achievement_service, activity_service

def run_tests():
    print("--- STARTING PHASE 7 GAMIFICATION & ACHIEVEMENTS TESTS ---")
    db = SessionLocal()
    try:
        # 1. Seed achievements
        achievement_service.seed_achievements(db)
        
        # Verify required templates exist
        required_slugs = [
            "first_explanation",
            "seven_day_learner",
            "fifty_concepts",
            "knowledge_gap_hunter",
            "ten_evaluations",
            "interview_ready"
        ]
        
        templates = db.query(models.AchievementTemplate).all()
        template_slugs = {t.slug for t in templates}
        for slug in required_slugs:
            assert slug in template_slugs, f"Missing required achievement template: {slug}"
            
        print("Test 1: Achievement Templates Seeding PASSED.")

        # 2. Create test user
        user = db.query(models.User).filter(models.User.email == "gamify_test@example.com").first()
        if not user:
            user = models.User(username="gamify_test", email="gamify_test@example.com", password_hash="hash")
            db.add(user)
            db.commit()
            db.refresh(user)

        # Clear existing test user achievements & activity logs
        db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user.id).delete()
        db.query(models.Evaluation).filter(models.Evaluation.user_id == user.id).delete()
        db.query(models.Interview).filter(models.Interview.user_id == user.id).delete()
        db.query(models.LearningActivity).filter(models.LearningActivity.user_id == user.id).delete()
        db.query(models.Streak).filter(models.Streak.user_id == user.id).delete()
        db.commit()




        # Initial check - no evaluations/interviews -> no unlocks yet
        unlocked = achievement_service.get_user_achievements(db, user.id)
        assert unlocked["unlocked_count"] == 0, f"Expected 0 unlocks, got {unlocked['unlocked_count']}"
        print("Test 2: Initial Locked State PASSED.")

        # 3. Add 1 Evaluation -> Should unlock First Explanation
        topic = db.query(models.Topic).first()
        eval1 = models.Evaluation(
            user_id=user.id,
            topic_id=topic.id,
            explanation="This is a detailed explanation of topic.",
            overall_score=85,
            ai_score=85
        )
        db.add(eval1)
        db.commit()

        achievement_service.check_achievements_for_user(db, user.id)
        res1 = achievement_service.get_user_achievements(db, user.id)
        unlocked_slugs1 = {a["slug"] for a in res1["achievements"] if a["unlocked"]}
        assert "first_explanation" in unlocked_slugs1, "Failed to unlock first_explanation when explanations >= 1"
        print("Test 3: First Explanation condition PASSED.")

        # 4. Add Mock Interview -> Should unlock Interview Ready
        interview = models.Interview(
            user_id=user.id,
            target_role="Full Stack Developer",
            difficulty="intermediate",
            interview_type="technical",
            overall_score=88
        )
        db.add(interview)
        db.commit()

        achievement_service.check_achievements_for_user(db, user.id)
        res2 = achievement_service.get_user_achievements(db, user.id)
        unlocked_slugs2 = {a["slug"] for a in res2["achievements"] if a["unlocked"]}
        assert "interview_ready" in unlocked_slugs2, "Failed to unlock interview_ready when interviews >= 1"
        print("Test 4: Interview Ready condition PASSED.")

        # 5. Streak Tracking
        today = datetime.now(timezone.utc).date()
        for i in range(7):
            d = today - timedelta(days=(6 - i))
            activity_service.ActivityService.update_streak(db, user.id, d)

        streak_info = activity_service.ActivityService.get_streak_info(db, user.id)
        assert streak_info["current_streak"] >= 7, f"Expected streak >= 7, got {streak_info['current_streak']}"
        
        achievement_service.check_achievements_for_user(db, user.id)
        res3 = achievement_service.get_user_achievements(db, user.id)
        unlocked_slugs3 = {a["slug"] for a in res3["achievements"] if a["unlocked"]}
        assert "seven_day_learner" in unlocked_slugs3, "Failed to unlock seven_day_learner when streak >= 7"
        print("Test 5: 7 Day Learner & Streak Tracking PASSED.")

        print("--- ALL PHASE 7 GAMIFICATION TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
