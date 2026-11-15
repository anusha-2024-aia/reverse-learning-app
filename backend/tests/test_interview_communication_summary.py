import os
import sys
import uuid
import json
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
from app.services.communication_coach_service import CommunicationCoachService
from app.services.adaptive_interview_service import AdaptiveInterviewService
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestInterviewCommunicationSummary(unittest.TestCase):
    """
    Focused unit and integration test suite for Mission 8B-2B:
    - Accurate interview-scoped aggregation of communication metrics
    - Strict isolation: filters by interview_id and user_id, excludes standalone records
    - Handling of voice vs. typed answers (WPM never diluted by null duration)
    - Robustness against malformed JSON or null metrics
    - Error containment: aggregation failure does not block report generation
    - API consistency across final answer submission and GET /report
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

        db = TestingSessionLocal()
        suffix = uuid.uuid4().hex[:6]
        cls.user = models.User(
            name="Summary Test User",
            username=f"summary_user_{suffix}",
            email=f"summary_{suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        cls.user_b = models.User(
            name="Other User",
            username=f"other_user_{suffix}",
            email=f"other_{suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        db.add(cls.user)
        db.add(cls.user_b)
        db.commit()
        db.refresh(cls.user)
        db.refresh(cls.user_b)

        cls.token = auth.create_access_token(data={"sub": cls.user.username})
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        db.close()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        self.interview = models.Interview(
            user_id=self.user.id,
            target_role="Backend Developer",
            interview_type="technical",
            current_difficulty="MEDIUM",
            question_count=2,
            current_question_number=1,
            status="IN_PROGRESS"
        )
        self.db.add(self.interview)
        self.db.commit()
        self.db.refresh(self.interview)

    def tearDown(self):
        self.db.close()

    def test_aggregate_multiple_voice_answers(self):
        """Averages scores and WPM accurately across multiple voice answers; combines fillers and deduplicates grammar tips."""
        rec1 = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=80,
            clarity_score=85,
            grammar_score=90,
            vocabulary_score=80,
            structure_score=85,
            speaking_pace="Good",
            words_per_minute=120,
            filler_word_count=3,
            filler_words_json=json.dumps({"um": 2, "like": 1}),
            grammar_improvements_json=json.dumps([
                {"incorrect": "he go to store", "improved": "he goes to the store", "explanation": "Subject-verb agreement"}
            ]),
            ai_coach_recommendation="Work on reducing filler words."
        )
        rec2 = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=90,
            clarity_score=95,
            grammar_score=80,
            vocabulary_score=90,
            structure_score=95,
            speaking_pace="Good",
            words_per_minute=160,
            filler_word_count=2,
            filler_words_json=json.dumps({"um": 1, "basically": 1}),
            grammar_improvements_json=json.dumps([
                {"incorrect": "he go to store", "improved": "he goes to the store", "explanation": "Subject-verb agreement"},
                {"incorrect": "less people", "improved": "fewer people", "explanation": "Countable nouns"}
            ]),
            ai_coach_recommendation="Pacing was excellent."
        )
        self.db.add_all([rec1, rec2])
        self.db.commit()

        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )

        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_answers_analyzed"], 2)
        self.assertTrue(summary["has_voice_data"])
        # (120 + 160) / 2 = 140
        self.assertEqual(summary["average_wpm"], 140)
        self.assertEqual(summary["overall_speaking_pace"], "Good")
        # (80 + 90) / 2 = 85
        self.assertEqual(summary["average_communication_score"], 85)
        # (85 + 95) / 2 = 90
        self.assertEqual(summary["average_clarity_score"], 90)
        # (90 + 80) / 2 = 85
        self.assertEqual(summary["average_grammar_score"], 85)
        # (80 + 90) / 2 = 85
        self.assertEqual(summary["average_vocabulary_score"], 85)
        # (85 + 95) / 2 = 90
        self.assertEqual(summary["average_structure_score"], 90)

        # Fillers: 3 + 2 = 5
        self.assertEqual(summary["total_filler_words"], 5)
        top_fillers = summary["top_filler_words"]
        self.assertEqual(len(top_fillers), 3)
        self.assertEqual(top_fillers[0], {"word": "um", "count": 3})
        self.assertIn({"word": "like", "count": 1}, top_fillers)
        self.assertIn({"word": "basically", "count": 1}, top_fillers)

        # Grammar improvements deduplicated: 2 unique items
        improvements = summary["grammar_improvements"]
        self.assertEqual(len(improvements), 2)
        self.assertEqual(improvements[0]["incorrect"], "he go to store")
        self.assertEqual(improvements[1]["incorrect"], "less people")
        self.assertEqual(summary["ai_coach_recommendation"], "Pacing was excellent.")

    def test_aggregate_mixed_voice_and_typed_answers(self):
        """Typed answers with no duration/wpm do NOT dilute or reduce the average WPM of voice answers."""
        # Voice answer
        rec_voice = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=80,
            clarity_score=80,
            speaking_pace="Good",
            words_per_minute=150,
            filler_word_count=2,
            filler_words_json=json.dumps({"like": 2})
        )
        # Typed answer (no voice duration, words_per_minute is None)
        rec_typed = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=70,
            clarity_score=70,
            speaking_pace=None,
            words_per_minute=None,
            filler_word_count=0,
            filler_words_json=json.dumps({})
        )
        self.db.add_all([rec_voice, rec_typed])
        self.db.commit()

        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )

        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_answers_analyzed"], 2)
        self.assertTrue(summary["has_voice_data"])
        # Should be 150, NOT (150 + 0) / 2 = 75
        self.assertEqual(summary["average_wpm"], 150)
        self.assertEqual(summary["overall_speaking_pace"], "Good")
        self.assertEqual(summary["average_communication_score"], 75)

    def test_aggregate_all_typed_answers(self):
        """When all answers are typed, has_voice_data is False and average_wpm and pace are None."""
        rec1 = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=75,
            clarity_score=75,
            speaking_pace=None,
            words_per_minute=None
        )
        rec2 = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=85,
            clarity_score=85,
            speaking_pace=None,
            words_per_minute=None
        )
        self.db.add_all([rec1, rec2])
        self.db.commit()

        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )

        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_answers_analyzed"], 2)
        self.assertFalse(summary["has_voice_data"])
        self.assertIsNone(summary["average_wpm"])
        self.assertIsNone(summary["overall_speaking_pace"])
        self.assertEqual(summary["average_communication_score"], 80)

    def test_aggregate_zero_records_returns_none(self):
        """Returns None when no communication analysis records exist for the interview."""
        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )
        self.assertIsNone(summary)

    def test_aggregate_isolation_cross_interview_and_user(self):
        """Strictly excludes records from other interviews, other users, and standalone coach sessions."""
        # 1. Target interview record
        target_rec = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=90,
            words_per_minute=140,
            speaking_pace="Good",
            filler_word_count=1
        )
        # 2. Standalone record for the same user (interview_id is None)
        standalone_rec = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=None,
            communication_score=50,
            words_per_minute=90,
            speaking_pace="Slow",
            filler_word_count=10
        )
        # 3. Different interview for the same user
        other_interview = models.Interview(
            user_id=self.user.id,
            target_role="Frontend Engineer",
            interview_type="technical",
            question_count=1,
            current_question_number=1,
            status="IN_PROGRESS"
        )
        self.db.add(other_interview)
        self.db.commit()
        self.db.refresh(other_interview)

        other_interview_rec = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=other_interview.id,
            communication_score=60,
            words_per_minute=210,
            speaking_pace="Fast",
            filler_word_count=8
        )
        # 4. Record for completely different user
        other_user_rec = models.CommunicationAnalysis(
            user_id=self.user_b.id,
            interview_id=self.interview.id,
            communication_score=40,
            words_per_minute=100,
            speaking_pace="Slow",
            filler_word_count=15
        )

        self.db.add_all([target_rec, standalone_rec, other_interview_rec, other_user_rec])
        self.db.commit()

        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )

        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_answers_analyzed"], 1)
        self.assertEqual(summary["average_communication_score"], 90)
        self.assertEqual(summary["average_wpm"], 140)
        self.assertEqual(summary["overall_speaking_pace"], "Good")
        self.assertEqual(summary["total_filler_words"], 1)

    def test_aggregate_malformed_json_and_none_fields(self):
        """Safely handles invalid JSON in filler_words_json and grammar_improvements_json without failing."""
        rec = models.CommunicationAnalysis(
            user_id=self.user.id,
            interview_id=self.interview.id,
            communication_score=None,
            clarity_score=None,
            grammar_score=None,
            vocabulary_score=None,
            structure_score=None,
            speaking_pace=None,
            words_per_minute=None,
            filler_word_count=None,
            filler_words_json="INVALID_JSON{{{",
            grammar_improvements_json="NOT_A_LIST",
            ai_coach_recommendation=None
        )
        self.db.add(rec)
        self.db.commit()

        summary = CommunicationCoachService.aggregate_interview_communication(
            db=self.db,
            interview_id=self.interview.id,
            user_id=self.user.id
        )

        self.assertIsNotNone(summary)
        self.assertEqual(summary["total_answers_analyzed"], 1)
        self.assertFalse(summary["has_voice_data"])
        # ORM default=70 was applied upon saving
        self.assertEqual(summary["average_communication_score"], 70)
        self.assertIsNone(summary["average_wpm"])
        self.assertEqual(summary["total_filler_words"], 0)
        self.assertEqual(summary["top_filler_words"], [])
        self.assertEqual(summary["grammar_improvements"], [])
        self.assertIsNone(summary["ai_coach_recommendation"])

        # Also verify None handling when scores are truly None (e.g. if nullable in query)
        class MockRecord:
            communication_score = None
            clarity_score = None
            grammar_score = None
            vocabulary_score = None
            structure_score = None
            words_per_minute = None
            speaking_pace = None
            filler_word_count = None
            filler_words_json = None
            grammar_improvements_json = None
            ai_coach_recommendation = None

        with patch.object(self.db, "query") as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = [MockRecord()]
            none_summary = CommunicationCoachService.aggregate_interview_communication(
                db=self.db,
                interview_id=self.interview.id,
                user_id=self.user.id
            )
            self.assertIsNotNone(none_summary)
            self.assertIsNone(none_summary["average_communication_score"])

    @patch("app.services.communication_coach_service.CommunicationCoachService.aggregate_interview_communication")
    async def _run_eval_with_mock(self, mock_aggregate):
        mock_aggregate.side_effect = RuntimeError("Simulated aggregation crash")
        return await AdaptiveInterviewService.evaluate_full_interview(
            db=self.db,
            user_id=self.user.id,
            interview_id=self.interview.id
        )

    def test_evaluate_full_interview_error_containment(self):
        """If aggregate_interview_communication fails, evaluate_full_interview completes and returns report with communication_summary=None."""
        import asyncio
        with patch("app.services.communication_coach_service.CommunicationCoachService.aggregate_interview_communication") as mock_agg:
            mock_agg.side_effect = RuntimeError("Simulated aggregation failure")
            report = asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=self.interview.id
                )
            )

        self.assertIsNotNone(report)
        self.assertIn("overall_score", report)
        self.assertIn("communication_summary", report)
        self.assertIsNone(report["communication_summary"])

    def test_api_consistency_final_answer_and_report_endpoints(self):
        """Verifies that final answer submission and GET /report both return the communication summary consistently."""
        q1 = models.InterviewQuestion(
            interview_id=self.interview.id,
            question_number=1,
            question_text="What is indexing in SQL?",
            category="TECHNICAL",
            difficulty="MEDIUM",
            topic="Databases"
        )
        self.db.add(q1)
        self.db.commit()
        self.db.refresh(q1)

        # Submit answer with is_final=True (triggers report evaluation)
        payload = {
            "interview_id": self.interview.id,
            "current_question_id": q1.id,
            "answer": "Database indexing creates a data structure such as a B-Tree to speed up lookups.",
            "is_final": True,
            "duration_seconds": 12.0
        }

        resp = self.client.post("/api/interview/answer", headers=self.headers, json=payload)
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()

        self.assertTrue(data["is_complete"])
        self.assertIn("report", data)
        report = data["report"]
        self.assertIn("communication_summary", report)

        comm_summary = report["communication_summary"]
        self.assertIsNotNone(comm_summary)
        self.assertTrue(comm_summary["has_voice_data"])
        self.assertIsNotNone(comm_summary["average_wpm"])
        self.assertIn("overall_speaking_pace", comm_summary)

        # Verify GET /api/interview/{id}/report returns the identical saved summary
        report_resp = self.client.get(f"/api/interview/{self.interview.id}/report", headers=self.headers)
        self.assertEqual(report_resp.status_code, 200)
        report_data = report_resp.json()
        self.assertIn("communication_summary", report_data)
        self.assertEqual(report_data["communication_summary"], comm_summary)

        # Verify GET /api/interview/history
        hist_resp = self.client.get("/api/interview/history", headers=self.headers)
        self.assertEqual(hist_resp.status_code, 200)
        history = hist_resp.json()
        self.assertTrue(any(item["id"] == self.interview.id for item in history))


if __name__ == "__main__":
    unittest.main()
