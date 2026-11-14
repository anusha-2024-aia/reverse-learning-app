import os
import sys
import uuid
import unittest
from unittest.mock import patch

# Ensure testing flag and environment variables before imports
os.environ["TESTING"] = "True"
os.environ["COMMUNICATION_RATE_LIMIT"] = "100"

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models, auth
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db

class TestCommunicationOwnership(unittest.TestCase):
    """
    Focused regression and security tests for POST /api/communication/analyze
    ensuring strict authorization and ownership validation of interview_id and answer_id.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

        db = TestingSessionLocal()
        # Seed User A directly in DB
        u_a_suffix = uuid.uuid4().hex[:6]
        cls.user_a = models.User(
            name="Comm User A",
            username=f"comm_user_a_{u_a_suffix}",
            email=f"comm_user_a_{u_a_suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        db.add(cls.user_a)

        # Seed User B directly in DB
        u_b_suffix = uuid.uuid4().hex[:6]
        cls.user_b = models.User(
            name="Comm User B",
            username=f"comm_user_b_{u_b_suffix}",
            email=f"comm_user_b_{u_b_suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        db.add(cls.user_b)
        db.commit()
        db.refresh(cls.user_a)
        db.refresh(cls.user_b)

        cls.user_a_id = cls.user_a.id
        cls.user_b_id = cls.user_b.id

        cls.token_a = auth.create_access_token({"sub": str(cls.user_a_id)})
        cls.token_b = auth.create_access_token({"sub": str(cls.user_b_id)})

        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}
        db.close()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.client_patcher = patch("app.services.communication_coach_service.client", None)
        self.client_patcher.start()

        self.db = TestingSessionLocal()

        # Create Interview A for User A with question and answer
        self.interview_a = models.Interview(
            user_id=self.user_a_id,
            target_role="Backend Developer",
            interview_type="technical",
            difficulty="MEDIUM"
        )
        self.db.add(self.interview_a)
        self.db.commit()
        self.db.refresh(self.interview_a)

        self.question_a = models.InterviewQuestion(
            interview_id=self.interview_a.id,
            question_number=1,
            question_text="What is database normalization?",
            category="DATABASE"
        )
        self.db.add(self.question_a)
        self.db.commit()
        self.db.refresh(self.question_a)

        self.answer_a = models.InterviewAnswer(
            question_id=self.question_a.id,
            answer_text="Normalization organizes data to reduce redundancy and improve data integrity."
        )
        self.db.add(self.answer_a)
        self.db.commit()
        self.db.refresh(self.answer_a)

        # Create Interview B for User B with question and answer
        self.interview_b = models.Interview(
            user_id=self.user_b_id,
            target_role="Frontend Developer",
            interview_type="technical",
            difficulty="MEDIUM"
        )
        self.db.add(self.interview_b)
        self.db.commit()
        self.db.refresh(self.interview_b)

        self.question_b = models.InterviewQuestion(
            interview_id=self.interview_b.id,
            question_number=1,
            question_text="Explain CSS box model.",
            category="FRONTEND"
        )
        self.db.add(self.question_b)
        self.db.commit()
        self.db.refresh(self.question_b)

        self.answer_b = models.InterviewAnswer(
            question_id=self.question_b.id,
            answer_text="The box model consists of content, padding, border, and margin."
        )
        self.db.add(self.answer_b)
        self.db.commit()
        self.db.refresh(self.answer_b)

    def tearDown(self):
        self.db.close()
        self.client_patcher.stop()

    # -------------------------------------------------------------
    # 1. Valid interview and answer belonging to current user
    # -------------------------------------------------------------
    def test_valid_interview_and_answer_belonging_to_current_user(self):
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Database normalization eliminates redundancy and ensures relational data consistency across tables.",
            "duration_seconds": 15,
            "interview_id": self.interview_a.id,
            "answer_id": self.answer_a.id
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("analysis_id", data)
        self.assertIn("communication_score", data)

        record = self.db.query(models.CommunicationAnalysis).filter(
            models.CommunicationAnalysis.id == data["analysis_id"]
        ).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.user_id, self.user_a_id)
        self.assertEqual(record.interview_id, self.interview_a.id)
        self.assertEqual(record.answer_id, self.answer_a.id)

    # -------------------------------------------------------------
    # 2. Interview belonging to another user rejected
    # -------------------------------------------------------------
    def test_interview_belonging_to_another_user_rejected(self):
        # User A attempts to associate User B's interview
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Attempting to link User B interview from User A session.",
            "duration_seconds": 10,
            "interview_id": self.interview_b.id,
            "answer_id": self.answer_b.id
        })
        self.assertEqual(res.status_code, 403)
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("Access denied", msg)

        # Reverse check: User B attempts to associate User A's interview
        res_rev = self.client.post("/api/communication/analyze", headers=self.headers_b, json={
            "transcript": "Attempting to link User A interview from User B session.",
            "duration_seconds": 10,
            "interview_id": self.interview_a.id,
            "answer_id": self.answer_a.id
        })
        self.assertEqual(res_rev.status_code, 403)
        msg_rev = res_rev.json().get("message") or res_rev.json().get("detail", "")
        self.assertIn("Access denied", msg_rev)

    # -------------------------------------------------------------
    # 3. Nonexistent interview ID rejected
    # -------------------------------------------------------------
    def test_nonexistent_interview_id_rejected(self):
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Analyzing communication with bogus interview id.",
            "duration_seconds": 12,
            "interview_id": 999999,
            "answer_id": self.answer_a.id
        })
        self.assertEqual(res.status_code, 404)
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("Interview session not found", msg)

    # -------------------------------------------------------------
    # 4. Answer belonging to another interview rejected
    # -------------------------------------------------------------
    def test_answer_belonging_to_another_interview_rejected(self):
        # Create a second interview for User A
        interview_a2 = models.Interview(
            user_id=self.user_a_id,
            target_role="DevOps Engineer",
            interview_type="technical",
            difficulty="HARD"
        )
        self.db.add(interview_a2)
        self.db.commit()
        self.db.refresh(interview_a2)

        # Try to associate answer_a (from interview_a) with interview_a2
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Cross-interview answer injection attempt.",
            "duration_seconds": 10,
            "interview_id": interview_a2.id,
            "answer_id": self.answer_a.id
        })
        self.assertEqual(res.status_code, 404)
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("not found for the referenced interview", msg)

    # -------------------------------------------------------------
    # 5. Nonexistent answer ID rejected
    # -------------------------------------------------------------
    def test_nonexistent_answer_id_rejected(self):
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Analyzing with valid interview but phantom answer id.",
            "duration_seconds": 10,
            "interview_id": self.interview_a.id,
            "answer_id": 888888
        })
        self.assertEqual(res.status_code, 404)
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("Interview answer not found", msg)

    # -------------------------------------------------------------
    # 6. Optional answer_id behavior supported
    # -------------------------------------------------------------
    def test_optional_answer_id_supported(self):
        # interview_id provided, answer_id omitted (None)
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Practice speech for the overall interview session without specific question link.",
            "duration_seconds": 25,
            "interview_id": self.interview_a.id
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("analysis_id", data)

        record = self.db.query(models.CommunicationAnalysis).filter(
            models.CommunicationAnalysis.id == data["analysis_id"]
        ).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.interview_id, self.interview_a.id)
        self.assertIsNone(record.answer_id)

    # -------------------------------------------------------------
    # 7. Standalone analysis without interview or answer supported
    # -------------------------------------------------------------
    def test_standalone_analysis_without_interview_or_answer(self):
        # Both interview_id and answer_id omitted
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Completely standalone speech practice snippet without any interview context.",
            "duration_seconds": 18
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("analysis_id", data)

        record = self.db.query(models.CommunicationAnalysis).filter(
            models.CommunicationAnalysis.id == data["analysis_id"]
        ).first()
        self.assertIsNotNone(record)
        self.assertIsNone(record.interview_id)
        self.assertIsNone(record.answer_id)

    # -------------------------------------------------------------
    # 8. Answer ID provided without interview ID rejected
    # -------------------------------------------------------------
    def test_answer_id_without_interview_id_rejected(self):
        res = self.client.post("/api/communication/analyze", headers=self.headers_a, json={
            "transcript": "Specifying answer_id without any interview_id reference.",
            "duration_seconds": 10,
            "answer_id": self.answer_a.id
        })
        self.assertEqual(res.status_code, 400)
        msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("interview_id is required", msg)

if __name__ == "__main__":
    unittest.main()
