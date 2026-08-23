import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app import models
from app.services.communication_coach_service import CommunicationCoachService
from app.services.adaptive_interview_service import AdaptiveInterviewService

async def run_tests():
    print("--- STARTING PHASE 10 VOICE COMMUNICATION ANALYSIS TESTS ---")
    db = SessionLocal()

    try:
        # Create test users
        user_a = db.query(models.User).filter(models.User.email == "comm_a@example.com").first()
        if not user_a:
            user_a = models.User(username="comm_a", email="comm_a@example.com", password_hash="hash", target_role="Full Stack Developer")
            db.add(user_a)
            db.commit()
            db.refresh(user_a)

        user_b = db.query(models.User).filter(models.User.email == "comm_b@example.com").first()
        if not user_b:
            user_b = models.User(username="comm_b", email="comm_b@example.com", password_hash="hash", target_role="Data Engineer")
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        # -------------------------------------------------------------
        # 1. Test Filler Word Detection
        # -------------------------------------------------------------
        text_with_fillers = "Um, I think MySQL was basically selected because, like, we needed relational tables and, you know, ACID compliance."
        fillers_result = CommunicationCoachService.detect_filler_words(text_with_fillers)
        
        assert fillers_result["total_count"] >= 4, f"Expected at least 4 filler words, detected {fillers_result['total_count']}"
        assert "um" in fillers_result["breakdown"], "Filler 'um' should be detected"
        assert "basically" in fillers_result["breakdown"], "Filler 'basically' should be detected"
        assert "like" in fillers_result["breakdown"], "Filler 'like' should be detected"
        print(f"Test 1 (Filler Word Detection): PASSED. Detected {fillers_result['total_count']} fillers ({json.dumps(fillers_result['breakdown'])}).")

        # -------------------------------------------------------------
        # 2. Test Speaking Pace Calculation
        # -------------------------------------------------------------
        # Pace with audio duration (14 words in 6 seconds -> ~140 WPM -> Good)
        pace_with_duration = CommunicationCoachService.analyze_speaking_pace(text_with_fillers, duration_seconds=6.0)
        assert pace_with_duration["pace"] == "Good", f"Expected 'Good' pace, got {pace_with_duration['pace']}"
        assert pace_with_duration["wpm"] is not None and pace_with_duration["wpm"] > 100, f"Expected valid WPM, got {pace_with_duration['wpm']}"
        print(f"Test 2a (Speaking Pace with Duration): PASSED ({pace_with_duration['wpm']} WPM -> {pace_with_duration['pace']}).")

        # Pace without audio duration (omitted -> Good fallback without fabricating WPM)
        pace_no_duration = CommunicationCoachService.analyze_speaking_pace(text_with_fillers, duration_seconds=None)
        assert pace_no_duration["wpm"] is None, "WPM must not be fabricated when duration is omitted"
        assert pace_no_duration["pace"] == "Good", "Pace should fall back to Good when duration is omitted"
        print("Test 2b (Speaking Pace without Duration - No Manufactured WPM): PASSED.")

        # -------------------------------------------------------------
        # 3. Test Weighted Communication Score Calculation
        # -------------------------------------------------------------
        # Score formula test
        score_calc = CommunicationCoachService.calculate_overall_communication_score(
            clarity=82,
            grammar=74,
            vocabulary=80,
            structure=78,
            pace="Good",
            filler_count=6
        )
        assert 70 <= score_calc <= 85, f"Expected overall score around 76-80%, got {score_calc}%"
        print(f"Test 3 (Weighted Score Calculation Formula): PASSED (Score: {score_calc}%).")

        # -------------------------------------------------------------
        # 4. Test Multi-Dimensional Quality Analysis
        # -------------------------------------------------------------
        eval_quality = await CommunicationCoachService.analyze_communication_quality(
            transcript="I selected MySQL because the data structure required strict relational foreign keys.",
            question_text="Why did you select MySQL for your project database?"
        )
        assert eval_quality["clarity_score"] > 60, "Clarity score should be > 60"
        assert eval_quality["grammar_score"] > 60, "Grammar score should be > 60"
        assert "vocabulary_feedback" in eval_quality, "Vocabulary feedback should be present"
        print("Test 4 (Multi-Dimensional Communication Quality Analysis): PASSED.")

        # -------------------------------------------------------------
        # 5. Test Saving Communication Analysis Record
        # -------------------------------------------------------------
        # Clean previous communication records for test user
        db.query(models.CommunicationAnalysis).filter(models.CommunicationAnalysis.user_id == user_a.id).delete()
        db.commit()

        rec1 = await CommunicationCoachService.process_and_save_communication_analysis(
            db=db,
            user_id=user_a.id,
            transcript="Um, like, I think, um, we used Express and React.",
            question_text="What technology stack did you use?",
            duration_seconds=8.0
        )
        assert rec1.id is not None, "Record 1 should be persisted to DB"
        assert rec1.filler_word_count >= 3, "Filler word count should be recorded"

        # Simulate second interview with improved communication
        rec2 = await CommunicationCoachService.process_and_save_communication_analysis(
            db=db,
            user_id=user_a.id,
            transcript="We selected React for component modularity and Express.js for RESTful API routing, which gave us high frontend responsiveness.",
            question_text="Why did you select React and Express?",
            duration_seconds=12.0
        )
        assert rec2.id is not None, "Record 2 should be persisted to DB"
        print("Test 5 (Process and Persist Communication Analysis Records): PASSED.")

        # -------------------------------------------------------------
        # 6. Test Communication Progress & Delta Tracking
        # -------------------------------------------------------------
        progress = CommunicationCoachService.get_communication_progress(db, user_a.id)
        assert progress["has_data"] is True, "Progress should indicate has_data = True"
        assert progress["total_interviews_analyzed"] == 2, f"Expected 2 analyzed sessions, got {progress['total_interviews_analyzed']}"
        assert progress["before_vs_latest"] is not None, "Before vs Latest comparison should be present"
        
        latest_score = progress["before_vs_latest"]["latest_interview"]["overall"]
        first_score = progress["before_vs_latest"]["first_interview"]["overall"]
        assert latest_score >= first_score, "Latest communication score should show improvement over first"
        print(f"Test 6 (Communication Progress Tracking: First {first_score}% -> Latest {latest_score}%): PASSED.")

        # -------------------------------------------------------------
        # 7. Test Separation of Technical Evaluation vs Communication Score
        # -------------------------------------------------------------
        # Verify that difficulty transition depends ONLY on technical score
        # Technical score = 88 (HARD), Communication score = 55 (WEAK)
        next_diff = AdaptiveInterviewService.calculate_next_difficulty("MEDIUM", 88)
        assert next_diff == "HARD", f"Technical score 88 must scale difficulty to HARD despite weak communication, got {next_diff}"
        print("Test 7 (Strict Separation of Technical vs Communication Scoring): PASSED.")

        # -------------------------------------------------------------
        # 8. Test User Security Isolation
        # -------------------------------------------------------------
        user_b_progress = CommunicationCoachService.get_communication_progress(db, user_b.id)
        assert user_b_progress["has_data"] is False, "User B should not have access to User A's communication records"
        print("Test 8 (User Security Isolation): PASSED.")

        print("--- ALL PHASE 10 VOICE COMMUNICATION ANALYSIS TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
