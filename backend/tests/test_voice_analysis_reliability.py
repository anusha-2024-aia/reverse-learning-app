import os
import sys
import uuid
import unittest
from unittest.mock import patch

# Ensure testing flag and environment variables before imports
os.environ["TESTING"] = "True"
os.environ["INTERVIEW_RATE_LIMIT"] = "100"

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models, auth
from app.schemas import SubmitAnswerRequest
from app.services.communication_coach_service import CommunicationCoachService
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestVoiceAnalysisReliability(unittest.TestCase):
    """
    Focused unit and integration tests for Mission 8B-1:
    - Backend error containment: Communication analysis failures never break answer submission.
    - Transaction safety: Failed communication analysis does not rollback or delete primary InterviewAnswer.
    - Speaking pace: WPM calculated only with valid positive duration; missing/zero duration gives None.
    - Pace classification: Word count alone never produces Slow/Good/Fast.
    - Frontend contract: communication_analysis is properly returned for MockInterview consumption.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

        db = TestingSessionLocal()
        # Seed test user
        suffix = uuid.uuid4().hex[:6]
        cls.user = models.User(
            name="Voice Test User",
            username=f"voice_user_{suffix}",
            email=f"voice_{suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        db.add(cls.user)
        db.commit()
        db.refresh(cls.user)

        cls.token = auth.create_access_token(data={"sub": cls.user.username})
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        db.close()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Create a fresh interview session and question for each test
        self.interview = models.Interview(
            user_id=self.user.id,
            target_role="Software Engineer",
            interview_type="technical",
            current_difficulty="MEDIUM",
            question_count=5,
            current_question_number=1,
            status="IN_PROGRESS"
        )
        self.db.add(self.interview)
        self.db.commit()
        self.db.refresh(self.interview)

        self.question = models.InterviewQuestion(
            interview_id=self.interview.id,
            question_number=1,
            question_text="Explain the difference between a process and a thread.",
            category="TECHNICAL",
            difficulty="MEDIUM",
            topic="Operating Systems"
        )
        self.db.add(self.question)
        self.db.commit()
        self.db.refresh(self.question)

    def tearDown(self):
        self.db.close()

    # 1. Speaking pace unit tests
    def test_wpm_calculation_with_valid_positive_duration(self):
        """Valid duration and positive word count produce accurate WPM."""
        # 30 words in 15 seconds -> 120 WPM
        words_30 = "one two three four five six seven eight nine ten " * 3
        res = CommunicationCoachService.analyze_speaking_pace(words_30, duration_seconds=15.0)
        self.assertEqual(res["wpm"], 120)
        self.assertEqual(res["pace"], "Good")
        self.assertIsNone(res["pause_count"])

        # 10 words in 10 seconds -> 60 WPM -> Slow (< 110)
        words_10 = "one two three four five six seven eight nine ten"
        res_slow = CommunicationCoachService.analyze_speaking_pace(words_10, duration_seconds=10.0)
        self.assertEqual(res_slow["wpm"], 60)
        self.assertEqual(res_slow["pace"], "Slow")
        self.assertIsNone(res_slow["pause_count"])

        # 100 words in 20 seconds -> 300 WPM -> Fast (> 185)
        words_100 = "word " * 100
        res_fast = CommunicationCoachService.analyze_speaking_pace(words_100, duration_seconds=20.0)
        self.assertEqual(res_fast["wpm"], 300)
        self.assertEqual(res_fast["pace"], "Fast")
        self.assertIsNone(res_fast["pause_count"])

    def test_valid_duration_does_not_produce_fabricated_pause_count(self):
        """Verifies that even with long duration and few words, pause_count is None and not fabricated."""
        text = "Short sentence with high duration."
        res = CommunicationCoachService.analyze_speaking_pace(text, duration_seconds=60.0)
        self.assertIsNone(res["pause_count"], "pause_count was fabricated using baseline formula!")
        self.assertEqual(res["pace"], "Slow")
        self.assertIsNotNone(res["wpm"])

    def test_wpm_none_and_no_pace_when_duration_is_missing_or_invalid(self):
        """Missing, zero, negative, boolean, or NaN duration returns wpm=None and pace=None."""
        words = "This is a detailed technical explanation of operating system processes and threads."

        # Missing duration (None)
        res_none = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds=None)
        self.assertIsNone(res_none["wpm"])
        self.assertIsNone(res_none["pace"])
        self.assertIsNone(res_none["pause_count"])

        # Zero duration
        res_zero = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds=0)
        self.assertIsNone(res_zero["wpm"])
        self.assertIsNone(res_zero["pace"])

        # Negative duration
        res_neg = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds=-10.5)
        self.assertIsNone(res_neg["wpm"])
        self.assertIsNone(res_neg["pace"])

        # Boolean duration (isinstance(True, int) is True in Python, must be caught)
        res_bool = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds=True)
        self.assertIsNone(res_bool["wpm"])
        self.assertIsNone(res_bool["pace"])

        # String invalid duration
        res_str = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds="invalid")
        self.assertIsNone(res_str["wpm"])
        self.assertIsNone(res_str["pace"])

        # NaN duration
        res_nan = CommunicationCoachService.analyze_speaking_pace(words, duration_seconds=float("nan"))
        self.assertIsNone(res_nan["wpm"])
        self.assertIsNone(res_nan["pace"])

    def test_word_count_alone_never_classifies_pace(self):
        """Verifies that short, medium, and long responses without duration NEVER receive Slow/Good/Fast pace ratings."""
        short_text = "Short answer."
        med_text = "This is a moderately long answer describing memory isolation between processes."
        long_text = "Process and thread differences include memory space, context switching overhead, and concurrency. " * 15

        for text in [short_text, med_text, long_text]:
            res = CommunicationCoachService.analyze_speaking_pace(text, duration_seconds=None)
            self.assertIsNone(res["pace"], f"Pace was classified from word count alone for text: {text[:20]}")
            self.assertIsNone(res["wpm"])

    # 2. Pydantic schema validation
    def test_submit_answer_request_schema_duration_validation(self):
        """SubmitAnswerRequest validates duration_seconds and normalizes invalid values to None."""
        # Valid float
        req1 = SubmitAnswerRequest(interview_id=1, answer="valid answer text", duration_seconds=12.5)
        self.assertEqual(req1.duration_seconds, 12.5)

        # Negative float -> normalized to None
        req2 = SubmitAnswerRequest(interview_id=1, answer="valid answer text", duration_seconds=-5.0)
        self.assertIsNone(req2.duration_seconds)

        # Zero -> normalized to None
        req3 = SubmitAnswerRequest(interview_id=1, answer="valid answer text", duration_seconds=0)
        self.assertIsNone(req3.duration_seconds)

        # Boolean True -> normalized to None
        req4 = SubmitAnswerRequest(interview_id=1, answer="valid answer text", duration_seconds=True)
        self.assertIsNone(req4.duration_seconds)

        # None -> None
        req5 = SubmitAnswerRequest(interview_id=1, answer="valid answer text", duration_seconds=None)
        self.assertIsNone(req5.duration_seconds)

    # 3. Backend error containment integration tests
    @patch("app.services.communication_coach_service.CommunicationCoachService.process_and_save_communication_analysis")
    def test_communication_failure_does_not_break_interview_answer_submission(self, mock_comm):
        """When CommunicationCoachService throws an unhandled exception, POST /interview/answer succeeds with HTTP 200."""
        mock_comm.side_effect = RuntimeError("Simulated Gemini API timeout or crash")

        payload = {
            "interview_id": self.interview.id,
            "current_question_id": self.question.id,
            "answer": "A process has its own address space, whereas threads share the memory of their process.",
            "is_final": False,
            "duration_seconds": 15.0
        }

        response = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")

        data = response.json()
        self.assertIn("eval_result", data)
        self.assertIn("overall_score", data["eval_result"])
        # communication_analysis should be None due to error containment
        self.assertIsNone(data["communication_analysis"])
        self.assertIn("next_question", data)

    @patch("app.services.communication_coach_service.CommunicationCoachService.process_and_save_communication_analysis")
    def test_failed_communication_transaction_does_not_undo_primary_interview_answer(self, mock_comm):
        """A failure in communication analysis must NOT rollback or delete the primary InterviewAnswer record."""
        mock_comm.side_effect = Exception("Database constraint violation in communication table")

        submitted_answer = "Processes have separate memory spaces. Threads share the heap and code segment."
        payload = {
            "interview_id": self.interview.id,
            "current_question_id": self.question.id,
            "answer": submitted_answer,
            "is_final": False,
            "duration_seconds": 20.0
        }

        response = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)

        # Verify that the primary InterviewAnswer was persisted in the database and survived
        db = TestingSessionLocal()
        saved_ans = db.query(models.InterviewAnswer).filter(
            models.InterviewAnswer.question_id == self.question.id
        ).first()

        self.assertIsNotNone(saved_ans, "Primary InterviewAnswer was rolled back or not persisted!")
        self.assertEqual(saved_ans.answer_text, submitted_answer)
        self.assertIsNotNone(saved_ans.technical_score)
        self.assertIsNotNone(saved_ans.overall_score)
        db.close()

    def test_successful_answer_with_valid_duration_includes_communication_analysis(self):
        """Submitting an answer with valid duration returns full communication analysis and WPM."""
        payload = {
            "interview_id": self.interview.id,
            "current_question_id": self.question.id,
            "answer": "A process is an executing program instance with independent virtual memory. Threads exist within a process and share resources.",
            "is_final": False,
            "duration_seconds": 10.0
        }

        response = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        comm = data.get("communication_analysis")
        self.assertIsNotNone(comm, "Expected communication_analysis in response")
        self.assertIn("communication_score", comm)
        self.assertIn("clarity_score", comm)
        self.assertIn("grammar_score", comm)
        self.assertIn("filler_word_count", comm)
        # 19 words / 10s * 60 = 114 WPM -> Good
        self.assertIsNotNone(comm["words_per_minute"])
        self.assertGreater(comm["words_per_minute"], 0)
        self.assertEqual(comm["speaking_pace"], "Good")

    def test_manually_typed_answer_without_duration_has_no_wpm(self):
        """Manually typed answers without duration_seconds receive wpm=None and speaking_pace=None without fabrication."""
        payload = {
            "interview_id": self.interview.id,
            "current_question_id": self.question.id,
            "answer": "Processes have distinct address spaces. Threads share state.",
            "is_final": False
            # duration_seconds omitted
        }

        response = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        comm = data.get("communication_analysis")
        self.assertIsNotNone(comm)
        self.assertIsNone(comm["words_per_minute"], "WPM was fabricated for typed answer without duration!")
        self.assertIsNone(comm["speaking_pace"], "Speaking pace was fabricated for typed answer without duration!")

    @patch("app.services.communication_coach_service.CommunicationCoachService.process_and_save_communication_analysis")
    def test_communication_rollback_preserves_difficulty_and_progression(self, mock_comm):
        """
        When communication analysis fails and triggers rollback, verifies that:
        1. InterviewAnswer remains saved.
        2. Difficulty transition is correctly persisted to the Interview record in the database.
        3. Interview question progression (current_question_number) remains correct.
        """
        mock_comm.side_effect = RuntimeError("Simulated communication crash")

        # Initial state: question 1, difficulty MEDIUM
        self.assertEqual(self.interview.current_difficulty, "MEDIUM")
        self.assertEqual(self.interview.current_question_number, 1)

        payload = {
            "interview_id": self.interview.id,
            "current_question_id": self.question.id,
            "answer": "This is an outstanding technical answer clearly defining virtual memory and execution contexts with extensive detail and examples.",
            "is_final": False,
            "duration_seconds": 15.0
        }

        response = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNone(data["communication_analysis"])
        self.assertEqual(data["current_step"], 2)

        # Inspect database directly
        db = TestingSessionLocal()
        # 1. InterviewAnswer remains saved
        saved_ans = db.query(models.InterviewAnswer).filter(
            models.InterviewAnswer.question_id == self.question.id
        ).first()
        self.assertIsNotNone(saved_ans, "InterviewAnswer was lost after communication rollback!")
        self.assertEqual(saved_ans.answer_text, payload["answer"])

        # 2. Difficulty transition is correctly persisted in database
        updated_interview = db.query(models.Interview).filter(
            models.Interview.id == self.interview.id
        ).first()
        self.assertIsNotNone(updated_interview)
        self.assertEqual(updated_interview.current_difficulty, data["new_difficulty"])

        # 3. Question progression is correct
        self.assertEqual(updated_interview.current_question_number, 2)
        db.close()


if __name__ == "__main__":
    unittest.main()
