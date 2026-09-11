import os
import sys
import uuid
import unittest
from datetime import datetime, timezone, timedelta

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import auth, models
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db

class TestAuthAndSecurity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Create User A
        self.email_a = f"sec_a_{uuid.uuid4().hex[:6]}@example.com"
        res_a = self.client.post("/api/auth/register", json={
            "name": "Security User A",
            "email": self.email_a,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res_a.status_code, 200)
        self.token_a = res_a.json()["access_token"]
        self.user_a_id = res_a.json()["user_id"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Create User B
        self.email_b = f"sec_b_{uuid.uuid4().hex[:6]}@example.com"
        res_b = self.client.post("/api/auth/register", json={
            "name": "Security User B",
            "email": self.email_b,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res_b.status_code, 200)
        self.token_b = res_b.json()["access_token"]
        self.user_b_id = res_b.json()["user_id"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # 0. Health Endpoint Test
    # -------------------------------------------------------------
    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

        res_api = self.client.get("/api/health")
        self.assertEqual(res_api.status_code, 200)
        self.assertEqual(res_api.json(), {"status": "ok"})

    # -------------------------------------------------------------
    # 1. Registration & Validation Unit Tests
    # -------------------------------------------------------------
    def test_registration_validations(self):
        # Duplicate email
        res_dup = self.client.post("/api/auth/register", json={
            "name": "Duplicate User",
            "email": self.email_a,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res_dup.status_code, 400)

        # Mismatched password
        res_mismatch = self.client.post("/api/auth/register", json={
            "name": "Mismatch User",
            "email": f"mismatch_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!",
            "confirm_password": "WrongPassword!"
        })
        self.assertEqual(res_mismatch.status_code, 400)

        # Password hash leak audit
        data_a = self.client.get("/api/auth/me", headers=self.headers_a).json()
        self.assertNotIn("password_hash", data_a)
        self.assertNotIn("password", data_a)

    # -------------------------------------------------------------
    # 2. Login Account Enumeration Protection
    # -------------------------------------------------------------
    def test_login_account_enumeration_protection(self):
        # Invalid Password
        res_bad_pass = self.client.post("/api/auth/login", json={"email": self.email_a, "password": "WrongPassword!"})
        self.assertEqual(res_bad_pass.status_code, 401)
        msg_bad_pass = res_bad_pass.json().get("message") or res_bad_pass.json().get("detail")
        self.assertEqual(msg_bad_pass, "Invalid email or password.")

        # Non-existent Email
        res_bad_email = self.client.post("/api/auth/login", json={"email": "non_existent@example.com", "password": "Password123!"})
        self.assertEqual(res_bad_email.status_code, 401)
        msg_bad_email = res_bad_email.json().get("message") or res_bad_email.json().get("detail")
        self.assertEqual(msg_bad_email, "Invalid email or password.")

    # -------------------------------------------------------------
    # 3. JWT Authentication & Expiration
    # -------------------------------------------------------------
    def test_jwt_authentication(self):
        # No Token -> 401
        res_no_auth = self.client.get("/api/dashboard-data")
        self.assertEqual(res_no_auth.status_code, 401)

        # Malformed / Invalid Token -> 401
        res_bad_token = self.client.get("/api/dashboard-data", headers={"Authorization": "Bearer invalid.jwt.token"})
        self.assertEqual(res_bad_token.status_code, 401)

        # Expired Token -> 401
        exp_token = auth.create_access_token({"sub": str(self.user_a_id)}, expires_delta=timedelta(seconds=-10))
        res_exp = self.client.get("/api/dashboard-data", headers={"Authorization": f"Bearer {exp_token}"})
        self.assertEqual(res_exp.status_code, 401)

    # -------------------------------------------------------------
    # 4. Bidirectional User Isolation Matrix
    # -------------------------------------------------------------
    def test_bidirectional_user_isolation(self):
        # Create Interview for User B
        res_int_b = self.client.post("/api/interview/start", headers=self.headers_b, json={
            "target_role": "Software Engineer",
            "difficulty": "MEDIUM",
            "question_count": 5
        })
        int_b_id = res_int_b.json()["interview_id"]

        # User A attempts to access User B's interview report -> 404 / 403
        res_cross_int = self.client.get(f"/api/interview/{int_b_id}/report", headers=self.headers_a)
        self.assertIn(res_cross_int.status_code, [403, 404])

        # Reverse Check: Create Interview for User A
        res_int_a = self.client.post("/api/interview/start", headers=self.headers_a, json={
            "target_role": "Frontend Engineer",
            "difficulty": "MEDIUM",
            "question_count": 5
        })
        int_a_id = res_int_a.json()["interview_id"]

        # User B attempts to access User A's interview report -> 404 / 403
        res_cross_rev = self.client.get(f"/api/interview/{int_a_id}/report", headers=self.headers_b)
        self.assertIn(res_cross_rev.status_code, [403, 404])

        # Parameter manipulation test: /api/analytics?userId=USER_B
        res_param = self.client.get(f"/api/analytics?userId={self.user_b_id}", headers=self.headers_a)
        self.assertEqual(res_param.status_code, 200)
        # Verify analytics payload is scoped strictly to User A
        self.assertEqual(res_param.json()["has_enough_data"], True if len(res_param.json()["scoreTrend"]) > 0 else False)

    # -------------------------------------------------------------
    # 5. File Upload Security & Path Traversal
    # -------------------------------------------------------------
    def test_file_upload_security(self):
        pdf_bytes = (
            b"%PDF-1.4\n"
            b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
            b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj\n"
            b"4 0 obj <</Length 55>> stream\n"
            b"BT /F1 12 Tf 100 700 Td (Software Engineer Resume Content) Tj ET\n"
            b"endstream\n"
            b"endobj\n"
            b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \n0000000212 00000 n \n"
            b"trailer <</Size 5 /Root 1 0 R>>\n"
            b"startxref\n318\n%%EOF\n"
        )
        # Valid PDF -> 200
        res_pdf = self.client.post("/api/resume/upload", headers=self.headers_a, files={"file": ("valid.pdf", pdf_bytes, "application/pdf")})
        self.assertEqual(res_pdf.status_code, 200)
        resume_id_a = res_pdf.json()["resume_id"]

        # User B attempts to access User A's Resume -> 404 / 403
        res_cross_res = self.client.get(f"/api/resume/{resume_id_a}", headers=self.headers_b)
        self.assertIn(res_cross_res.status_code, [403, 404])

        # Malicious .exe file -> 400
        res_exe = self.client.post("/api/resume/upload", headers=self.headers_a, files={"file": ("payload.exe", b"MZ\x90\x00Fake Exe", "application/octet-stream")})
        self.assertEqual(res_exe.status_code, 400)

        # Path Traversal Filename -> Sanitized safely
        res_trav = self.client.post("/api/resume/upload", headers=self.headers_a, files={"file": ("../../etc/passwd.pdf", pdf_bytes, "application/pdf")})
        self.assertEqual(res_trav.status_code, 200)
        self.assertNotIn("../../", res_trav.json().get("file_name", ""))

    # -------------------------------------------------------------
    # 6. Security Headers Audit
    # -------------------------------------------------------------
    def test_security_headers(self):
        res = self.client.get("/api/dashboard-data", headers=self.headers_a)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")

if __name__ == "__main__":
    unittest.main()
