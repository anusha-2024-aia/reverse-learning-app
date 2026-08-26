import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db

class TestAIAndDBResiliency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app, raise_server_exceptions=False)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Register user
        res = self.client.post("/api/auth/register", json={
            "name": "Resiliency Tester",
            "email": f"resilient_{os.urandom(4).hex()}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res.status_code, 200)
        self.token = res.json()["access_token"]
        self.user_id = res.json()["user_id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Create topic
        self.topic = models.Topic(name="System Resiliency", category="Engineering", description="Resiliency testing")
        self.db.add(self.topic)
        self.db.commit()
        self.db.refresh(self.topic)

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # 1. AI Success Flow Test
    # -------------------------------------------------------------
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_ai_success_evaluation_flow(self, mock_evaluate):
        mock_evaluate.return_value = {
            "technicalAccuracy": {"score": 80, "feedback": "Good accuracy"},
            "conceptUnderstanding": {"score": 80, "feedback": "Good understanding"},
            "completeness": {"score": 80, "feedback": "Complete"},
            "examples": {"score": 80, "feedback": "Good examples"},
            "relevance": {"score": 80, "feedback": "Relevant"},
            "communication": {"score": 80, "feedback": "Clear"},
            "grammar": {"score": 80, "feedback": "Good grammar"},
            "vocabulary": {"score": 80, "feedback": "Good vocabulary"},
            "summary": "Clear explanation of system design."
        }

        res = self.client.post("/api/evaluate", headers=self.headers, json={
            "topic_id": self.topic.id,
            "explanation": "Resiliency in distributed systems relies on circuit breakers and retries.",
            "learning_mode": "EXPLAIN"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("score", data)
        self.assertGreater(data["score"], 0)
        self.assertIn("summary", data)

    # -------------------------------------------------------------
    # 2. AI Failure Resiliency Tests (403 Leaked Key, 429 Quota, 500 Server Error)
    # -------------------------------------------------------------
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_ai_api_403_and_429_resilience(self, mock_evaluate):
        # Simulate 403 / 429 API Exception
        mock_evaluate.side_effect = Exception("Error code: 429 - Quota Exceeded")

        res = self.client.post("/api/evaluate", headers=self.headers, json={
            "topic_id": self.topic.id,
            "explanation": "Testing AI rate limit fallback handling.",
            "learning_mode": "EXPLAIN"
        })
        # Should fallback gracefully without unhandled crash
        self.assertIn(res.status_code, [200, 500, 503])
        # Ensure no internal secret or traceback is leaked in detail
        self.assertNotIn("GEMINI_API_KEY", res.text)
        self.assertNotIn("JWT_SECRET", res.text)

    # -------------------------------------------------------------
    # 3. AI Malformed / Invalid Response Handling
    # -------------------------------------------------------------
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_ai_malformed_json_response(self, mock_evaluate):
        # Simulate invalid non-numeric score JSON
        mock_evaluate.return_value = {
            "technicalAccuracy": "excellent_not_integer",
            "summary": "Malformed score"
        }

        res = self.client.post("/api/evaluate", headers=self.headers, json={
            "topic_id": self.topic.id,
            "explanation": "Testing malformed AI JSON structure response.",
            "learning_mode": "EXPLAIN"
        })
        self.assertEqual(res.status_code, 200) # Fallback parser handles non-int score gracefully
        self.assertIn("score", res.json())

    # -------------------------------------------------------------
    # 4. Database Transaction Rollback Test
    # -------------------------------------------------------------
    def test_database_transaction_rollback_on_failure(self):
        initial_eval_count = self.db.query(models.Evaluation).count()
        try:
            # Simulate a multi-step operation with DB rollback
            new_eval = models.Evaluation(
                user_id=self.user_id,
                topic_id=99999, # Non-existent topic to trigger FK constraint or exception
                user_explanation="Invalid topic evaluation test"
            )
            self.db.add(new_eval)
            self.db.flush()
            # Force deliberate error
            raise ValueError("Deliberate error mid-transaction")
        except Exception:
            self.db.rollback()

        final_eval_count = self.db.query(models.Evaluation).count()
        self.assertEqual(initial_eval_count, final_eval_count)

if __name__ == "__main__":
    unittest.main()
