import os
import sys
import uuid
import json
import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure testing flag and environment variables before imports
os.environ["TESTING"] = "True"

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import models, auth
from app.services.resume_intelligence_service import ResumeIntelligenceService
from app.services.adaptive_interview_service import AdaptiveInterviewService
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestAITopicMatching(unittest.TestCase):
    """
    Focused test suite verifying normalized exact topic matching in:
    1. ResumeIntelligenceService.evaluate_resume_interview
    2. AdaptiveInterviewService.evaluate_full_interview

    Ensures that AI-generated topic names cannot match unrelated curriculum topics,
    wildcard characters (% and _) do not expand matching, whitespace is stripped,
    case-insensitive matching works, and duplicates are safely deduplicated.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.db = TestingSessionLocal()

        # Seed test user
        suffix = uuid.uuid4().hex[:6]
        cls.user = models.User(
            name="Topic Test User",
            username=f"topic_user_{suffix}",
            email=f"topic_user_{suffix}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        cls.db.add(cls.user)
        cls.db.commit()
        cls.db.refresh(cls.user)

        # Seed test resume
        cls.resume = models.Resume(
            user_id=cls.user.id,
            file_name="test_resume.pdf",
            file_type="pdf",
            file_path="/tmp/test_resume.pdf",
            extracted_text="Python FastAPI Docker Developer",
            is_active=True
        )
        cls.db.add(cls.resume)
        cls.db.commit()
        cls.db.refresh(cls.resume)

        # Seed test curriculum
        cls.curriculum = models.Curriculum(
            name="Backend Engineering Track",
            description="Software Engineering Backend",
            difficulty="INTERMEDIATE"
        )
        cls.db.add(cls.curriculum)
        cls.db.commit()
        cls.db.refresh(cls.user)
        cls.db.refresh(cls.curriculum)

        # Clear any previous test topics and evaluations to guarantee exact ID matches
        cls.db.query(models.Evaluation).delete()
        cls.db.query(models.Topic).filter(
            models.Topic.name.like("Security Test %")
        ).delete(synchronize_session=False)
        cls.db.commit()

        # Seed distinctive topics with unique test prefixes to prevent collisions:
        # - "Security Test Docker Engine" (exact match)
        # - "Security Test Docker Engine & Cloud Tools" (composite - should NOT match)
        # - "Security Test SQL Database Design" (composite - should NOT match)
        # - "Security Test Python Programming" (exact match)
        cls.t_docker = models.Topic(
            name="Security Test Docker Engine",
            curriculum_id=cls.curriculum.id,
            category="DevOps"
        )
        cls.t_docker_composite = models.Topic(
            name="Security Test Docker Engine & Cloud Tools",
            curriculum_id=cls.curriculum.id,
            category="DevOps"
        )
        cls.t_sql_composite = models.Topic(
            name="Security Test SQL Database Design",
            curriculum_id=cls.curriculum.id,
            category="Databases"
        )
        cls.t_python = models.Topic(
            name="Security Test Python Programming",
            curriculum_id=cls.curriculum.id,
            category="Languages"
        )

        cls.db.add_all([
            cls.t_docker,
            cls.t_docker_composite,
            cls.t_sql_composite,
            cls.t_python
        ])
        cls.db.commit()
        for t in [cls.t_docker, cls.t_docker_composite, cls.t_sql_composite, cls.t_python]:
            cls.db.refresh(t)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cleanup_test_db()

    def setUp(self):
        self.db.rollback()
        # Clean evaluations before each test to guarantee test isolation
        self.db.query(models.Evaluation).delete()
        self.db.commit()

    def tearDown(self):
        self.db.rollback()

    # =========================================================================
    # RESUME INTELLIGENCE SERVICE TESTS
    # =========================================================================

    def _create_resume_interview(self):
        interview = models.ResumeInterview(
            user_id=self.user.id,
            resume_id=self.resume.id,
            status="IN_PROGRESS"
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def test_resume_exact_topic_match(self):
        """Exact topic name correctly matches and creates an Evaluation."""
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 70,
            "technical_score": 50,
            "project_knowledge_score": 75,
            "communication_score": 70,
            "problem_solving_score": 70,
            "resume_understanding_score": 70,
            "strengths": ["Clear explanation"],
            "weaknesses": ["Docker containerization"],
            "recommended_preparation": ["Study Dockerfiles"],
            "knowledge_gaps_identified": ["Security Test Docker Engine"]
        }

        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "What is Docker?", "answer": "Container tool"}]
                )
            )

        evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user.id
        ).all()
        self.assertEqual(len(evals), 1)
        self.assertEqual(evals[0].topic_id, self.t_docker.id)
        self.assertEqual(evals[0].user_id, self.user.id)
        self.assertIn("Security Test Docker Engine", evals[0].explanation)

    def test_resume_case_insensitive_match(self):
        """Topic matching is case-insensitive (e.g. 'docker', 'DOCKER')."""
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": ["sEcUrItY tEsT dOcKeR eNgInE"]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 1)
        self.assertEqual(evals[0].topic_id, self.t_docker.id)

    def test_resume_whitespace_trimming(self):
        """Surrounding whitespace is trimmed and does not prevent exact match."""
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": ["   Security Test Docker Engine \n\t "]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 1)
        self.assertEqual(evals[0].topic_id, self.t_docker.id)
        # Verify explanation uses cleaned topic name
        self.assertEqual(evals[0].explanation, "Resume Interview weakness identified in Security Test Docker Engine")

    def test_resume_partial_topic_name_does_not_match(self):
        """
        AI gap 'Security Test Docker Engine' must NOT match 'Security Test Docker Engine & Cloud Tools'.
        AI gap 'Security Test SQL' must NOT match 'Security Test SQL Database Design'.
        AI gap 'Security Test' must NOT match 'Security Test Python Programming'.
        """
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": ["Security Test Docker", "Security Test SQL", "Security Test"]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        # None of the partial names should have matched composite or longer topic names
        self.assertEqual(len(evals), 0)

    def test_resume_sql_wildcards_do_not_match(self):
        """
        SQL wildcards '%' and '_' must NOT broaden matching.
        '%' must NOT match any topic.
        '%Docker%' or '_ocker' must NOT match anything.
        """
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": ["%", "%Docker%", "_ocker", "P_thon", "____", "%Security Test%"]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 0)

    def test_resume_unknown_and_invalid_topics_skipped(self):
        """
        Unknown topic names, empty strings, whitespace-only strings,
        non-strings (numbers, dicts, None), and non-list gaps are safely skipped.
        """
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": [
                "Totally Unknown Topic XYZ",
                "",
                "   ",
                None,
                123,
                {"invalid": "structure"}
            ]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 0)

    def test_resume_non_list_gaps_payload(self):
        """If AI returns knowledge_gaps_identified as a string, it must not iterate characters."""
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            # Malformed AI output where knowledge_gaps_identified is a string, not a list
            "knowledge_gaps_identified": "Docker"
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 0)

    def test_resume_duplicate_topics_deduplicated(self):
        """Duplicate topic mentions within the same AI response create only 1 Evaluation."""
        interview = self._create_resume_interview()

        ai_response = {
            "overall_score": 75,
            "technical_score": 45,
            "knowledge_gaps_identified": [
                "Security Test Docker Engine",
                "security test docker engine",
                "  Security Test Docker Engine  ",
                "SECURITY TEST DOCKER ENGINE"
            ]
        }
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=f"<json>{json.dumps(ai_response)}</json>"))]

        with patch("app.services.resume_intelligence_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
            asyncio.run(
                ResumeIntelligenceService.evaluate_resume_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id,
                    qa_history=[{"question": "Q", "answer": "A"}]
                )
            )

        evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.topic_id == self.t_docker.id
        ).all()
        # Exactly one evaluation created, not four
        self.assertEqual(len(evals), 1)

    # =========================================================================
    # ADAPTIVE INTERVIEW SERVICE TESTS
    # =========================================================================

    def _create_adaptive_interview_with_questions(self, topic_and_scores):
        """
        Creates an Interview with InterviewQuestions and InterviewAnswers.
        topic_and_scores: list of tuples (topic_str, overall_score, tech_score)
        """
        interview = models.Interview(
            user_id=self.user.id,
            target_role="Backend Developer",
            interview_type="technical",
            status="IN_PROGRESS"
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)

        for idx, (topic_name, score, tech_score) in enumerate(topic_and_scores, start=1):
            q = models.InterviewQuestion(
                interview_id=interview.id,
                question_number=idx,
                question_text=f"Sample question {idx} regarding {topic_name}",
                difficulty="MEDIUM",
                category="TECHNICAL",
                topic=topic_name
            )
            self.db.add(q)
            self.db.commit()
            self.db.refresh(q)

            ans = models.InterviewAnswer(
                question_id=q.id,
                answer_text=f"Sample answer {idx}",
                overall_score=score,
                technical_score=tech_score,
                communication_score=70
            )
            self.db.add(ans)

        self.db.commit()
        return interview

    def test_adaptive_exact_topic_match(self):
        """Adaptive interview weak topic exact matches create evaluation for correct topic."""
        # Score < 60 triggers weak topic detection
        interview = self._create_adaptive_interview_with_questions([
            ("Security Test Python Programming", 45, 40)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user.id
        ).all()
        self.assertEqual(len(evals), 1)
        self.assertEqual(evals[0].topic_id, self.t_python.id)
        self.assertEqual(evals[0].overall_score, 40)  # min(55, avg_tech=40)
        self.assertIn("Security Test Python Programming", evals[0].explanation)

    def test_adaptive_case_and_whitespace_normalization(self):
        """Adaptive interview topic matching handles case variance and surrounding whitespace."""
        interview = self._create_adaptive_interview_with_questions([
            ("   sEcUrItY tEsT pYtHoN pRoGrAmMiNg   ", 50, 48)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 1)
        self.assertEqual(evals[0].topic_id, self.t_python.id)
        self.assertIn("'sEcUrItY tEsT pYtHoN pRoGrAmMiNg'", evals[0].explanation)

    def test_adaptive_partial_name_does_not_match(self):
        """
        Adaptive interview weak topics 'Security Test Python' and 'Security Test SQL' must NOT match
        'Security Test Python Programming' and 'Security Test SQL Database Design'.
        """
        interview = self._create_adaptive_interview_with_questions([
            ("Security Test Python", 40, 40),
            ("Security Test SQL", 35, 35)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).all()
        # Must not have matched any topic
        self.assertEqual(len(evals), 0)

    def test_adaptive_sql_wildcards_do_not_match(self):
        """SQL wildcards % and _ in adaptive questions must not match topics."""
        interview = self._create_adaptive_interview_with_questions([
            ("%", 40, 40),
            ("%Python%", 30, 30),
            ("_ocker", 45, 45)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 0)

    def test_adaptive_duplicate_weak_topics_deduplicated(self):
        """Multiple weak questions on the same topic only create 1 Evaluation."""
        interview = self._create_adaptive_interview_with_questions([
            ("Security Test Python Programming", 40, 40),
            ("security test python programming", 50, 45),
            ("  Security Test Python Programming  ", 30, 35)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.topic_id == self.t_python.id
        ).all()
        self.assertEqual(len(evals), 1)

    def test_adaptive_unknown_and_empty_topic_skipped(self):
        """Nonexistent or blank topics are safely skipped."""
        interview = self._create_adaptive_interview_with_questions([
            ("Nonexistent Topic", 30, 30),
            ("   ", 40, 40),
            ("", 35, 35)
        ])

        with patch("app.services.adaptive_interview_service.client", None):
            asyncio.run(
                AdaptiveInterviewService.evaluate_full_interview(
                    db=self.db,
                    user_id=self.user.id,
                    interview_id=interview.id
                )
            )

        evals = self.db.query(models.Evaluation).all()
        self.assertEqual(len(evals), 0)


if __name__ == "__main__":
    unittest.main()
