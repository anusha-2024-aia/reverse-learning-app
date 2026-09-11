import os
import sys
import uuid
import importlib
import unittest
from datetime import timedelta

# Add backend root directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["JWT_SECRET"] = "test_secure_random_jwt_secret_32bytes_min"

from fastapi.testclient import TestClient
from app.main import app
from app import auth, models
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestJWTSecretSecurity(unittest.TestCase):
    """
    Security verification tests for JWT Secret environment variable configuration,
    fail-fast error handling when missing, token creation, token verification,
    invalid token rejection, and user isolation.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # TEST 1 & TEST 2: Secret Configuration & Fail-Fast Verification
    # -------------------------------------------------------------
    def test_01_secret_exists_configuration_succeeds(self):
        """TEST 1: Given JWT_SECRET environment variable is set, config succeeds."""
        self.assertIsNotNone(auth.SECRET_KEY)
        self.assertTrue(len(auth.SECRET_KEY) > 0)
        self.assertNotEqual(auth.SECRET_KEY, "reverselearn_secret_2026")

    def test_02_secret_missing_fails_clearly(self):
        """TEST 2: Given JWT_SECRET is absent, module initialization fails fast with RuntimeError."""
        old_jwt = os.environ.pop("JWT_SECRET", None)
        old_sec = os.environ.pop("SECRET_KEY", None)

        try:
            with self.assertRaises(RuntimeError) as ctx:
                importlib.reload(auth)
            
            err_msg = str(ctx.exception)
            self.assertIn("JWT secret is not configured", err_msg)
            self.assertIn("JWT_SECRET", err_msg)
            # Ensure actual secret is not leaked in error message
            self.assertNotIn("reverselearn_secret_2026", err_msg)
        finally:
            # Restore environment variables for subsequent tests
            if old_jwt:
                os.environ["JWT_SECRET"] = old_jwt
            else:
                os.environ["JWT_SECRET"] = "test_secure_random_jwt_secret_32bytes_min"
            if old_sec:
                os.environ["SECRET_KEY"] = old_sec
            importlib.reload(auth)

    # -------------------------------------------------------------
    # TEST 3: Login & Token Creation
    # -------------------------------------------------------------
    def test_03_login_generates_jwt_token(self):
        """TEST 3: Valid credentials generate valid JWT token."""
        test_email = f"login_jwt_{uuid.uuid4().hex[:6]}@example.com"
        reg_res = self.client.post("/api/auth/register", json={
            "name": "JWT Login Test User",
            "email": test_email,
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        })
        self.assertEqual(reg_res.status_code, 200)

        login_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "SecurePassword123!"
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("token_type"), "bearer")
        self.assertTrue(len(data["access_token"]) > 20)

    # -------------------------------------------------------------
    # TEST 4: Protected Endpoint Access
    # -------------------------------------------------------------
    def test_04_protected_endpoint_with_valid_jwt(self):
        """TEST 4: Valid JWT allows access to protected endpoints."""
        test_email = f"protected_jwt_{uuid.uuid4().hex[:6]}@example.com"
        reg_res = self.client.post("/api/auth/register", json={
            "name": "Protected Endpoint User",
            "email": test_email,
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        })
        self.assertEqual(reg_res.status_code, 200)
        token = reg_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertEqual(me_data["email"], test_email)

    # -------------------------------------------------------------
    # TEST 5: Invalid or Tampered JWT Rejection
    # -------------------------------------------------------------
    def test_05_invalid_or_tampered_jwt_rejected(self):
        """TEST 5: Invalid/tampered JWT is rejected with 401 Unauthorized."""
        # Malformed token string
        res_malformed = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
        self.assertEqual(res_malformed.status_code, 401)
        body = res_malformed.json()
        self.assertTrue("message" in body or "detail" in body)

        # Token signed with a different secret
        other_secret_token = auth.jwt.encode(
            {"sub": "1"}, "different_unauthorized_secret_key_12345", algorithm=auth.ALGORITHM
        )
        res_wrong_sig = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {other_secret_token}"})
        self.assertEqual(res_wrong_sig.status_code, 401)

        # Expired token
        expired_token = auth.create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-10))
        res_expired = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        self.assertEqual(res_expired.status_code, 401)

    # -------------------------------------------------------------
    # TEST 6: User Isolation Verification
    # -------------------------------------------------------------
    def test_06_user_isolation(self):
        """TEST 6: Verify User A cannot access User B's resources."""
        # Create User A
        email_a = f"iso_a_{uuid.uuid4().hex[:6]}@example.com"
        res_a = self.client.post("/api/auth/register", json={
            "name": "Isolation User A",
            "email": email_a,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_a = res_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Create User B
        email_b = f"iso_b_{uuid.uuid4().hex[:6]}@example.com"
        res_b = self.client.post("/api/auth/register", json={
            "name": "Isolation User B",
            "email": email_b,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_b = res_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User B creates an interview
        res_int_b = self.client.post("/api/interview/start", headers=headers_b, json={
            "target_role": "Security Engineer",
            "difficulty": "MEDIUM",
            "question_count": 3
        })
        self.assertEqual(res_int_b.status_code, 200)
        int_b_id = res_int_b.json()["interview_id"]

        # User A attempts to view User B's interview report -> Must fail with 403 or 404
        res_cross = self.client.get(f"/api/interview/{int_b_id}/report", headers=headers_a)
        self.assertIn(res_cross.status_code, [403, 404])


if __name__ == "__main__":
    unittest.main()
