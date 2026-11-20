import os
import unittest
from unittest.mock import patch
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure test mode for rate limiter bypass
os.environ["TESTING"] = "True"

from app.main import app
from app.database import get_db, Base
from app import models, auth
from app.services.demo_service import DEMO_USER_EMAIL, get_or_create_demo_user

TEST_DATABASE_URL = "sqlite:///./test_data_isolation.db"

class TestDataIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)
        if os.path.exists("./test_data_isolation.db"):
            try:
                os.remove("./test_data_isolation.db")
            except Exception:
                pass

    def setUp(self):
        from app.rate_limiter import _LIMITERS
        _LIMITERS.clear()

    def test_01_demo_login_has_maya_lin_data(self):
        """Test that 1-Click Demo Pass authenticates as Maya Lin and contains demo records."""
        res = self.client.post("/api/auth/demo-login")
        self.assertEqual(res.status_code, 200)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check /api/auth/me
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], DEMO_USER_EMAIL)
        self.assertEqual(me_res.json()["name"], "Maya Lin")

        # Check dashboard has Maya's 14-day streak and evaluations
        dash_res = self.client.get("/api/dashboard-data", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertGreaterEqual(dash_data["summary"]["streak"], 14)
        self.assertGreater(dash_data["summary"]["overallScore"], 70)
        self.assertTrue(dash_data["resumeSummary"]["has_resume"])

    def test_02_newly_registered_user_starts_with_clean_account(self):
        """Test that a brand new user starts with 0 score, 0 streak, no resume, and no activity."""
        reg_payload = {
            "name": "Clean Student",
            "email": "clean.student@university.edu",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
            "university": "Stanford University",
            "target_role": "Backend Engineer"
        }
        reg_res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(reg_res.status_code, 200)
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Dashboard data must be completely clean (0 metrics, empty lists)
        dash_res = self.client.get("/api/dashboard-data", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        data = dash_res.json()

        self.assertEqual(data["user"]["name"], "Clean Student")
        self.assertEqual(data["summary"]["overallScore"], 0)
        self.assertEqual(data["summary"]["streak"], 0)
        self.assertEqual(data["summary"]["technicalMastery"], 0)
        self.assertEqual(data["summary"]["interviewReadiness"], 0)
        self.assertEqual(len(data["recentActivity"]), 0)
        self.assertEqual(len(data["strongestTopics"]), 0)
        self.assertEqual(len(data["weakestTopics"]), 0)
        self.assertFalse(data["resumeSummary"]["has_resume"])

        # Resume active endpoint must return has_resume: False
        resume_res = self.client.get("/api/resume/active", headers=headers)
        self.assertEqual(resume_res.status_code, 200)
        self.assertFalse(resume_res.json()["has_resume"])

        # Knowledge gaps endpoint must return empty gaps
        gaps_res = self.client.get("/api/knowledge-gaps", headers=headers)
        self.assertEqual(gaps_res.status_code, 200)
        self.assertEqual(len(gaps_res.json()["gaps"]), 0)

        # Revisions endpoint must return 0 due items
        rev_res = self.client.get("/api/revisions", headers=headers)
        self.assertEqual(rev_res.status_code, 200)
        self.assertEqual(rev_res.json()["summary"]["due_today_count"], 0)

    def test_03_cross_user_isolation(self):
        """Test that User A and User B cannot access each other's data."""
        # Create User A
        res_a = self.client.post("/api/auth/register", json={
            "name": "User Alpha",
            "email": "alpha@test.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_a = res_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Create User B
        res_b = self.client.post("/api/auth/register", json={
            "name": "User Beta",
            "email": "beta@test.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_b = res_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A's dashboard is isolated from User B
        dash_a = self.client.get("/api/dashboard-data", headers=headers_a).json()
        dash_b = self.client.get("/api/dashboard-data", headers=headers_b).json()

        self.assertEqual(dash_a["user"]["name"], "User Alpha")
        self.assertEqual(dash_b["user"]["name"], "User Beta")
        self.assertEqual(dash_a["summary"]["overallScore"], 0)
        self.assertEqual(dash_b["summary"]["overallScore"], 0)

    def test_04_resume_upload_persists_to_correct_user(self):
        """Test that uploading a resume persists to current_user and is not leaked to others."""
        # Register User C
        res_c = self.client.post("/api/auth/register", json={
            "name": "Resume User",
            "email": "resume.user@test.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_c = res_c.json()["access_token"]
        headers_c = {"Authorization": f"Bearer {token_c}"}

        # Register User D (Observer)
        res_d = self.client.post("/api/auth/register", json={
            "name": "Observer User",
            "email": "observer.user@test.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        token_d = res_d.json()["access_token"]
        headers_d = {"Authorization": f"Bearer {token_d}"}

        # Upload resume for User C
        dummy_resume_content = b"%PDF-1.4 dummy valid length resume text with skills Go, Python, Docker, Kubernetes, Linux and projects."
        files = {"file": ("my_resume.pdf", dummy_resume_content, "application/pdf")}
        with patch("app.services.resume_intelligence_service.ResumeIntelligenceService.extract_text", return_value="Skills: Python, Go, Docker. Projects: Distributed System"):
            upload_res = self.client.post("/api/resume/upload", headers=headers_c, files=files)
        self.assertEqual(upload_res.status_code, 200)

        # User C now has active resume
        active_c = self.client.get("/api/resume/active", headers=headers_c)
        self.assertEqual(active_c.status_code, 200)
        self.assertTrue(active_c.json()["has_resume"])
        self.assertEqual(active_c.json()["file_name"], "my_resume.pdf")

        # User D still has NO resume
        active_d = self.client.get("/api/resume/active", headers=headers_d)
        self.assertEqual(active_d.status_code, 200)
        self.assertFalse(active_d.json()["has_resume"])

if __name__ == "__main__":
    unittest.main()
