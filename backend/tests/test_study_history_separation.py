import os
import sys
import uuid
import json
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock

# Ensure testing flag and environment variables before imports
os.environ["TESTING"] = "True"
os.environ["AI_EVALUATION_RATE_LIMIT"] = "1000"

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app import models, auth
from app.services import (
    dashboard_service,
    insights_service,
    achievement_service,
    analytics_service,
    knowledge_gap_engine,
    smart_revision_service,
    adaptive_learning_engine
)
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestStudyHistorySeparation(unittest.TestCase):
    """
    Comprehensive test suite verifying MISSION 11C-C:
    Separation of genuine study history from synthetic interview weakness records.

    Covers:
    1. Attempt numbering in evaluations_routes ignores synthetic interview records.
    2. /evaluations/mine and /evaluations/topic/{id} exclude synthetic records.
    3. curriculum_routes ignores synthetic records for progress, attempts, and last_studied.
    4. dashboard_service recent activity does not render fake "Practiced {topic}" and computes genuine mastery.
    5. insights_service streak, totals, trends, and breakdowns ignore synthetic records.
    6. analytics_service and achievement_service count only genuine study evaluations.
    7. smart_revision_service ignores synthetic records for revision attempt count and history.
    8. Historical record 17 (explanation with ai_feedback_json IS NULL) is preserved as genuine.
    9. knowledge_gap_engine continues to consume synthetic records for gap analysis.
    10. Predicate behavior with NULL, empty, and varying explanation strings.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)
        db = TestingSessionLocal()

        # Seed shared test curriculum
        curr_suffix = uuid.uuid4().hex[:6]
        cls.curriculum = models.Curriculum(
            name=f"Systems Architecture {curr_suffix}",
            description="Backend & Distributed Systems Track",
            difficulty="ADVANCED"
        )
        db.add(cls.curriculum)
        db.commit()
        db.refresh(cls.curriculum)

        # Seed shared test topics
        cls.topic_a = models.Topic(
            name=f"Distributed Consensus {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Distributed Systems"
        )
        cls.topic_b = models.Topic(
            name=f"Database Sharding {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Databases"
        )
        cls.topic_c = models.Topic(
            name=f"Message Brokers {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Infrastructure"
        )
        db.add_all([cls.topic_a, cls.topic_b, cls.topic_c])
        db.commit()
        db.refresh(cls.topic_a)
        db.refresh(cls.topic_b)
        db.refresh(cls.topic_c)

        cls.curriculum_id = cls.curriculum.id
        cls.topic_a_id = cls.topic_a.id
        cls.topic_b_id = cls.topic_b.id
        cls.topic_c_id = cls.topic_c.id
        cls.topic_a_name = cls.topic_a.name
        cls.topic_b_name = cls.topic_b.name
        cls.topic_c_name = cls.topic_c.name

        db.close()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Seed fresh user per test to guarantee complete test isolation
        suffix = uuid.uuid4().hex[:6]
        self.user = models.User(
            name="Separation Test User",
            username=f"sep_user_{suffix}",
            email=f"sep_user_{suffix}@example.com",
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
        # Clean data for this test user
        self.db.query(models.Evaluation).filter(models.Evaluation.user_id == self.user_id).delete()
        self.db.query(models.RevisionSchedule).filter(models.RevisionSchedule.user_id == self.user_id).delete()
        self.db.query(models.LearningActivity).filter(models.LearningActivity.user_id == self.user_id).delete()
        self.db.commit()
        self.db.close()

    # -------------------------------------------------------------------------
    # Helper seed methods
    # -------------------------------------------------------------------------

    def _create_genuine_eval(self, topic_id: int, score: int = 80, explanation: str = "A valid student study explanation.", feedback: bool = True, days_ago: int = 0):
        created = datetime.now(timezone.utc) - timedelta(days=days_ago)
        fb_json = json.dumps({"strengths": ["Clear definition"], "weaknesses": []}) if feedback else None
        e = models.Evaluation(
            user_id=self.user_id,
            topic_id=topic_id,
            explanation=explanation,
            ai_score=score,
            overall_score=score,
            technical_score=score,
            communication_score=score,
            ai_feedback_json=fb_json,
            created_at=created
        )
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    def _create_resume_synthetic_eval(self, topic_id: int, score: int = 50, days_ago: int = 0):
        created = datetime.now(timezone.utc) - timedelta(days=days_ago)
        t = self.db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        topic_name = t.name if t else "Unknown"
        e = models.Evaluation(
            user_id=self.user_id,
            topic_id=topic_id,
            explanation=f"{models.RESUME_WEAKNESS_PREFIX}{topic_name}",
            ai_score=score,
            overall_score=score,
            technical_score=score,
            communication_score=score,
            ai_feedback_json=None,
            created_at=created
        )
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    def _create_adaptive_synthetic_eval(self, topic_id: int, score: int = 55, days_ago: int = 0):
        created = datetime.now(timezone.utc) - timedelta(days=days_ago)
        t = self.db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        topic_name = t.name if t else "Unknown"
        e = models.Evaluation(
            user_id=self.user_id,
            topic_id=topic_id,
            explanation=f"{models.ADAPTIVE_WEAKNESS_PREFIX}{topic_name}",
            ai_score=score,
            overall_score=score,
            technical_score=score,
            communication_score=score,
            ai_feedback_json=None,
            created_at=created
        )
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return e

    # -------------------------------------------------------------------------
    # TEST 1: Attempt numbering ignores synthetic interview records
    # -------------------------------------------------------------------------
    def test_attempt_numbering_ignores_synthetic_records(self):
        # 1 genuine eval + 2 synthetic evals for topic_a
        self._create_genuine_eval(topic_id=self.topic_a_id, score=80, days_ago=2)
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=50, days_ago=1)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_a_id, score=55, days_ago=1)

        # Mock AI evaluation services
        mock_eval_response = {
            "technicalAccuracy": {"score": 85, "feedback": "Solid"},
            "conceptUnderstanding": {"score": 85, "feedback": "Solid"},
            "completeness": {"score": 85, "feedback": "Solid"},
            "examples": {"score": 85, "feedback": "Solid"},
            "relevance": {"score": 85, "feedback": "Solid"},
            "communication": {"score": 85, "feedback": "Solid"},
            "grammar": {"score": 85, "feedback": "Solid"},
            "vocabulary": {"score": 85, "feedback": "Solid"},
            "strengths": ["Well explained"],
            "weaknesses": []
        }

        with patch("app.routes.evaluations_routes.evaluate_explanation", new_callable=AsyncMock) as mock_ai, \
             patch("app.routes.evaluations_routes.generate_improvement_insight", new_callable=AsyncMock) as mock_insight:
            mock_ai.return_value = mock_eval_response
            mock_insight.return_value = "Great improvement on Raft fundamentals."

            response = self.client.post(
                "/api/evaluate",
                headers=self.headers,
                json={
                    "topic_id": self.topic_a_id,
                    "explanation": "Raft achieves consensus via leader election and log replication.",
                    "learning_mode": "TECHNICAL"
                }
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Without fix, previous_evals was 3 -> attempt_number would be 4.
        # With fix, previous_evals is 1 -> attempt_number is 2!
        self.assertEqual(data["attempt_number"], 2)

    # -------------------------------------------------------------------------
    # TEST 2: /evaluations/mine and /evaluations/topic/{id} exclude synthetic records
    # -------------------------------------------------------------------------
    def test_evaluations_routes_exclude_synthetic_records(self):
        genuine_1 = self._create_genuine_eval(topic_id=self.topic_a_id, score=82)
        genuine_2 = self._create_genuine_eval(topic_id=self.topic_b_id, score=90)
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=45)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_b_id, score=50)

        # Check /api/evaluations/mine
        res_mine = self.client.get("/api/evaluations/mine", headers=self.headers)
        self.assertEqual(res_mine.status_code, 200)
        mine_data = res_mine.json()
        self.assertEqual(len(mine_data), 2)
        mine_ids = [m["id"] for m in mine_data]
        self.assertIn(genuine_1.id, mine_ids)
        self.assertIn(genuine_2.id, mine_ids)

        # Check /api/evaluations/topic/{topic_id}
        res_topic = self.client.get(f"/api/evaluations/topic/{self.topic_a_id}", headers=self.headers)
        self.assertEqual(res_topic.status_code, 200)
        topic_data = res_topic.json()
        self.assertEqual(topic_data["total_attempts"], 1)
        self.assertEqual(len(topic_data["history"]), 1)
        self.assertEqual(topic_data["history"][0]["id"], genuine_1.id)

    # -------------------------------------------------------------------------
    # TEST 3: curriculum_routes ignores synthetic records
    # -------------------------------------------------------------------------
    def test_curriculum_routes_ignores_synthetic_records(self):
        # Topic A has 1 genuine (score 80) and 1 synthetic (score 50)
        self._create_genuine_eval(topic_id=self.topic_a_id, score=80, days_ago=3)
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=50, days_ago=1)

        # Topic B has ONLY a synthetic record (score 55)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_b_id, score=55, days_ago=1)

        res = self.client.get(f"/api/curricula/{self.curriculum_id}/progress", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        topics = data["topics"]
        topic_a_stat = next(t for t in topics if t["id"] == self.topic_a_id)
        topic_b_stat = next(t for t in topics if t["id"] == self.topic_b_id)

        # Topic A must report 1 attempt and best_score 80
        self.assertEqual(topic_a_stat["attempts"], 1)
        self.assertEqual(topic_a_stat["best_score"], 80)

        # Topic B must report 0 attempts, not completed
        self.assertEqual(topic_b_stat["attempts"], 0)
        self.assertIsNone(topic_b_stat["best_score"])
        self.assertIsNone(topic_b_stat["last_attempt"])

    # -------------------------------------------------------------------------
    # TEST 4: dashboard_service recent activity does not render fake "Practiced {topic}"
    # -------------------------------------------------------------------------
    def test_dashboard_service_ignores_synthetic_records(self):
        genuine = self._create_genuine_eval(topic_id=self.topic_a_id, score=88)
        self._create_resume_synthetic_eval(topic_id=self.topic_b_id, score=50)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_c_id, score=45)

        # Recent activity
        activities = dashboard_service.get_recent_activity(self.db, self.user_id)
        titles = [a["title"] for a in activities]
        self.assertIn(f"Practiced {self.topic_a_name}", titles)
        self.assertNotIn(f"Practiced {self.topic_b_name}", titles)
        self.assertNotIn(f"Practiced {self.topic_c_name}", titles)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]["id"], genuine.id)

        # Mastery calculation
        tech_mastery = dashboard_service.calculate_technical_mastery(self.db, self.user_id)
        self.assertEqual(tech_mastery, 88.0)

        comm_score = dashboard_service.calculate_communication_score(self.db, self.user_id)
        self.assertEqual(comm_score, 88.0)

    # -------------------------------------------------------------------------
    # TEST 5: insights_service streak, totals, trends, and breakdowns ignore synthetic records
    # -------------------------------------------------------------------------
    def test_insights_service_ignores_synthetic_records(self):
        # Seed 2 genuine evaluations
        self._create_genuine_eval(topic_id=self.topic_a_id, score=70, days_ago=1)
        self._create_genuine_eval(topic_id=self.topic_a_id, score=90, days_ago=0)

        # Seed synthetic records with low scores
        self._create_resume_synthetic_eval(topic_id=self.topic_b_id, score=40, days_ago=0)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_c_id, score=35, days_ago=0)

        # 1. Summary stats
        stats = insights_service.get_summary_stats(self.db, self.user_id)
        self.assertEqual(stats["total_evaluations"], 2)
        self.assertEqual(stats["average_score"], 80.0)

        # 2. Score trend
        trend = insights_service.calculate_score_trend(self.db, self.user_id)
        total_evals_trend = sum(pt["count"] for pt in trend["trend"])
        self.assertEqual(total_evals_trend, 2)

        # 3. Weak / strong topics
        weak = insights_service.get_weak_topics(self.db, self.user_id)
        weak_names = [w["topic_name"] for w in weak["weak_topics"]]
        self.assertNotIn(self.topic_b_name, weak_names)
        self.assertNotIn(self.topic_c_name, weak_names)

        # 4. Most attempted topics
        attempted = insights_service.get_most_attempted_topics(self.db, self.user_id)
        attempt_map = {m["topic_name"]: m["attempts"] for m in attempted["most_attempted"]}
        self.assertEqual(attempt_map.get(self.topic_a_name), 2)
        self.assertNotIn(self.topic_b_name, attempt_map)
        self.assertNotIn(self.topic_c_name, attempt_map)

        # 5. Grammar trend
        grammar = insights_service.get_grammar_trend(self.db, self.user_id)
        self.assertGreaterEqual(len(grammar["grammar_score_over_time"]), 1)

        # 6. Curriculum stats
        curr_stats = insights_service.get_curriculum_stats(self.db, self.user_id)
        curr_entry = next((c for c in curr_stats["curriculums"] if c["curriculum_id"] == self.curriculum_id), None)
        self.assertIsNotNone(curr_entry)
        self.assertEqual(curr_entry["completed_topics"], 1)  # Only Topic A was genuinely studied
        self.assertEqual(curr_entry["average_score"], 80.0)

    # -------------------------------------------------------------------------
    # TEST 6: analytics_service and achievement_service count only genuine study evaluations
    # -------------------------------------------------------------------------
    def test_analytics_and_achievement_services_ignore_synthetic_records(self):
        self._create_genuine_eval(topic_id=self.topic_a_id, score=85)
        self._create_resume_synthetic_eval(topic_id=self.topic_b_id, score=45)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_c_id, score=40)

        # AnalyticsService
        analytics = analytics_service.AnalyticsService.get_comprehensive_analytics(self.db, self.user_id)
        self.assertEqual(analytics["weeklySummary"]["evaluations"], 1)
        self.assertEqual(analytics["summary"]["technicalMastery"], 85)
        self.assertEqual(len(analytics["scoreTrend"]), 1)
        self.assertEqual(analytics["scoreTrend"][0]["overall"], 85)

        # AchievementService user metrics
        metrics = achievement_service.get_user_metrics(self.db, self.user_id)
        self.assertEqual(metrics["evaluation_count"], 1)
        self.assertEqual(metrics["concepts_count"], 1)

    # -------------------------------------------------------------------------
    # TEST 7: smart_revision_service ignores synthetic records for study attempts and history
    # -------------------------------------------------------------------------
    def test_smart_revision_service_ignores_synthetic_records(self):
        # Create genuine schedule and evaluation
        self._create_genuine_eval(topic_id=self.topic_a_id, score=78)
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=50)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_a_id, score=52)

        sched = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            current_mastery_score=78.0,
            review_count=1,
            next_review_at=datetime.now(timezone.utc)
        )
        self.db.add(sched)
        self.db.commit()

        # Check get_user_revisions attempt count
        revisions_data = smart_revision_service.SmartRevisionService.get_user_revisions(self.db, self.user_id)
        all_cards = (
            revisions_data.get("due_today", []) +
            revisions_data.get("upcoming", []) +
            revisions_data.get("tomorrow", []) +
            revisions_data.get("overdue", [])
        )
        topic_a_card = next((c for c in all_cards if c["topic_id"] == self.topic_a_id), None)
        self.assertIsNotNone(topic_a_card)
        self.assertEqual(topic_a_card["attempts"], 1)

        # Check get_user_revision_history_all
        history = smart_revision_service.SmartRevisionService.get_user_revision_history_all(self.db, self.user_id)
        topic_a_hist = next((h for h in history if h["topic_id"] == self.topic_a_id), None)
        self.assertIsNotNone(topic_a_hist)
        self.assertEqual(topic_a_hist["total_attempts"], 1)
        self.assertEqual(len(topic_a_hist["history_attempts"]), 1)
        self.assertEqual(topic_a_hist["history_attempts"][0]["score"], 78)

    # -------------------------------------------------------------------------
    # TEST 8: Historical record 17 (explanation with ai_feedback_json IS NULL) is preserved
    # -------------------------------------------------------------------------
    def test_historical_legacy_record_preserved(self):
        # Legacy record pattern: ai_feedback_json is NULL, genuine explanation
        legacy = self._create_genuine_eval(
            topic_id=self.topic_a_id,
            score=85,
            explanation="This is a detailed explanation of topic.",
            feedback=False  # ai_feedback_json is None
        )

        genuine_query = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.genuine_predicate()
        ).all()
        self.assertEqual(len(genuine_query), 1)
        self.assertEqual(genuine_query[0].id, legacy.id)

        # Verify it appears in /evaluations/mine
        res = self.client.get("/api/evaluations/mine", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        mine = res.json()
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine[0]["id"], legacy.id)

        # Verify it appears in dashboard activity
        activities = dashboard_service.get_recent_activity(self.db, self.user_id)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]["id"], legacy.id)

    # -------------------------------------------------------------------------
    # TEST 9: knowledge_gap_engine continues to consume synthetic records correctly
    # -------------------------------------------------------------------------
    def test_knowledge_gap_engine_consumes_synthetic_records(self):
        # Seed ONLY synthetic interview weaknesses for topic_a and topic_b
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=45)
        self._create_adaptive_synthetic_eval(topic_id=self.topic_b_id, score=50)

        # Knowledge gap engine MUST detect these as weaknesses
        gaps = knowledge_gap_engine.analyze_user_knowledge(self.db, self.user_id)
        gap_topic_ids = [g["topic_id"] for g in gaps]
        self.assertIn(self.topic_a_id, gap_topic_ids)
        self.assertIn(self.topic_b_id, gap_topic_ids)

        gap_a = next(g for g in gaps if g["topic_id"] == self.topic_a_id)
        self.assertIn(gap_a["severity"], ["CRITICAL", "HIGH", "MEDIUM"])

    # -------------------------------------------------------------------------
    # TEST 10: Predicate behavior with NULL, empty, and varying explanation strings
    # -------------------------------------------------------------------------
    def test_predicate_edge_cases_and_mutual_exclusion(self):
        e_null = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id, explanation=None, ai_score=80
        )
        e_empty = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id, explanation="", ai_score=80
        )
        e_spaces = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id, explanation="   ", ai_score=80
        )
        e_normal = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id, explanation="Valid explanation of Raft", ai_score=80
        )
        e_syn_res = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id,
            explanation=f"{models.RESUME_WEAKNESS_PREFIX}Topic X", ai_score=50
        )
        e_syn_adapt = models.Evaluation(
            user_id=self.user_id, topic_id=self.topic_a_id,
            explanation=f"{models.ADAPTIVE_WEAKNESS_PREFIX}Topic Y", ai_score=50
        )

        self.db.add_all([e_null, e_empty, e_spaces, e_normal, e_syn_res, e_syn_adapt])
        self.db.commit()

        # Query using genuine_predicate()
        genuine_evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.genuine_predicate()
        ).all()
        genuine_ids = {e.id for e in genuine_evals}

        # Query using synthetic_predicate()
        synthetic_evals = self.db.query(models.Evaluation).filter(
            models.Evaluation.user_id == self.user_id,
            models.Evaluation.synthetic_predicate()
        ).all()
        synthetic_ids = {e.id for e in synthetic_evals}

        # Verify genuine contains null, empty, spaces, normal
        self.assertIn(e_null.id, genuine_ids)
        self.assertIn(e_empty.id, genuine_ids)
        self.assertIn(e_spaces.id, genuine_ids)
        self.assertIn(e_normal.id, genuine_ids)

        # Verify synthetic contains only the two prefixed records
        self.assertIn(e_syn_res.id, synthetic_ids)
        self.assertIn(e_syn_adapt.id, synthetic_ids)

        # Verify strict mutual exclusion: disjoint sets and full coverage
        self.assertTrue(genuine_ids.isdisjoint(synthetic_ids))
        self.assertEqual(len(genuine_ids) + len(synthetic_ids), 6)

    # -------------------------------------------------------------------------
    # TEST 11: Adaptive recommendations use synthetic weakness without counting attempts
    # -------------------------------------------------------------------------
    def test_adaptive_recommendations_use_synthetic_weakness_without_counting_attempts(self):
        # Seed ONLY synthetic interview weaknesses for topic_a (score 48)
        self._create_resume_synthetic_eval(topic_id=self.topic_a_id, score=48)

        # Generate learning path
        path = adaptive_learning_engine.generate_user_learning_path(self.db, self.user_id)
        topic_a_node = next((n for n in path if n["topic_id"] == self.topic_a_id), None)
        self.assertIsNotNone(topic_a_node)

        # 1. Weakness signal is preserved: mastery score is low (~48), priority is high
        self.assertLess(topic_a_node["mastery_score"], 60)
        self.assertGreater(topic_a_node["priority"], 50)
        self.assertIn(self.topic_a_name, topic_a_node["reason"])

        # 2. Genuine attempts NOT counted: state is NOT_STARTED and action is LEARN
        self.assertEqual(topic_a_node["state"], "NOT_STARTED")
        self.assertEqual(topic_a_node["action_type"], "LEARN")

        # 3. Target concept from gap requires genuine evaluation
        target_concept = adaptive_learning_engine.get_target_concept_from_gap(self.db, self.topic_a_id, self.user_id)
        self.assertIsNone(target_concept)

        # Now add 1 genuine study evaluation for topic_a with score 55
        self._create_genuine_eval(topic_id=self.topic_a_id, score=55)

        # Recalculate learning path: now user has genuinely attempted it
        path_after = adaptive_learning_engine.generate_user_learning_path(self.db, self.user_id)
        node_after = next((n for n in path_after if n["topic_id"] == self.topic_a_id), None)
        self.assertIsNotNone(node_after)
        self.assertIn(node_after["state"], ["WEAK", "CRITICAL"])
        self.assertEqual(node_after["action_type"], "REVIEW")

        target_concept_after = adaptive_learning_engine.get_target_concept_from_gap(self.db, self.topic_a_id, self.user_id)
        self.assertEqual(target_concept_after, "Core Fundamentals")


if __name__ == "__main__":
    unittest.main()
