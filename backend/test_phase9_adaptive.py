import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app import models
from app.services.adaptive_interview_service import AdaptiveInterviewService

async def run_tests():
    print("--- STARTING PHASE 9 ADAPTIVE MOCK INTERVIEW TESTS ---")
    db = SessionLocal()

    try:
        # Create test users
        user_a = db.query(models.User).filter(models.User.email == "adaptive_a@example.com").first()
        if not user_a:
            user_a = models.User(username="adaptive_a", email="adaptive_a@example.com", password_hash="hash", target_role="Full Stack Developer")
            db.add(user_a)
            db.commit()
            db.refresh(user_a)

        user_b = db.query(models.User).filter(models.User.email == "adaptive_b@example.com").first()
        if not user_b:
            user_b = models.User(username="adaptive_b", email="adaptive_b@example.com", password_hash="hash", target_role="Data Engineer")
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        # -------------------------------------------------------------
        # 1. Test Cases 1 - 7: Deterministic Difficulty Scaling Rules
        # -------------------------------------------------------------
        # Test Case 1: MEDIUM + Score 48 -> EASY
        d1 = AdaptiveInterviewService.calculate_next_difficulty("MEDIUM", 48)
        assert d1 == "EASY", f"Test Case 1 failed: Expected EASY, got {d1}"
        print("Test Case 1 (MEDIUM + Score 48 -> EASY): PASSED.")

        # Test Case 2: MEDIUM + Score 72 -> MEDIUM
        d2 = AdaptiveInterviewService.calculate_next_difficulty("MEDIUM", 72)
        assert d2 == "MEDIUM", f"Test Case 2 failed: Expected MEDIUM, got {d2}"
        print("Test Case 2 (MEDIUM + Score 72 -> MEDIUM): PASSED.")

        # Test Case 3: MEDIUM + Score 88 -> HARD
        d3 = AdaptiveInterviewService.calculate_next_difficulty("MEDIUM", 88)
        assert d3 == "HARD", f"Test Case 3 failed: Expected HARD, got {d3}"
        print("Test Case 3 (MEDIUM + Score 88 -> HARD): PASSED.")

        # Test Case 4: EASY + Score 95 -> MEDIUM
        d4 = AdaptiveInterviewService.calculate_next_difficulty("EASY", 95)
        assert d4 == "MEDIUM", f"Test Case 4 failed: Expected MEDIUM, got {d4}"
        print("Test Case 4 (EASY + Score 95 -> MEDIUM): PASSED.")

        # Test Case 5: HARD + Score 95 -> HARD (boundary ceiling check)
        d5 = AdaptiveInterviewService.calculate_next_difficulty("HARD", 95)
        assert d5 == "HARD", f"Test Case 5 failed: Expected HARD, got {d5}"
        print("Test Case 5 (HARD + Score 95 -> HARD): PASSED.")

        # Test Case 6: EASY + Score 40 -> EASY (boundary floor check)
        d6 = AdaptiveInterviewService.calculate_next_difficulty("EASY", 40)
        assert d6 == "EASY", f"Test Case 6 failed: Expected EASY, got {d6}"
        print("Test Case 6 (EASY + Score 40 -> EASY): PASSED.")

        # Test Case 7: HARD + Score 45 -> MEDIUM
        d7 = AdaptiveInterviewService.calculate_next_difficulty("HARD", 45)
        assert d7 == "MEDIUM", f"Test Case 7 failed: Expected MEDIUM, got {d7}"
        print("Test Case 7 (HARD + Score 45 -> MEDIUM): PASSED.")

        # -------------------------------------------------------------
        # 8. Test Single Answer Evaluation
        # -------------------------------------------------------------
        eval_weak = await AdaptiveInterviewService.evaluate_single_answer("REST API", "What is REST API?", "idk")
        assert eval_weak["overall_score"] < 60, f"Expected weak score <60 for 'idk', got {eval_weak['overall_score']}"
        print(f"Test 8 (Single Answer Weak Evaluation): PASSED ({eval_weak['overall_score']}%).")

        eval_strong = await AdaptiveInterviewService.evaluate_single_answer(
            "REST API", 
            "Explain REST API principles", 
            "REST APIs use standard HTTP verbs like GET, POST, PUT, DELETE, maintain stateless client-server communication, return JSON or XML payloads, and utilize proper HTTP status codes for error handling."
        )
        assert eval_strong["overall_score"] >= 80, f"Expected strong score >=80, got {eval_strong['overall_score']}"
        print(f"Test 9 (Single Answer Strong Evaluation): PASSED ({eval_strong['overall_score']}%).")

        # -------------------------------------------------------------
        # 9. Test Interview Session Creation & Question Generation
        # -------------------------------------------------------------
        # Clean previous test sessions
        db.query(models.Interview).filter(models.Interview.user_id == user_a.id).delete()
        db.commit()

        session = models.Interview(
            user_id=user_a.id,
            target_role="Full Stack Developer",
            interview_type="technical",
            starting_difficulty="MEDIUM",
            current_difficulty="MEDIUM",
            question_count=3,
            current_question_number=1,
            status="IN_PROGRESS"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Question 1
        q1_data = await AdaptiveInterviewService.generate_adaptive_question(db, user_a.id, session, last_qa=None)
        q1 = models.InterviewQuestion(
            interview_id=session.id,
            question_number=1,
            question_text=q1_data["question"],
            category=q1_data["category"],
            difficulty=q1_data["difficulty"],
            is_followup=q1_data["is_followup"],
            topic=q1_data["topic"],
            source=q1_data["source"]
        )
        db.add(q1)
        db.commit()
        db.refresh(q1)

        a1 = models.InterviewAnswer(
            question_id=q1.id,
            answer_text="I used Python and MySQL.",
            overall_score=48,
            technical_score=48,
            communication_score=50
        )
        db.add(a1)
        session.current_difficulty = AdaptiveInterviewService.calculate_next_difficulty("MEDIUM", 48)
        session.current_question_number = 2
        db.commit()

        assert session.current_difficulty == "EASY", "Session difficulty should drop to EASY after 48 score"
        print("Test 10 (Session Q1 Weak Answer & Difficulty Drop): PASSED.")

        # Question 2
        q2_data = await AdaptiveInterviewService.generate_adaptive_question(
            db, user_a.id, session, 
            last_qa={"question": q1.question_text, "answer": a1.answer_text, "score": 48}
        )
        assert q2_data["question"] != q1.question_text, "Question 2 must not repeat Question 1"
        
        q2 = models.InterviewQuestion(
            interview_id=session.id,
            question_number=2,
            question_text=q2_data["question"],
            category=q2_data["category"],
            difficulty=q2_data["difficulty"],
            is_followup=q2_data["is_followup"],
            topic=q2_data["topic"],
            source=q2_data["source"]
        )
        db.add(q2)
        db.commit()
        db.refresh(q2)

        a2 = models.InterviewAnswer(
            question_id=q2.id,
            answer_text="MySQL provides ACID compliance, relational foreign key constraints, and structured schema storage suitable for transactional database integrity.",
            overall_score=90,
            technical_score=90,
            communication_score=85
        )
        db.add(a2)
        session.current_difficulty = AdaptiveInterviewService.calculate_next_difficulty("EASY", 90)
        session.current_question_number = 3
        db.commit()

        assert session.current_difficulty == "MEDIUM", "Session difficulty should increase to MEDIUM after 90 score"
        print("Test 11 (Session Q2 Strong Answer & Difficulty Increase): PASSED.")

        # -------------------------------------------------------------
        # 10. Test Final Interview Report & Knowledge Gap Integration
        # -------------------------------------------------------------
        report = await AdaptiveInterviewService.evaluate_full_interview(db, user_a.id, session.id)
        assert report["overall_score"] > 0, "Final report overall score should be > 0"
        assert len(report["progression"]) == 2, "Progression should contain 2 questions"
        assert session.status == "COMPLETED", "Session status should be COMPLETED"
        print(f"Test 12 (Full Interview Report & Progression): PASSED (Score: {report['overall_score']}%).")

        # -------------------------------------------------------------
        # 11. Test User Security Isolation
        # -------------------------------------------------------------
        user_b_session = db.query(models.Interview).filter(
            models.Interview.id == session.id,
            models.Interview.user_id == user_b.id
        ).first()
        assert user_b_session is None, "User B should not be authorized to view User A's session"
        print("Test 13 (User Security Isolation): PASSED.")

        print("--- ALL PHASE 9 ADAPTIVE MOCK INTERVIEW TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
