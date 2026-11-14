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

    @patch("app.services.resume_intelligence_service.ResumeIntelligenceService.generate_followup_question")
    def test_resume_interview_answer_rate_limiting(self, mock_followup):
        """Verify POST /api/resume/interview/answer is rate limited and blocks excessive calls."""
        mock_followup.return_value = "What is the complexity of your algorithm?"
        
        hit_429 = False
        for _ in range(10):
            res = client.post(
                "/api/resume/interview/answer",
                json={"interview_id": 999, "answer": "Used binary search.", "is_final": False},
                headers=self.headers_user_a
            )
            if res.status_code == 429:
                hit_429 = True
                self.assertIn("Retry-After", res.headers)
                break

        self.assertTrue(hit_429, "Resume interview answer endpoint should be rate-limited after 5 requests.")

    # -----------------------------------------------------------------
    # Bounded Rate Limiter & LRU Tests (Deterministic Time Mocking)
    # -----------------------------------------------------------------

    def test_invalid_max_keys_rejected(self):
        """Verify invalid max_keys values raise ValueError."""
        for invalid_val in [0, -1, -50, "100", None, 3.14, True, False]:
            with self.subTest(invalid_val=invalid_val):
                with self.assertRaises(ValueError):
                    InMemoryRateLimiter(max_keys=invalid_val)

    @patch("time.time")
    def test_capacity_never_exceeds_max_keys(self, mock_time):
        """Verify dictionary never exceeds the configured max_keys capacity."""
        mock_time.return_value = 1000.0
        max_capacity = 5
        limiter = InMemoryRateLimiter(requests_per_window=10, window_seconds=60, max_keys=max_capacity)

        for i in range(25):
            limiter.is_rate_limited(f"client_ip_{i}")
            self.assertLessEqual(len(limiter.requests), max_capacity)

        self.assertEqual(len(limiter.requests), max_capacity)

    @patch("time.time")
    def test_least_recently_used_key_is_evicted(self, mock_time):
        """Verify the least recently used key is evicted when max_keys is reached."""
        mock_time.return_value = 1000.0
        limiter = InMemoryRateLimiter(requests_per_window=5, window_seconds=60, max_keys=3)

        limiter.is_rate_limited("key_a")
        limiter.is_rate_limited("key_b")
        limiter.is_rate_limited("key_c")
        self.assertEqual(list(limiter.requests.keys()), ["key_a", "key_b", "key_c"])

        # Inserting key_d should evict key_a (oldest in LRU order)
        limiter.is_rate_limited("key_d")
        self.assertEqual(list(limiter.requests.keys()), ["key_b", "key_c", "key_d"])
        self.assertNotIn("key_a", limiter.requests)

    @patch("time.time")
    def test_accessing_key_updates_lru_position(self, mock_time):
        """Verify accessing an existing key updates its LRU position so it is not evicted next."""
        mock_time.return_value = 1000.0
        limiter = InMemoryRateLimiter(requests_per_window=5, window_seconds=60, max_keys=3)

        limiter.is_rate_limited("key_a")
        limiter.is_rate_limited("key_b")
        limiter.is_rate_limited("key_c")
        self.assertEqual(list(limiter.requests.keys()), ["key_a", "key_b", "key_c"])

        # Access key_a again: should move key_a to the end (MRU)
        limiter.is_rate_limited("key_a")
        self.assertEqual(list(limiter.requests.keys()), ["key_b", "key_c", "key_a"])

        # Now inserting key_d should evict key_b (new LRU), keeping key_a
        limiter.is_rate_limited("key_d")
        self.assertEqual(list(limiter.requests.keys()), ["key_c", "key_a", "key_d"])
        self.assertIn("key_a", limiter.requests)
        self.assertNotIn("key_b", limiter.requests)

    @patch("time.time")
    def test_expired_timestamps_removed_when_key_accessed_again(self, mock_time):
        """Verify expired timestamps are pruned when the same key makes a new request."""
        mock_time.return_value = 1000.0
        limiter = InMemoryRateLimiter(requests_per_window=3, window_seconds=60, max_keys=10)

        limiter.is_rate_limited("client_x")
        mock_time.return_value = 1020.0
        limiter.is_rate_limited("client_x")
        self.assertEqual(limiter.requests["client_x"], [1000.0, 1020.0])

        # Advance time to t=1070.0 (cutoff is 1070 - 60 = 1010.0)
        # Timestamp 1000.0 is expired (< 1010.0), 1020.0 is still valid (> 1010.0)
        mock_time.return_value = 1070.0
        is_limited, _, remaining = limiter.is_rate_limited("client_x")
        self.assertFalse(is_limited)
        self.assertEqual(limiter.requests["client_x"], [1020.0, 1070.0])
        self.assertEqual(remaining, 1)

    @patch("time.time")
    def test_empty_entries_not_retained(self, mock_time):
        """Verify empty timestamp lists are never retained in the requests dictionary."""
        mock_time.return_value = 1000.0
        limiter = InMemoryRateLimiter(requests_per_window=2, window_seconds=30, max_keys=10)

        limiter.is_rate_limited("client_y")
        self.assertIn("client_y", limiter.requests)
        for val in limiter.requests.values():
            self.assertGreater(len(val), 0)

        # Advance time far beyond window (t=1100.0, cutoff = 1070.0)
        mock_time.return_value = 1100.0
        limiter.is_rate_limited("client_y")
        self.assertEqual(limiter.requests["client_y"], [1100.0])
        for val in limiter.requests.values():
            self.assertGreater(len(val), 0)

    @patch("time.time")
    def test_sliding_window_limits_and_retry_after(self, mock_time):
        """Verify exact sliding-window quota and Retry-After calculation."""
        mock_time.return_value = 1000.0
        limiter = InMemoryRateLimiter(requests_per_window=2, window_seconds=40, max_keys=10)

        # Request 1: allowed, 1 remaining
        limited, retry, rem = limiter.is_rate_limited("key_z")
        self.assertFalse(limited)
        self.assertEqual(rem, 1)
        self.assertEqual(retry, 0)

        # Request 2 (t=1010): allowed, 0 remaining
        mock_time.return_value = 1010.0
        limited, retry, rem = limiter.is_rate_limited("key_z")
        self.assertFalse(limited)
        self.assertEqual(rem, 0)
        self.assertEqual(retry, 0)

        # Request 3 (t=1025): rate limited! Oldest=1000.0, window=40, expires=1040.0.
        # Retry-After = 1040 - 1025 = 15 seconds
        mock_time.return_value = 1025.0
        limited, retry, rem = limiter.is_rate_limited("key_z")
        self.assertTrue(limited)
        self.assertEqual(retry, 15)
        self.assertEqual(rem, 0)

        # Request 4 (t=1041): oldest 1000.0 expired (cutoff=1001.0). Allowed!
        mock_time.return_value = 1041.0
        limited, retry, rem = limiter.is_rate_limited("key_z")
        self.assertFalse(limited)
        self.assertEqual(rem, 0)

if __name__ == "__main__":
    unittest.main()
