import os
import sys
import uuid
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db

class TestProductionVerificationGate(unittest.TestCase):
    """
    Complete Pre-Production Verification Suite:
    Executes real cross-feature workflows (1-7), strict data isolation checks,
    and end-to-end integration validations across all layers.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app, raise_server_exceptions=False)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        self.topic = self.db.query(models.Topic).first()
        if not self.topic:
            cur = self.db.query(models.Curriculum).first()
            if not cur:
                cur = models.Curriculum(name="Distributed Systems", description="Core distributed systems")
                self.db.add(cur)
                self.db.commit()
                self.db.refresh(cur)
            self.topic = models.Topic(
                name="Distributed Consensus (Raft)",
                category="Engineering",
                curriculum_id=cur.id,
                description="Consensus protocol fundamentals and leader election"
            )
            self.db.add(self.topic)
            self.db.commit()
            self.db.refresh(self.topic)

    def tearDown(self):
        self.db.close()

    def _register_and_login(self, name_prefix="Student"):
        uid = uuid.uuid4().hex[:8]
        email = f"{name_prefix.lower()}_{uid}@example.com"
        password = "SecurePassword2025!"
        reg_res = self.client.post("/api/auth/register", json={
            "name": f"{name_prefix} {uid}",
            "email": email,
            "password": password,
            "confirm_password": password
        })
        self.assertEqual(reg_res.status_code, 200, f"Registration failed: {reg_res.text}")
        token = reg_res.json()["access_token"]
        return email, password, token, {"Authorization": f"Bearer {token}"}

    # =========================================================================
    # WORKFLOW 1: Register -> Login -> Dashboard -> Explore Topic -> Complete Activity -> Dashboard Update -> History Update
    # =========================================================================
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_workflow_1_register_to_learning_history(self, mock_evaluate):
        mock_evaluate.return_value = {
            "technicalAccuracy": {"score": 90, "feedback": "Accurate leader election mechanics"},
            "conceptUnderstanding": {"score": 88, "feedback": "Good understanding of terms"},
            "completeness": {"score": 85, "feedback": "Complete coverage"},
            "examples": {"score": 80, "feedback": "Practical scenarios"},
            "relevance": {"score": 95, "feedback": "Directly relevant"},
            "communication": {"score": 90, "feedback": "Clear explanation"},
            "grammar": {"score": 90, "feedback": "Good grammar"},
            "vocabulary": {"score": 85, "feedback": "Strong terminology"},
            "summary": "Outstanding mastery of distributed consensus."
        }

        email, password, token, headers = self._register_and_login("WorkflowOne")

        # 1. Login
        login_res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        self.assertEqual(login_res.status_code, 200)

        # 2. Clean initial dashboard
        dash_initial = self.client.get("/api/dashboard-data", headers=headers).json()
        self.assertEqual(dash_initial["summary"]["overallScore"], 0)

        # 3. Explore topic details
        topic_res = self.client.get(f"/api/topics/{self.topic.id}", headers=headers)
        self.assertEqual(topic_res.status_code, 200)

        # 4. Ask AI Tutor
        ask_res = self.client.post(f"/api/topics/{self.topic.id}/ask-ai", json={
            "question": "Why does Raft require an odd number of voting nodes like 5 vs 6?"
        }, headers=headers)
        self.assertEqual(ask_res.status_code, 200)
        self.assertIn("Quorum", ask_res.json()["answer"])

        # 5. Complete Learning Activity / Evaluation
        eval_res = self.client.post("/api/evaluate", headers=headers, json={
            "topic_id": self.topic.id,
            "explanation": "In Raft, consensus requires a strict majority quorum Q = floor(N/2) + 1.",
            "learning_mode": "technical"
        })
        self.assertEqual(eval_res.status_code, 200)

        # 6. Dashboard reflects updated mastery
        dash_updated = self.client.get("/api/dashboard-data", headers=headers).json()
        self.assertGreater(dash_updated["summary"]["overallScore"], 0)

        # 7. Learning history updated
        evals_mine = self.client.get("/api/evaluations/mine", headers=headers).json()
        self.assertTrue(len(evals_mine) >= 1)
        self.assertEqual(evals_mine[0]["topic_id"], self.topic.id)

    # =========================================================================
    # WORKFLOW 2: Login -> Diagnostic / Evaluation -> Evaluation Returned -> Saved -> Gaps Update -> Dashboard
    # =========================================================================
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_workflow_2_diagnostic_and_knowledge_gaps(self, mock_evaluate):
        # Return lower score to trigger knowledge gap detection (< 70)
        mock_evaluate.return_value = {
            "technicalAccuracy": {"score": 50, "feedback": "Misconception regarding log compaction"},
            "conceptUnderstanding": {"score": 55, "feedback": "Confusion between term and index"},
            "completeness": {"score": 50, "feedback": "Omitted commit index"},
            "examples": {"score": 40, "feedback": "No examples provided"},
            "relevance": {"score": 60, "feedback": "Partially relevant"},
            "communication": {"score": 60, "feedback": "Vague phrasing"},
            "grammar": {"score": 70, "feedback": "Acceptable grammar"},
            "vocabulary": {"score": 55, "feedback": "Missing keywords"},
            "summary": "Critical gap in distributed log replication semantics."
        }

        email, password, token, headers = self._register_and_login("DiagUser")

        # Initial gaps check: empty
        gaps_initial = self.client.get("/api/knowledge-gaps", headers=headers).json()
        self.assertEqual(len(gaps_initial.get("gaps", [])), 0)

        # Submit diagnostic explanation
        eval_res = self.client.post("/api/evaluate", headers=headers, json={
            "topic_id": self.topic.id,
            "explanation": "Nodes send logs whenever they want without commit indices.",
            "learning_mode": "explain"
        })
        self.assertEqual(eval_res.status_code, 200)

        # Gaps updated
        gaps_updated = self.client.get("/api/knowledge-gaps", headers=headers).json()
        self.assertTrue(len(gaps_updated.get("gaps", [])) >= 1)

        # Dashboard knowledge-gap widget reflects weakest topic
        weakest_res = self.client.get("/api/dashboard/knowledge-gap", headers=headers).json()
        self.assertTrue(weakest_res["has_gap"])
        self.assertEqual(weakest_res["topic_id"], self.topic.id)

    # =========================================================================
    # WORKFLOW 3: Upload Resume -> Analyze -> Save -> View Skills/Gaps -> Persistence
    # =========================================================================
    @patch("app.services.resume_intelligence_service.ResumeIntelligenceService.extract_text")
    def test_workflow_3_resume_upload_and_persistence(self, mock_extract):
        mock_extract.return_value = (
            "Senior Systems Engineer with expertise in Distributed Systems, Kubernetes, Go, Python, "
            "Kafka, and High-Throughput Microservices. Built consensus engines and database storage."
        )

        _, _, _, headers = self._register_and_login("ResumeUser")

        # Initial active resume: None
        active_initial = self.client.get("/api/resume/active", headers=headers).json()
        self.assertFalse(active_initial["has_resume"])

        # Upload synthetic PDF bytes >= 50 bytes
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Senior Engineer Resume) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
        upload_res = self.client.post(
            "/api/resume/upload",
            headers=headers,
            files={"file": ("systems_architect.pdf", dummy_pdf, "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 200)
        resume_data = upload_res.json()
        self.assertIn("resume_id", resume_data)

        # Verify active resume retrieval
        active_retrieved = self.client.get("/api/resume/active", headers=headers).json()
        self.assertTrue(active_retrieved["has_resume"])
        self.assertEqual(active_retrieved["resume_id"], resume_data["resume_id"])
        self.assertEqual(active_retrieved["file_name"], "systems_architect.pdf")

    # =========================================================================
    # WORKFLOW 4: Start Mock Interview -> Submit Answers -> Save Attempt -> Analytics
    # =========================================================================
    def test_workflow_4_mock_interview_lifecycle(self):
        _, _, _, headers = self._register_and_login("InterviewUser")

        # Start interview
        start_res = self.client.post("/api/interview/start", headers=headers, json={
            "target_role": "Cloud Architect",
            "difficulty": "MEDIUM",
            "question_count": 3
        })
        self.assertEqual(start_res.status_code, 200)
        int_data = start_res.json()
        int_id = int_data["interview_id"]
        q_id = int_data["question_id"]

        # Submit answer
        ans_res = self.client.post("/api/interview/answer", headers=headers, json={
            "interview_id": int_id,
            "current_question_id": q_id,
            "answer": "We enforce idempotency by using a unique requestId generated at the client and persisted in a Redis cache."
        })
        self.assertEqual(ans_res.status_code, 200)

        # Check interview history
        history_res = self.client.get("/api/interview/history", headers=headers).json()
        self.assertTrue(len(history_res) >= 1)

    # =========================================================================
    # WORKFLOW 5: Learning Activity -> Revision Record -> Smart Revision Flow
    # =========================================================================
    @patch("app.routes.evaluations_routes.evaluate_explanation")
    def test_workflow_5_smart_revision_lifecycle(self, mock_evaluate):
        mock_evaluate.return_value = {
            "technicalAccuracy": {"score": 88, "feedback": "Good"},
            "conceptUnderstanding": {"score": 85, "feedback": "Good"},
            "completeness": {"score": 85, "feedback": "Good"},
            "examples": {"score": 80, "feedback": "Good"},
            "relevance": {"score": 90, "feedback": "Good"},
            "communication": {"score": 85, "feedback": "Good"},
            "grammar": {"score": 85, "feedback": "Good"},
            "vocabulary": {"score": 85, "feedback": "Good"},
            "summary": "Solid explanation."
        }

        _, _, _, headers = self._register_and_login("RevisionUser")

        # Complete evaluation to generate revision schedule
        self.client.post("/api/evaluate", headers=headers, json={
            "topic_id": self.topic.id,
            "explanation": "Consensus ensures state machines execute identical command logs in exact order.",
            "learning_mode": "technical"
        })

        # Fetch revisions summary
        rev_summary = self.client.get("/api/revisions/summary", headers=headers).json()
        self.assertIn("total_scheduled", rev_summary)

        # Complete revision session
        rev_complete = self.client.post(f"/api/revisions/{self.topic.id}/complete", headers=headers, json={
            "explanation": "Re-reviewed Raft leader heartbeat interval and election timeout randomization.",
            "learning_mode": "technical"
        })
        self.assertEqual(rev_complete.status_code, 200)
        self.assertEqual(rev_complete.json()["topic_id"], self.topic.id)

    # =========================================================================
    # WORKFLOW 6: Virtual Study Session -> Save -> History -> Analytics
    # =========================================================================
    def test_workflow_6_virtual_study_session_logging(self):
        _, _, _, headers = self._register_and_login("FocusUser")

        # Log focus session
        log_res = self.client.post("/api/sessions/live-focus", headers=headers, json={
            "topic_id": self.topic.id,
            "duration_minutes": 45,
            "objective": "Deep study of Paxos synod and multi-paxos protocol",
            "notes": "Reviewed prepared phase and accept phase message exchanges."
        })
        self.assertEqual(log_res.status_code, 200)

        # Mine sessions
        sessions = self.client.get("/api/sessions/mine", headers=headers).json()
        self.assertTrue(len(sessions) >= 1)

        # Analytics reflects study session
        analytics = self.client.get("/api/analytics", headers=headers).json()
        self.assertIn("summary", analytics)
        self.assertIn("learningActivity", analytics)

    # =========================================================================
    # WORKFLOW 7: Strict Demo Account vs New User Isolation
    # =========================================================================
    def test_workflow_7_demo_vs_new_user_isolation(self):
        # 1. Login as Demo Maya Lin
        demo_login_res = self.client.post("/api/auth/demo-login")
        self.assertEqual(demo_login_res.status_code, 200)
        demo_headers = {"Authorization": f"Bearer {demo_login_res.json()['access_token']}"}

        # Demo profile should be Maya Lin
        demo_me = self.client.get("/api/auth/me", headers=demo_headers).json()
        self.assertIn("Maya", demo_me["name"])

        # 2. Register fresh new student
        _, _, _, new_headers = self._register_and_login("CompletelyClean")

        # New user profile is independent
        new_me = self.client.get("/api/auth/me", headers=new_headers).json()
        self.assertNotIn("Maya", new_me["name"])

        # New user has 0 items and no demo data
        new_dash = self.client.get("/api/dashboard-data", headers=new_headers).json()
        self.assertEqual(new_dash["summary"]["overallScore"], 0)
        self.assertEqual(new_dash["summary"]["streak"], 0)

        new_resume = self.client.get("/api/resume/active", headers=new_headers).json()
        self.assertFalse(new_resume["has_resume"])

    # =========================================================================
    # PHASE 4: Cross-User Boundary Attack Tests (User A vs User B)
    # =========================================================================
    @patch("app.services.resume_intelligence_service.ResumeIntelligenceService.extract_text")
    def test_cross_user_boundary_access_denied(self, mock_extract):
        mock_extract.return_value = "Secret Confidential Resume of User A"

        _, _, _, headers_a = self._register_and_login("UserA")
        _, _, _, headers_b = self._register_and_login("UserB")

        # User A uploads resume (>= 50 bytes)
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Secret Confidential Resume A) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
        up_res = self.client.post(
            "/api/resume/upload",
            headers=headers_a,
            files={"file": ("secret_resume_a.pdf", dummy_pdf, "application/pdf")}
        )
        self.assertEqual(up_res.status_code, 200)
        resume_id_a = up_res.json()["resume_id"]

        # User B attempts to access User A's resume directly by ID
        b_access = self.client.get(f"/api/resume/{resume_id_a}", headers=headers_b)
        self.assertEqual(b_access.status_code, 404, "User B was illegally able to read User A's resume!")

        # User B checks active resume: must be empty
        b_active = self.client.get("/api/resume/active", headers=headers_b).json()
        self.assertFalse(b_active["has_resume"])

if __name__ == "__main__":
    unittest.main()
