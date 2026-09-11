import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "True"
os.environ["JWT_SECRET"] = "error_handling_test_secret_key_1234567890"

from app.main import app
from app.auth import create_access_token, hash_password
from app.database import SessionLocal, engine, Base
from app.models import User, Topic, Curriculum
from app.core.exceptions import AppException, ErrorCode, DatabaseException, AIServiceException

client = TestClient(app, raise_server_exceptions=False)

class TestErrorHandlingAndLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == "error_test_user@test.com").first()
            if not user:
                user = User(
                    name="Error Test User",
                    username="error_test_user",
                    email="error_test_user@test.com",
                    password_hash=hash_password("pass123")
                )
                db.add(user)

            cur = db.query(Curriculum).first()
            if not cur:
                cur = Curriculum(name="Error Test Curriculum", description="Test", difficulty="beginner")
                db.add(cur)
                db.commit()
                db.refresh(cur)

            topic = db.query(Topic).first()
            if not topic:
                topic = Topic(name="Error Test Topic", category="Engineering", curriculum_id=cur.id, order_in_curriculum=1)
                db.add(topic)

            db.commit()
            db.refresh(user)
            db.refresh(topic)

            cls.user_id = user.id
            cls.topic_id = topic.id
        finally:
            db.close()

    def setUp(self):
        self.user_token = create_access_token({"sub": str(self.user_id)})
        self.headers = {"Authorization": f"Bearer {self.user_token}"}

    def test_01_valid_api_request_success_response_unchanged(self):
        """TEST 1: Valid API request returns expected success status and schema."""
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})
        self.assertIn("X-Request-ID", res.headers)

    def test_02_validation_error_format(self):
        """TEST 2: Validation error returns HTTP 422 with consistent error format."""
        res = client.post("/api/auth/register", json={"email": "invalid-email-format"})
        self.assertEqual(res.status_code, 422)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.VALIDATION_ERROR)
        self.assertEqual(body["message"], "The request contains invalid data.")
        self.assertIn("details", body)
        self.assertIn("request_id", body)

    def test_03_authentication_failure_format(self):
        """TEST 3: Authentication failure returns HTTP 401 with safe error format."""
        res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_123"})
        self.assertEqual(res.status_code, 401)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.AUTHENTICATION_FAILED)
        self.assertIn("request_id", body)
        self.assertNotIn("secret", str(body).lower())

    def test_04_missing_resource_format(self):
        """TEST 4: Missing resource returns HTTP 404 with safe error format."""
        res = client.get("/api/topics/999999", headers=self.headers)
        self.assertEqual(res.status_code, 404)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.RESOURCE_NOT_FOUND)
        self.assertEqual(body["message"], "Topic not found")
        self.assertIn("request_id", body)

    @patch("app.auth.hash_password")
    def test_05_unexpected_exception_format(self, mock_hash):
        """TEST 5: Unexpected exception returns HTTP 500 without exposing stack trace to user."""
        mock_hash.side_effect = ZeroDivisionError("division by zero internal error")
        import uuid
        res = client.post(
            "/api/auth/register",
            json={"email": f"unexp_{uuid.uuid4().hex[:6]}@test.com", "password": "password123", "name": "Test User"}
        )
        self.assertEqual(res.status_code, 500)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.INTERNAL_SERVER_ERROR)
        self.assertEqual(body["message"], "An unexpected error occurred. Please try again later.")
        self.assertNotIn("ZeroDivisionError", str(body))
        self.assertNotIn("traceback", str(body).lower())

    @patch("sqlalchemy.orm.Session.query")
    def test_06_database_failure_format(self, mock_query):
        """TEST 6: Database failure returns safe DATABASE_ERROR without exposing credentials."""
        mock_query.side_effect = SQLAlchemyError("Internal DB Connection Refused")
        res = client.get("/api/curricula")
        self.assertEqual(res.status_code, 500)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.DATABASE_ERROR)
        self.assertEqual(body["message"], "Unable to complete database operation right now.")
        self.assertNotIn("Connection Refused", str(body))
        self.assertNotIn("postgresql://", str(body))

    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_07_gemini_failure_format(self, mock_gemini):
        """TEST 7: Gemini failure returns safe AI_SERVICE_ERROR without exposing API key."""
        mock_gemini.side_effect = Exception("Gemini API quota exceeded or 503 Service Unavailable")
        res = client.post(
            "/api/evaluate",
            json={"topic_id": self.topic_id, "explanation": "Python is an interpreted programming language."},
            headers=self.headers
        )
        self.assertEqual(res.status_code, 500)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertIn(body["error"], [ErrorCode.AI_SERVICE_ERROR, ErrorCode.INTERNAL_SERVER_ERROR])
        self.assertNotIn("GEMINI_API_KEY", str(body))

    @patch("app.rate_limiter.is_testing_mode", return_value=False)
    @patch("app.rate_limiter.InMemoryRateLimiter.is_rate_limited", return_value=(True, 30, 0))
    def test_08_rate_limit_exceeded_format(self, mock_limiter, mock_test_mode):
        """TEST 8: Rate limit exceeded returns HTTP 429 with consistent format and Retry-After header."""
        res = client.post(
            "/api/evaluate",
            json={"topic_id": self.topic_id, "explanation_text": "Testing rate limit format."},
            headers=self.headers
        )
        self.assertEqual(res.status_code, 429)
        body = res.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], ErrorCode.RATE_LIMIT_EXCEEDED)
        self.assertEqual(body["message"], "Too many requests. Please try again later.")
        self.assertEqual(res.headers.get("Retry-After"), "30")

    @patch("app.main.logger.info")
    def test_09_request_logging_metadata(self, mock_logger_info):
        """TEST 9: Request logging logs method, path, status, and duration without logging passwords."""
        client.get("/health")
        mock_logger_info.assert_called()
        log_message = mock_logger_info.call_args[0][0]
        self.assertIn("method=GET", log_message)
        self.assertIn("path=/health", log_message)
        self.assertIn("status=200", log_message)
        self.assertIn("duration=", log_message)
        self.assertNotIn("password", log_message.lower())
        self.assertNotIn("secret", log_message.lower())

if __name__ == "__main__":
    unittest.main()
