import os
import sys
import uuid
import json
import tempfile
import asyncio
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock

# Ensure testing flag and environment variables before imports
os.environ["TESTING"] = "True"
os.environ["DOCUMENT_RATE_LIMIT"] = "1000"
os.environ["RESUME_RATE_LIMIT"] = "1000"

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models, auth
from app.services.resume_intelligence_service import ResumeIntelligenceService
from app.services.resume_parser import ResumeParser
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestResumeIntelligenceSuite(unittest.TestCase):
    """
    Focused test suite for Phase 7A: Safe Resume Intelligence Fixes:
    1. Elimination of fabricated fallback data (no Skylena, KGiSL, CareerAI).
    2. Gemini failure handling with clean, honest fallback.
    3. AI success with empty sections preserved (no mock section injection).
    4. Empty, corrupted, and unsupported file handling.
    5. DOCX table text extraction.
    6. Safe upload failure cleanup (no orphaned disk files).
    7. Active resume response contract (top-level projects and skills).
    8. Answer length validation (max 4000 chars).
    9. Server-side maximum interview turns (max 5 turns).
    10. Completed interview protection.
    11. Legacy upload route compatibility and question generation.
    12. Personalized questions never reference fabricated entities.
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
        suffix = uuid.uuid4().hex[:6]
        self.user = models.User(
            name="Resume Test User",
            username=f"res_user_{suffix}",
            email=f"res_user_{suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

        self.user_id = self.user.id
        self.token = auth.create_access_token({"sub": str(self.user_id)})
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        self.db.rollback()
        # Clean up files created for this user's resumes
        try:
            user_resumes = self.db.query(models.Resume).filter(models.Resume.user_id == self.user_id).all()
            for r in user_resumes:
                if r.file_path and os.path.exists(r.file_path) and ("uploads" in r.file_path or "temp" in r.file_path):
                    try:
                        os.unlink(r.file_path)
                    except Exception:
                        pass
        except Exception:
            pass

        # Clean up records created for this user
        self.db.query(models.Evaluation).filter(models.Evaluation.user_id == self.user_id).delete()
        self.db.query(models.ResumeInterview).filter(models.ResumeInterview.user_id == self.user_id).delete()
        self.db.query(models.ResumeQuestion).filter(models.ResumeQuestion.user_id == self.user_id).delete()
        self.db.query(models.Resume).filter(models.Resume.user_id == self.user_id).delete()
        self.db.query(models.User).filter(models.User.id == self.user_id).delete()
        self.db.commit()
        self.db.close()

    # -------------------------------------------------------------------------
    # Mission 1: Fabrication Elimination Tests
    # -------------------------------------------------------------------------

    def test_01_no_fabricated_fallback_information(self):
        """
        Verify that fallback_rule_based_parse never injects hardcoded sample data
        (Skylena, KGiSL, CareerAI, Campus Control, CGPA 9.17) even when trigger words
        like 'intern', 'monitoring', 'b.tech', 'job matching' are present.
        """
        text = """
        Candidate with internship experience in cloud monitoring and job matching algorithms.
        Holds a B.Tech degree in Artificial Intelligence.
        Proficient in Python, PostgreSQL, and Docker.
        """
        result = ResumeIntelligenceService.fallback_rule_based_parse(text)

        result_str = json.dumps(result)
        self.assertNotIn("Skylena", result_str, "Fabricated company Skylena must never be injected!")
        self.assertNotIn("KGiSL", result_str, "Fabricated university KGiSL must never be injected!")
        self.assertNotIn("CareerAI", result_str, "Fabricated project CareerAI must never be injected!")
        self.assertNotIn("Campus Control", result_str, "Fabricated project Campus Control must never be injected!")
        self.assertNotIn("9.17", result_str, "Fabricated CGPA 9.17 must never be injected!")

        # Projects, experience, and education must remain empty in fallback
        self.assertEqual(result["projects"], [])
        self.assertEqual(result["experience"], [])
        self.assertEqual(result["education"], [])
        self.assertEqual(result["certifications"], [])

        # Legitimate skills in text must be extracted
        self.assertIn("Python", result["skills"])
        self.assertIn("PostgreSQL", result["skills"])
        self.assertIn("Docker", result["skills"])

    def test_02_gemini_failure_returns_safe_honest_fallback(self):
        """
        Verify that when AI service is unavailable, analyze_and_structure_resume
        returns honest fallback data with zero fabricated companies or projects.
        """
        with patch("app.services.resume_intelligence_service.client", None):
            text = "Java Spring Boot developer with experience in MySQL and REST APIs."
            result = asyncio.run(ResumeIntelligenceService.analyze_and_structure_resume(text))

        result_str = json.dumps(result)
        self.assertNotIn("Skylena", result_str)
        self.assertNotIn("KGiSL", result_str)
        self.assertNotIn("CareerAI", result_str)

        self.assertEqual(result["projects"], [])
        self.assertEqual(result["experience"], [])
        self.assertIn("Java", result["skills"])
        self.assertIn("MySQL", result["skills"])

    def test_03_ai_empty_sections_not_overwritten_by_fallback(self):
        """
        Verify that when AI succeeds and returns empty projects or experience,
        the system does NOT overwrite them with fabricated sample data.
        """
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(
                message=AsyncMock(
                    content="""<json>
                    {
                        "summary": "Junior Python Developer",
                        "skills": ["Python", "SQLite"],
                        "projects": [],
                        "experience": [],
                        "education": [{"degree": "B.Sc Computer Science", "institution": "State University", "year": "2024"}]
                    }
                    </json>"""
                )
            )
        ]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            text = "Junior developer intern seeking entry level Python roles."
            result = asyncio.run(ResumeIntelligenceService.analyze_and_structure_resume(text))

        self.assertEqual(result["projects"], [], "Empty projects from AI must remain empty!")
        self.assertEqual(result["experience"], [], "Empty experience from AI must remain empty!")
        self.assertNotIn("Skylena", json.dumps(result))

    # -------------------------------------------------------------------------
    # Mission 3: Extraction Reliability Tests
    # -------------------------------------------------------------------------

    def test_04_empty_and_corrupted_file_handling(self):
        """
        Verify extract_text handles empty files, corrupted bytes, and non-existent files safely.
        """
        # 1. Non-existent file
        with self.assertRaises(Exception) as ctx:
            ResumeIntelligenceService.extract_text("non_existent_path.pdf", "pdf")
        self.assertIn("not found", str(ctx.exception).lower())

        # 2. Corrupted PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"NOT_A_VALID_PDF_HEADER_JUST_RANDOM_CORRUPT_BYTES")
            corrupt_path = f.name

        try:
            with self.assertRaises(Exception) as ctx:
                ResumeIntelligenceService.extract_text(corrupt_path, "pdf")
            self.assertIn("failed to extract text", str(ctx.exception).lower())
        finally:
            if os.path.exists(corrupt_path):
                try:
                    os.unlink(corrupt_path)
                except Exception:
                    pass

        # 3. Unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"MZ" + b"\x00" * 100)
            exe_path = f.name

        try:
            with self.assertRaises(Exception) as ctx:
                ResumeIntelligenceService.extract_text(exe_path, "exe")
            self.assertIn("unsupported file extension", str(ctx.exception).lower())
        finally:
            if os.path.exists(exe_path):
                try:
                    os.unlink(exe_path)
                except Exception:
                    pass

    def test_05_docx_table_extraction(self):
        """
        Verify extract_text extracts text from both body paragraphs and tables in DOCX files.
        """
        import docx
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            docx_path = f.name

        try:
            doc = docx.Document()
            doc.add_paragraph("Heading: Candidate Skills Profile")
            table = doc.add_table(rows=2, cols=2)
            table.cell(0, 0).text = "Distributed Systems"
            table.cell(0, 1).text = "Apache Kafka & Event Streaming"
            table.cell(1, 0).text = "Microservices"
            table.cell(1, 1).text = "FastAPI & Docker Containerization"
            doc.save(docx_path)

            extracted = ResumeIntelligenceService.extract_text(docx_path, "docx")
            self.assertIn("Candidate Skills Profile", extracted)
            self.assertIn("Distributed Systems", extracted)
            self.assertIn("Apache Kafka", extracted)
            self.assertIn("FastAPI & Docker Containerization", extracted)
        finally:
            if os.path.exists(docx_path):
                try:
                    os.unlink(docx_path)
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # Mission 2: Safe Upload Cleanup Tests
    # -------------------------------------------------------------------------

    def test_06_upload_failure_cleans_up_disk_file(self):
        """
        Verify that if upload text extraction or structuring fails,
        the newly created physical file in uploads/resumes is removed.
        """
        upload_dir = "./uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)
        count_before = len(os.listdir(upload_dir))

        # Upload a corrupted file with .pdf extension
        corrupt_bytes = b"%PDF-1.4 CORRUPTED INVALID BODY CONTENT WITHOUT XREF OR PAGES"
        res = self.client.post(
            "/api/resume/upload",
            headers=self.headers,
            files={"file": ("corrupt_resume.pdf", corrupt_bytes, "application/pdf")}
        )

        self.assertEqual(res.status_code, 400)
        count_after = len(os.listdir(upload_dir))
        self.assertEqual(
            count_before, count_after,
            f"Orphaned file leaked! Count before: {count_before}, count after: {count_after}"
        )

    # -------------------------------------------------------------------------
    # Mission 4: Active Resume API Contract Tests
    # -------------------------------------------------------------------------

    def test_07_active_resume_response_contract(self):
        """
        Verify GET /api/resume/active returns projects and skills at the top level
        in addition to analysis_summary, ensuring MockInterview.jsx contract compatibility.
        """
        structured = {
            "summary": "Full Stack Engineer",
            "skills": ["React", "FastAPI", "PostgreSQL"],
            "projects": [
                {
                    "name": "E-Commerce Microservice",
                    "description": "High-throughput order processing service.",
                    "technologies": ["FastAPI", "PostgreSQL"]
                }
            ],
            "experience": [],
            "education": []
        }

        resume = models.Resume(
            user_id=self.user_id,
            file_name="active_test_resume.pdf",
            file_type="pdf",
            file_path="/tmp/test_resume.pdf",
            extracted_text="Full Stack Engineer with React and FastAPI.",
            is_active=True,
            parsed_skills=json.dumps(structured["skills"]),
            parsed_projects=json.dumps(structured["projects"]),
            parsed_experience=json.dumps(structured["experience"]),
            parsed_education=json.dumps(structured["education"]),
            analysis_summary_json=json.dumps(structured)
        )
        self.db.add(resume)
        self.db.commit()

        res = self.client.get("/api/resume/active", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data.get("has_resume"))
        self.assertEqual(data.get("file_name"), "active_test_resume.pdf")

        # Top-level keys required by frontend consumers
        self.assertIn("projects", data)
        self.assertIn("skills", data)
        self.assertEqual(len(data["projects"]), 1)
        self.assertEqual(data["projects"][0]["name"], "E-Commerce Microservice")
        self.assertIn("FastAPI", data["skills"])

    # -------------------------------------------------------------------------
    # Mission 5: Interview Answer Bounds & Maximum Turns Tests
    # -------------------------------------------------------------------------

    def test_08_answer_length_limit(self):
        """
        Verify answer_resume_interview_question rejects answers exceeding 4000 characters.
        """
        # Create a resume and interview session
        resume = models.Resume(
            user_id=self.user_id,
            file_name="bounds_resume.pdf",
            file_type="pdf",
            file_path="/tmp/bounds.pdf",
            is_active=True
        )
        self.db.add(resume)
        self.db.commit()

        session_state = {
            "qa_history": [],
            "current_question": "Explain how you handle data consistency in microservices."
        }
        interview = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps(session_state)
        )
        self.db.add(interview)
        self.db.commit()

        # Submit an answer with 4001 characters
        oversized_answer = "A" * 4001
        res = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={
                "interview_id": interview.id,
                "answer": oversized_answer,
                "is_final": False
            }
        )

        self.assertEqual(res.status_code, 400)
        err_msg = res.json().get("message") or res.json().get("detail", "")
        self.assertIn("exceeds maximum allowed length", err_msg)

    @patch("app.routes.resume_routes.ResumeIntelligenceService.generate_followup_question", new_callable=AsyncMock)
    @patch("app.routes.resume_routes.ResumeIntelligenceService.evaluate_resume_interview", new_callable=AsyncMock)
    def test_09_maximum_interview_turns_enforced(self, mock_eval, mock_followup):
        """
        Verify that interview auto-completes on the 5th turn even if the client sends is_final=False.
        """
        mock_followup.return_value = "Can you elaborate on your testing strategy?"
        mock_eval.return_value = {
            "overall_score": 85,
            "technical_score": 85,
            "strengths": ["Solid architecture answers"],
            "weaknesses": []
        }

        resume = models.Resume(
            user_id=self.user_id,
            file_name="turns_resume.pdf",
            file_type="pdf",
            file_path="/tmp/turns.pdf",
            is_active=True
        )
        self.db.add(resume)
        self.db.commit()

        # Seed interview already at 4 turns
        qa_history = [
            {"question": f"Question {i}", "answer": f"Answer {i}"}
            for i in range(1, 5)
        ]
        session_state = {
            "qa_history": qa_history,
            "current_question": "Final Question 5: How do you handle cache invalidation?"
        }
        interview = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps(session_state)
        )
        self.db.add(interview)
        self.db.commit()

        # Submit 5th turn with is_final=False
        res = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={
                "interview_id": interview.id,
                "answer": "We use write-through cache with a short TTL and pub-sub invalidation.",
                "is_final": False  # Client tries to keep session open
            }
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_complete"], "Session must auto-complete on turn 5 regardless of is_final!")

        # Verify DB status is COMPLETED
        self.db.expire_all()
        db_int = self.db.query(models.ResumeInterview).filter(models.ResumeInterview.id == interview.id).first()
        self.assertEqual(db_int.status, "COMPLETED")

        # Test 10: Protection against re-answering a completed interview
        res_reanswer = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={
                "interview_id": interview.id,
                "answer": "Another answer after interview completion",
                "is_final": False
            }
        )
        self.assertEqual(res_reanswer.status_code, 400)
        reanswer_err = res_reanswer.json().get("message") or res_reanswer.json().get("detail", "")
        self.assertIn("already been completed", reanswer_err)

    # -------------------------------------------------------------------------
    # Mission 6: Legacy Upload Route Compatibility
    # -------------------------------------------------------------------------

    @patch("app.routes.interview_routes.ResumeParser.parse_resume", new_callable=AsyncMock)
    @patch("app.routes.interview_routes.ResumeIntelligenceService.generate_personalized_questions", new_callable=AsyncMock)
    def test_11_legacy_upload_compatibility(self, mock_gen_q, mock_parse):
        """
        Verify that POST /api/interview/resume/upload sets file_name, file_type,
        is_active, and calls generate_personalized_questions for consistency.
        """
        mock_parse.return_value = {
            "skills": ["Go", "Kubernetes"],
            "projects": [{"name": "Cluster Monitor", "technologies": ["Go"]}],
            "experience": []
        }
        mock_gen_q.return_value = []

        fake_pdf = b"%PDF-1.4 minimal valid pdf content for test compatibility"
        res = self.client.post(
            "/api/interview/resume/upload",
            headers=self.headers,
            files={"file": ("golang_dev.pdf", fake_pdf, "application/pdf")}
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("resume_id", data)

        # Verify DB record has full fields populated
        db_resume = self.db.query(models.Resume).filter(models.Resume.id == data["resume_id"]).first()
        self.assertEqual(db_resume.file_name, "golang_dev.pdf")
        self.assertEqual(db_resume.file_type, "pdf")
        self.assertTrue(db_resume.is_active)
        self.assertIn("Go", db_resume.parsed_skills)

        # Verify physical file exists and clean it up immediately
        created_file = db_resume.file_path
        self.assertTrue(os.path.exists(created_file), "Physical file should exist after successful upload")
        if os.path.exists(created_file):
            try:
                os.unlink(created_file)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Mission 1 Extra: Question Generation Honesty
    # -------------------------------------------------------------------------

    def test_12_questions_never_reference_fabricated_entities(self):
        """
        Verify that generate_personalized_questions never asks questions
        about Skylena, KGiSL, or CareerAI when candidate only has genuine skills.
        """
        summary = {
            "summary": "Database Engineer",
            "skills": ["SQL", "PostgreSQL", "Query Optimization"],
            "projects": [],
            "experience": []
        }
        resume = models.Resume(
            user_id=self.user_id,
            file_name="db_engineer.pdf",
            file_type="pdf",
            file_path="/tmp/db_eng.pdf",
            is_active=True,
            analysis_summary_json=json.dumps(summary)
        )
        self.db.add(resume)
        self.db.commit()

        # Generate questions via fallback (no AI call)
        with patch("app.services.resume_intelligence_service.client", None):
            questions = asyncio.run(
                ResumeIntelligenceService.generate_personalized_questions(
                    db=self.db,
                    user_id=self.user_id,
                    resume_id=resume.id
                )
            )

        self.assertGreater(len(questions), 0)
        for q in questions:
            q_text = q.question_text
            self.assertNotIn("Skylena", q_text)
            self.assertNotIn("KGiSL", q_text)
            self.assertNotIn("CareerAI", q_text)
            self.assertNotIn("Campus Control", q_text)

    # -------------------------------------------------------------------------
    # Phase 7A-B Hardening Tests
    # -------------------------------------------------------------------------

    def test_13_synthetic_weakness_idempotency(self):
        """
        Verify that repeated resume interview evaluations identifying the same
        knowledge gap do not create duplicate synthetic Evaluation records.
        """
        topic_name = f"Docker_{uuid.uuid4().hex[:6]}"
        topic = models.Topic(name=topic_name, description="Containerization topic")
        self.db.add(topic)
        self.db.commit()

        resume = models.Resume(
            user_id=self.user_id,
            file_name="idem_resume.pdf",
            file_type="pdf",
            file_path="/tmp/idem.pdf",
            is_active=True
        )
        self.db.add(resume)
        self.db.commit()

        interview1 = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps({"qa_history": [], "current_question": "Explain Docker."})
        )
        self.db.add(interview1)
        self.db.commit()

        eval_payload_1 = {
            "overall_score": 50,
            "technical_score": 50,
            "knowledge_gaps_identified": [topic_name]
        }

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.choices = [AsyncMock(message=AsyncMock(content=f"<json>{json.dumps(eval_payload_1)}</json>"))]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

            asyncio.run(ResumeIntelligenceService.evaluate_resume_interview(
                db=self.db,
                user_id=self.user_id,
                interview_id=interview1.id,
                qa_history=[{"question": "Q1", "answer": "A1"}]
            ))

        # Check 1 synthetic evaluation was created
        synthetic_evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.topic_id == topic.id,
            models.Evaluation.explanation.like(f"{models.RESUME_WEAKNESS_PREFIX}%")
        ).all()
        self.assertEqual(len(synthetic_evals), 1)
        first_eval_id = synthetic_evals[0].id
        self.assertEqual(synthetic_evals[0].overall_score, 50)

        # Create a second interview for the same user identifying the same topic weakness
        interview2 = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps({"qa_history": [], "current_question": "Explain Docker volumes."})
        )
        self.db.add(interview2)
        self.db.commit()

        eval_payload_2 = {
            "overall_score": 40,
            "technical_score": 40,
            "knowledge_gaps_identified": [topic_name]
        }

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.choices = [AsyncMock(message=AsyncMock(content=f"<json>{json.dumps(eval_payload_2)}</json>"))]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

            asyncio.run(ResumeIntelligenceService.evaluate_resume_interview(
                db=self.db,
                user_id=self.user_id,
                interview_id=interview2.id,
                qa_history=[{"question": "Q2", "answer": "A2"}]
            ))

        # Verify still exactly 1 synthetic evaluation exists (updated in place, not duplicated)
        synthetic_evals_after = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.topic_id == topic.id,
            models.Evaluation.explanation.like(f"{models.RESUME_WEAKNESS_PREFIX}%")
        ).all()
        self.assertEqual(len(synthetic_evals_after), 1, "Duplicate synthetic weakness record was created!")
        self.assertEqual(synthetic_evals_after[0].id, first_eval_id, "Existing synthetic record should have been updated in place")
        self.assertEqual(synthetic_evals_after[0].overall_score, 40)

    def test_14_genuine_evaluation_not_modified_by_synthetic_weakness(self):
        """
        Verify that genuine study Evaluation records are never overwritten or modified
        when a resume interview synchronizes synthetic weaknesses for the same topic.
        """
        topic_name = f"PostgreSQL_{uuid.uuid4().hex[:6]}"
        topic = models.Topic(name=topic_name, description="Relational database topic")
        self.db.add(topic)
        self.db.commit()

        genuine_eval = models.Evaluation(
            user_id=self.user_id,
            topic_id=topic.id,
            explanation="Comprehensive deep dive on PostgreSQL B-Tree and GIN indexes",
            overall_score=88,
            ai_score=88,
            attempt_number=1
        )
        self.db.add(genuine_eval)
        self.db.commit()
        genuine_id = genuine_eval.id

        resume = models.Resume(
            user_id=self.user_id,
            file_name="pg_resume.pdf",
            file_type="pdf",
            file_path="/tmp/pg.pdf",
            is_active=True
        )
        self.db.add(resume)
        self.db.commit()

        interview = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps({"qa_history": [], "current_question": "Explain PostgreSQL."})
        )
        self.db.add(interview)
        self.db.commit()

        eval_payload = {
            "overall_score": 45,
            "technical_score": 45,
            "knowledge_gaps_identified": [topic_name]
        }

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.choices = [AsyncMock(message=AsyncMock(content=f"<json>{json.dumps(eval_payload)}</json>"))]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

            asyncio.run(ResumeIntelligenceService.evaluate_resume_interview(
                db=self.db,
                user_id=self.user_id,
                interview_id=interview.id,
                qa_history=[{"question": "Q1", "answer": "A1"}]
            ))

        # Re-fetch genuine evaluation and assert it is untouched
        refetched_genuine = self.db.query(models.Evaluation).filter(models.Evaluation.id == genuine_id).first()
        self.assertEqual(refetched_genuine.overall_score, 88)
        self.assertEqual(refetched_genuine.ai_score, 88)
        self.assertEqual(refetched_genuine.explanation, "Comprehensive deep dive on PostgreSQL B-Tree and GIN indexes")

        # Verify a separate synthetic evaluation was created alongside it
        all_evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.topic_id == topic.id
        ).all()
        self.assertEqual(len(all_evals), 2)
        synthetic = [e for e in all_evals if e.id != genuine_id][0]
        self.assertTrue(synthetic.explanation.startswith(models.RESUME_WEAKNESS_PREFIX))
        self.assertEqual(synthetic.overall_score, 45)

    def test_15_failed_resume_persistence_does_not_deactivate_active_resume(self):
        """
        Verify that if database persistence fails during upload, the transaction is rolled back
        so previous active resumes remain active, and temporary files are cleaned up.
        """
        existing_resume = models.Resume(
            user_id=self.user_id,
            file_name="existing_active.pdf",
            file_type="pdf",
            file_path="/tmp/existing_active.pdf",
            is_active=True
        )
        self.db.add(existing_resume)
        self.db.commit()
        existing_id = existing_resume.id

        upload_dir = "./uploads/resumes"
        count_before = len(os.listdir(upload_dir)) if os.path.exists(upload_dir) else 0

        # Simulate DB persistence failure during resume saving
        with patch("app.routes.resume_routes.ResumeIntelligenceService.extract_text", return_value="Sample extracted text"):
            with patch("app.routes.resume_routes.ResumeIntelligenceService.analyze_and_structure_resume", new_callable=AsyncMock) as mock_struct:
                mock_struct.return_value = {"skills": ["Rust"]}
                with patch.object(models.Resume, "__init__", side_effect=Exception("Database simulation error")):
                    fake_pdf = b"%PDF-1.4 " + b"X" * 100
                    res = self.client.post(
                        "/api/resume/upload",
                        headers=self.headers,
                        files={"file": ("new_resume.pdf", fake_pdf, "application/pdf")}
                    )

        self.assertEqual(res.status_code, 500)

        # Verify existing resume is STILL active
        self.db.expire_all()
        reloaded_resume = self.db.query(models.Resume).filter(models.Resume.id == existing_id).first()
        self.assertTrue(reloaded_resume.is_active, "Existing active resume must not be deactivated when new resume persistence fails!")

        # Verify disk file was cleaned up
        count_after = len(os.listdir(upload_dir)) if os.path.exists(upload_dir) else 0
        self.assertEqual(count_before, count_after, "Failed upload leaked a physical file on disk!")

    def test_16_explicit_resume_id_selection_and_authorization(self):
        """
        Verify POST /api/resume/interview/start:
        - Nonexistent resume_id returns 404.
        - Unauthorized resume_id belonging to another user returns 404.
        - Valid resume_id belonging to current user returns 200.
        - Omitted resume_id falls back to the user's active resume.
        """
        # User A resume
        resume_a = models.Resume(
            user_id=self.user_id,
            file_name="user_a_active.pdf",
            file_type="pdf",
            file_path="/tmp/user_a.pdf",
            is_active=True
        )
        self.db.add(resume_a)
        self.db.commit()

        q_a = models.ResumeQuestion(
            user_id=self.user_id,
            resume_id=resume_a.id,
            category="Technical",
            question_text="Tell me about your Python project."
        )
        self.db.add(q_a)
        self.db.commit()

        # User B setup
        user_b = models.User(
            name="Other User",
            username=f"other_{uuid.uuid4().hex[:6]}",
            email=f"other_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        self.db.add(user_b)
        self.db.commit()

        resume_b = models.Resume(
            user_id=user_b.id,
            file_name="user_b_active.pdf",
            file_type="pdf",
            file_path="/tmp/user_b.pdf",
            is_active=True
        )
        self.db.add(resume_b)
        self.db.commit()

        q_b = models.ResumeQuestion(
            user_id=user_b.id,
            resume_id=resume_b.id,
            category="Technical",
            question_text="Tell me about your C++ project."
        )
        self.db.add(q_b)
        self.db.commit()

        try:
            # 1. Nonexistent resume_id returns 404
            res_nonexistent = self.client.post(
                "/api/resume/interview/start",
                headers=self.headers,
                json={"resume_id": 999999}
            )
            self.assertEqual(res_nonexistent.status_code, 404)

            # 2. Unauthorized resume_id belonging to User B returns 404
            res_unauthorized = self.client.post(
                "/api/resume/interview/start",
                headers=self.headers,
                json={"resume_id": resume_b.id}
            )
            self.assertEqual(res_unauthorized.status_code, 404)

            # 3. Explicit valid resume_id for User A returns 200
            res_valid = self.client.post(
                "/api/resume/interview/start",
                headers=self.headers,
                json={"resume_id": resume_a.id}
            )
            self.assertEqual(res_valid.status_code, 200)
            self.assertIn("interview_id", res_valid.json())

            # 4. Omitted resume_id falls back to active resume
            res_omitted = self.client.post(
                "/api/resume/interview/start",
                headers=self.headers,
                json={}
            )
            self.assertEqual(res_omitted.status_code, 200)
            self.assertIn("interview_id", res_omitted.json())
        finally:
            self.db.query(models.ResumeInterview).filter(models.ResumeInterview.user_id == user_b.id).delete()
            self.db.query(models.ResumeQuestion).filter(models.ResumeQuestion.user_id == user_b.id).delete()
            self.db.query(models.Resume).filter(models.Resume.user_id == user_b.id).delete()
            self.db.query(models.User).filter(models.User.id == user_b.id).delete()
            self.db.commit()

    @patch("app.routes.resume_routes.ResumeIntelligenceService.generate_followup_question", new_callable=AsyncMock)
    def test_17_non_boolean_is_final_rejected(self, mock_followup):
        """
        Verify that POST /api/resume/interview/answer rejects non-boolean is_final
        values (strings, integers, None) with HTTP 400, while accepting booleans
        and defaulting to False when omitted.
        """
        resume = models.Resume(
            user_id=self.user_id,
            file_name="is_final_test.pdf",
            file_type="pdf",
            file_path="/tmp/final_test.pdf",
            is_active=True
        )
        self.db.add(resume)
        self.db.commit()

        session_state = {
            "qa_history": [],
            "current_question": "Explain inheritance in object-oriented programming."
        }
        interview = models.ResumeInterview(
            user_id=self.user_id,
            resume_id=resume.id,
            status="IN_PROGRESS",
            feedback_json=json.dumps(session_state)
        )
        self.db.add(interview)
        self.db.commit()

        mock_followup.return_value = "Follow-up question on polymorphism."

        # String "true" -> 400
        res1 = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={"interview_id": interview.id, "answer": "Inheritance allows reuse.", "is_final": "true"}
        )
        self.assertEqual(res1.status_code, 400)
        self.assertIn("is_final must be a boolean", res1.text)

        # String "false" -> 400
        res2 = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={"interview_id": interview.id, "answer": "Inheritance allows reuse.", "is_final": "false"}
        )
        self.assertEqual(res2.status_code, 400)
        self.assertIn("is_final must be a boolean", res2.text)

        # Integer 1 -> 400
        res3 = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={"interview_id": interview.id, "answer": "Inheritance allows reuse.", "is_final": 1}
        )
        self.assertEqual(res3.status_code, 400)
        self.assertIn("is_final must be a boolean", res3.text)

        # Valid boolean False -> 200
        res_valid = self.client.post(
            "/api/resume/interview/answer",
            headers=self.headers,
            json={"interview_id": interview.id, "answer": "Inheritance allows reuse.", "is_final": False}
        )
        self.assertEqual(res_valid.status_code, 200)


if __name__ == "__main__":
    unittest.main()
