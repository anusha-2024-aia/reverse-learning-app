import os
import sys
import uuid
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

class TestE2EUserJourney(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app, raise_server_exceptions=False)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Seed test topic
        self.topic = self.db.query(models.Topic).first()
        if not self.topic:
            self.topic = models.Topic(name="System Architecture", category="Engineering", description="System design principles")
            self.db.add(self.topic)
            self.db.commit()
            self.db.refresh(self.topic)

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # 1. Full E2E User Journey Test
    # -------------------------------------------------------------
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_complete_e2e_user_journey(self, mock_evaluate):
        mock_evaluate.return_value = {
            "technicalAccuracy": {"score": 85, "feedback": "Solid architectural concepts"},
            "conceptUnderstanding": {"score": 80, "feedback": "Good understanding"},
            "completeness": {"score": 80, "feedback": "Complete"},
            "examples": {"score": 80, "feedback": "Good examples"},
            "relevance": {"score": 90, "feedback": "Relevant"},
            "communication": {"score": 85, "feedback": "Clear"},
            "grammar": {"score": 85, "feedback": "Good grammar"},
            "vocabulary": {"score": 85, "feedback": "Good vocabulary"},
            "summary": "Excellent system architecture explanation."
        }

        # Step 1: Register User
        email = f"e2e_{uuid.uuid4().hex[:6]}@example.com"
        res_reg = self.client.post("/api/auth/register", json={
            "name": "E2E Student",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res_reg.status_code, 200)
        token = res_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Login Check
        res_login = self.client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
        self.assertEqual(res_login.status_code, 200)

        # Step 3: View Initial Dashboard
        res_dash1 = self.client.get("/api/dashboard-data", headers=headers)
        self.assertEqual(res_dash1.status_code, 200)

        # Step 4: Submit Concept Evaluation
        res_eval = self.client.post("/api/evaluate", headers=headers, json={
            "topic_id": self.topic.id,
            "explanation": "Microservices communicate asynchronously via message queues for high scalability.",
            "learning_mode": "EXPLAIN"
        })
        self.assertEqual(res_eval.status_code, 200)

        # Step 5: Verify Knowledge Gaps & Recommendations Updated
        res_gaps = self.client.get("/api/dashboard/knowledge-gap/", headers=headers)
        self.assertEqual(res_gaps.status_code, 200)

        # Step 6: Verify Revision Scheduler
        res_rev = self.client.get("/api/revisions", headers=headers)
        self.assertEqual(res_rev.status_code, 200)

        # Step 7: Conduct Adaptive Mock Interview
        res_int = self.client.post("/api/interview/start", headers=headers, json={
            "target_role": "Backend Architect",
            "difficulty": "MEDIUM",
            "question_count": 5
        })
        self.assertEqual(res_int.status_code, 200)
        int_id = res_int.json()["interview_id"]

        # Step 8: Analyze Voice Communication
        res_comm = self.client.post("/api/communication/analyze", headers=headers, json={
            "transcript": "Um, microservices use asynchronous event streams to decouple components, you know.",
            "duration_seconds": 20
        })
        self.assertEqual(res_comm.status_code, 200)

        # Step 9: View Final Analytics
        res_analytics = self.client.get("/api/analytics?range=30d", headers=headers)
        self.assertEqual(res_analytics.status_code, 200)
        data_analytics = res_analytics.json()
        self.assertTrue(data_analytics["has_enough_data"])
        self.assertGreater(data_analytics["summary"]["overallScore"], 0)

    # -------------------------------------------------------------
    # 2. Personalized Resume-to-Interview Journey Test
    # -------------------------------------------------------------
    def test_resume_to_interview_e2e_flow(self):
        # Step 1: Register User
        email = f"resume_e2e_{uuid.uuid4().hex[:6]}@example.com"
        res_reg = self.client.post("/api/auth/register", json={
            "name": "Resume Candidate",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(res_reg.status_code, 200)
        headers = {"Authorization": f"Bearer {res_reg.json()['access_token']}"}

        # Step 2: Upload Valid Resume PDF
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
        res_upload = self.client.post("/api/resume/upload", headers=headers, files={"file": ("candidate_resume.pdf", pdf_bytes, "application/pdf")})
        self.assertEqual(res_upload.status_code, 200)
        resume_id = res_upload.json()["resume_id"]

        # Step 3: Get Resume Profile Details
        res_detail = self.client.get(f"/api/resume/{resume_id}", headers=headers)
        self.assertEqual(res_detail.status_code, 200)

        # Step 4: Start Resume-Personalized Interview
        res_int = self.client.post("/api/interview/start", headers=headers, json={
            "resume_id": resume_id,
            "target_role": "Full Stack Engineer",
            "difficulty": "MEDIUM",
            "question_count": 5
        })
        self.assertEqual(res_int.status_code, 200)
        int_id = res_int.json()["interview_id"]

        # Step 5: Fetch Final Report
        res_report = self.client.get(f"/api/interview/{int_id}/report", headers=headers)
        self.assertEqual(res_report.status_code, 200)

if __name__ == "__main__":
    unittest.main()
