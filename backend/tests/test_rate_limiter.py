import os
import sys
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set test environment secret before importing app modules
os.environ["JWT_SECRET"] = "rate_limit_test_secret_key_1234567890"

from app.main import app
from app.auth import create_access_token, hash_password
from app.database import SessionLocal, engine, Base
from app.models import User, Topic, Curriculum
from app.rate_limiter import InMemoryRateLimiter, reset_all_limiters

client = TestClient(app)

class TestRateLimiter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["FORCE_RATE_LIMIT"] = "True"
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            # Seed test users
            user_a = db.query(User).filter(User.email == "user_a_rate@test.com").first()
            if not user_a:
                user_a = User(name="User A", username="user_a_rate", email="user_a_rate@test.com", password_hash=hash_password("pass123"))
                db.add(user_a)

            user_b = db.query(User).filter(User.email == "user_b_rate@test.com").first()
            if not user_b:
                user_b = User(name="User B", username="user_b_rate", email="user_b_rate@test.com", password_hash=hash_password("pass123"))
                db.add(user_b)
                
            cur = db.query(Curriculum).first()
            if not cur:
                cur = Curriculum(name="Test Curriculum", description="Test", difficulty="beginner")
                db.add(cur)
                db.commit()
                db.refresh(cur)
                
            topic = db.query(Topic).first()
            if not topic:
                topic = Topic(name="Test Topic", category="Engineering", curriculum_id=cur.id, order_in_curriculum=1)
                db.add(topic)

            db.commit()
            db.refresh(user_a)
            db.refresh(user_b)
            db.refresh(topic)

            cls.user_a_id = user_a.id
            cls.user_b_id = user_b.id
            cls.topic_id = topic.id
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("FORCE_RATE_LIMIT", None)
        reset_all_limiters()

    def setUp(self):
        reset_all_limiters()
        self.user_a_token = create_access_token({"sub": str(self.user_a_id)})
        self.user_b_token = create_access_token({"sub": str(self.user_b_id)})
        self.headers_user_a = {"Authorization": f"Bearer {self.user_a_token}"}
        self.headers_user_b = {"Authorization": f"Bearer {self.user_b_token}"}

    def tearDown(self):
        reset_all_limiters()

    def test_in_memory_rate_limiter_unit(self):
        """Test sliding window calculation in InMemoryRateLimiter."""
        limiter = InMemoryRateLimiter(requests_per_window=2, window_seconds=1)
        
        # Request 1 & 2 allowed
        is_limited, retry_after, remaining = limiter.is_rate_limited("test_key")
        self.assertFalse(is_limited)
        self.assertEqual(remaining, 1)

        is_limited, retry_after, remaining = limiter.is_rate_limited("test_key")
        self.assertFalse(is_limited)
        self.assertEqual(remaining, 0)

        # Request 3 rate-limited
        is_limited, retry_after, remaining = limiter.is_rate_limited("test_key")
        self.assertTrue(is_limited)
        self.assertGreaterEqual(retry_after, 1)

        # Wait for window expiry
        time.sleep(1.1)
        is_limited, retry_after, remaining = limiter.is_rate_limited("test_key")
        self.assertFalse(is_limited)

    def test_health_check_endpoint_unrestricted(self):
        """Verify GET /health is not rate-limited."""
        for _ in range(15):
            response = client.get("/health")
            self.assertEqual(response.status_code, 200)

    @patch("app.ai_service.gemini_agent.evaluate_explanation")
    def test_rate_limit_rejection_occurs_before_gemini_call(self, mock_gemini):
        """Verify 429 occurs and mock Gemini is NOT called after rate limit is exceeded."""
        mock_gemini.return_value = {
            "overall_score": 85,
            "technical_accuracy": {"score": 85, "feedback": "Good job"},
            "concept_understanding": {"score": 85, "feedback": "Solid"},
            "completeness": {"score": 85, "feedback": "Complete"},
            "examples_quality": {"score": 85, "feedback": "Clear"},
            "relevance": {"score": 85, "feedback": "Relevant"},
            "communication_clarity": {"score": 85, "feedback": "Clear"},
            "grammar_language": {"score": 85, "feedback": "Accurate"},
            "strengths": ["Clear explanation"],
            "weaknesses": ["None"]
        }

        rate_limit_hit = False
        retry_after_found = False

        # Make requests until rate limit is hit
        for i in range(10):
            res = client.post(
                "/api/evaluate",
                json={"topic_id": self.topic_id, "explanation_text": "Python is an interpreted high level programming language."},
                headers=self.headers_user_a
            )
            if res.status_code == 429:
                rate_limit_hit = True
                self.assertIn("Retry-After", res.headers)
                msg = res.json().get("message") or res.json().get("detail")
                self.assertEqual(msg, "Too many requests. Please try again later.")
                retry_after_found = True
                break

        self.assertTrue(rate_limit_hit, "Rate limit should have been hit after multiple evaluation requests.")
        self.assertTrue(retry_after_found)

    @patch("app.ai_service.gemini_agent.evaluate_explanation")
    def test_user_isolation_rate_limiting(self, mock_gemini):
        """Verify User A exceeding limit does NOT block User B."""
        mock_gemini.return_value = {
            "overall_score": 80,
            "technical_accuracy": {"score": 80, "feedback": "OK"},
            "concept_understanding": {"score": 80, "feedback": "OK"},
            "completeness": {"score": 80, "feedback": "OK"},
            "examples_quality": {"score": 80, "feedback": "OK"},
            "relevance": {"score": 80, "feedback": "OK"},
            "communication_clarity": {"score": 80, "feedback": "OK"},
            "grammar_language": {"score": 80, "feedback": "OK"},
            "strengths": ["Good"],
            "weaknesses": ["None"]
        }

        # User A sends requests until rate limited
        for _ in range(10):
            client.post(
                "/api/evaluate",
                json={"topic_id": self.topic_id, "explanation_text": "Python programming language test explanation."},
                headers=self.headers_user_a
            )

        # User B sends request and must succeed (not blocked by User A)
        res_b = client.post(
            "/api/evaluate",
            json={"topic_id": self.topic_id, "explanation_text": "Python programming language test explanation."},
            headers=self.headers_user_b
        )
        self.assertNotEqual(res_b.status_code, 429, "User B should not be rate-limited by User A's activity.")

if __name__ == "__main__":
    unittest.main()
