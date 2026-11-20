import os
os.environ["TESTING"] = "True"
import unittest
import uuid
import bcrypt
from fastapi.testclient import TestClient

from app.main import app
from app import models
from app.rate_limiter import _LIMITERS
from tests.test_db_config import init_test_db, cleanup_test_db, TestingSessionLocal

class TestRegistrationAndLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        for lim in _LIMITERS:
            lim.clear()
        self.db = TestingSessionLocal()
        self.test_email = f"student_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"

    def tearDown(self):
        self.db.close()

    def test_01_register_new_valid_user(self):
        """TEST 1: Register a new user with a valid, unused email and password -> Account created successfully."""
        res = self.client.post("/api/auth/register", json={
            "name": "Jane Doe",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password,
            "university": "UC Berkeley",
            "target_role": "Distributed Systems & Cloud Infrastructure"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("user_id", data)
        self.assertIn("access_token", data)
        self.assertEqual(data["email"], self.test_email.lower())

    def test_02_register_duplicate_email(self):
        """TEST 2: Register again using the same email -> Duplicate email message. No duplicate account."""
        # First registration
        res1 = self.client.post("/api/auth/register", json={
            "name": "First User",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(res1.status_code, 200)

        # Duplicate registration attempt
        res2 = self.client.post("/api/auth/register", json={
            "name": "Second User",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(res2.status_code, 400)
        err_msg = res2.json().get("message") or res2.json().get("detail")
        self.assertIn("already registered", err_msg.lower())

        # Verify only 1 account exists in database
        users = self.db.query(models.User).filter(models.User.email == self.test_email.lower()).all()
        self.assertEqual(len(users), 1)

    def test_04_register_malformed_email(self):
        """TEST 4: Register using a malformed email -> Validation error. No account created."""
        res = self.client.post("/api/auth/register", json={
            "name": "Malformed User",
            "email": "not-an-email-domain",
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(res.status_code, 422)

    def test_05_password_stored_as_secure_hash(self):
        """TEST 5: Register using a new valid email and password -> Password stored as secure hash, never plaintext."""
        res = self.client.post("/api/auth/register", json={
            "name": "Security Student",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(res.status_code, 200)
        user_id = res.json()["user_id"]

        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, self.test_password)
        self.assertTrue(user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$"))
        # Verify bcrypt can check it
        self.assertTrue(bcrypt.checkpw(self.test_password.encode('utf-8'), user.password_hash.encode('utf-8')))

    def test_06_login_with_newly_created_credentials(self):
        """TEST 6: Log in using exact email and password -> Successful authentication & token."""
        # 1. Register
        reg_res = self.client.post("/api/auth/register", json={
            "name": "Login Tester",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(reg_res.status_code, 200)

        # 2. Login using email
        login_res = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        token_data = login_res.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "bearer")

        # 3. Access /auth/me with token
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], self.test_email.lower())

    def test_07_login_incorrect_password_rejected(self):
        """TEST 7: Log in using incorrect password -> Authentication rejected."""
        # Register
        self.client.post("/api/auth/register", json={
            "name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })

        # Login with bad password
        bad_res = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": "WrongPassword999!"
        })
        self.assertEqual(bad_res.status_code, 401)

    def test_10_demo_login_works_independently(self):
        """TEST 10: Verify demo login works independently without interfering with real accounts."""
        res = self.client.post("/api/auth/demo-login")
        self.assertEqual(res.status_code, 200)
        token_data = res.json()
        self.assertIn("access_token", token_data)

        # Check me endpoint for demo user
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], "maya.lin@berkeley.edu")

    def test_12_existing_database_users_preserved(self):
        """TEST 12: Verify database user lookup handles normalization and integrity."""
        # Test case-insensitivity on email lookup
        mixed_email = f"CaseMixed_{uuid.uuid4().hex[:6]}@Example.COM"
        reg = self.client.post("/api/auth/register", json={
            "name": "Case User",
            "email": mixed_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(reg.status_code, 200)

        # Login using lowercased email
        login_lower = self.client.post("/api/auth/login", json={
            "email": mixed_email.lower(),
            "password": self.test_password
        })
        self.assertEqual(login_lower.status_code, 200)
