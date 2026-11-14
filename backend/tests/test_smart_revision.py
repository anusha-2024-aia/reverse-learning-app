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
from app.services.smart_revision_service import (
    SmartRevisionService,
    LOW_MASTERY_INTERVAL,
    MEDIUM_MASTERY_INTERVAL,
    GOOD_MASTERY_INTERVAL,
    HIGH_MASTERY_INTERVAL
)
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db


class TestSmartRevisionSuite(unittest.TestCase):
    """
    Comprehensive test suite for Smart Revision Engine and API (Phase 6 & 6B):
    1. Deterministic interval calculation (<60: 1d, 60-79: 3d, 80-89: 7d, >=90: 14d).
    2. Acceleration logic for knowledge gaps and declining performance trends.
    3. Dynamic status calculation (OVERDUE, DUE, UPCOMING).
    4. Priority scoring and failed_attempts calculation using genuine evaluations.
    5. Schedule updating without duplicate increments (review_count increases by 1).
    6. RoadmapItem synchronization without prematurely forcing MASTERED status.
    7. User isolation across all revision endpoints and services.
    8. Complete API routes coverage (/revisions, /summary, /today, /overdue, /upcoming, /history, /start, /complete).
    9. Synthetic interview evaluation isolation from genuine study attempt counts and history.
    """

    @classmethod
    def setUpClass(cls):
        init_test_db()
        cls.client = TestClient(app)
        db = TestingSessionLocal()

        # Seed shared test curriculum
        curr_suffix = uuid.uuid4().hex[:6]
        cls.curriculum = models.Curriculum(
            name=f"Revision Test Curriculum {curr_suffix}",
            description="Curriculum for Smart Revision Testing",
            difficulty="INTERMEDIATE"
        )
        db.add(cls.curriculum)
        db.commit()
        db.refresh(cls.curriculum)

        # Seed shared test topics
        cls.topic_a = models.Topic(
            name=f"Cache Invalidation {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Caching"
        )
        cls.topic_b = models.Topic(
            name=f"Event Sourcing {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Architecture"
        )
        cls.topic_c = models.Topic(
            name=f"Raft Consensus {curr_suffix}",
            curriculum_id=cls.curriculum.id,
            category="Distributed Systems"
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
        suffix = uuid.uuid4().hex[:6]
        self.user = models.User(
            name="Revision Tester",
            username=f"rev_user_{suffix}",
            email=f"rev_user_{suffix}@example.com",
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
        self.db.query(models.Evaluation).filter(models.Evaluation.user_id == self.user_id).delete()
        self.db.query(models.RevisionSchedule).filter(models.RevisionSchedule.user_id == self.user_id).delete()
        self.db.query(models.RoadmapItem).filter(models.RoadmapItem.user_id == self.user_id).delete()
        self.db.query(models.Roadmap).filter(models.Roadmap.user_id == self.user_id).delete()
        self.db.query(models.LearningActivity).filter(models.LearningActivity.user_id == self.user_id).delete()
        self.db.query(models.User).filter(models.User.id == self.user_id).delete()
        self.db.commit()
        self.db.close()

    # -------------------------------------------------------------------------
    # Helper seed methods
    # -------------------------------------------------------------------------

    def _create_genuine_eval(self, topic_id: int, score: int = 80, days_ago: int = 0):
        created = datetime.now(timezone.utc) - timedelta(days=days_ago)
        fb_json = json.dumps({"strengths": ["Solid foundation"], "weaknesses": []})
        e = models.Evaluation(
            user_id=self.user_id,
            topic_id=topic_id,
            explanation="A comprehensive and detailed student explanation.",
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

    def _create_synthetic_eval(self, topic_id: int, score: int = 50, days_ago: int = 0):
        created = datetime.now(timezone.utc) - timedelta(days=days_ago)
        t = self.db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        topic_name = t.name if t else "Topic"
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

    # -------------------------------------------------------------------------
    # 1. Deterministic Interval Boundaries Tests
    # -------------------------------------------------------------------------

    def test_01_interval_tiers(self):
        """Verify strict adherence to interval tiers: <60: 1d, 60-79: 3d, 80-89: 7d, >=90: 14d."""
        # Tier 1: Low mastery (< 60)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(0.0), LOW_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(50.0), LOW_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(59.9), LOW_MASTERY_INTERVAL)

        # Tier 2: Medium mastery (60 - 79)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(60.0), MEDIUM_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(70.0), MEDIUM_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(79.9), MEDIUM_MASTERY_INTERVAL)

        # Tier 3: Good mastery (80 - 89)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(80.0), GOOD_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(85.0), GOOD_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(89.9), GOOD_MASTERY_INTERVAL)

        # Tier 4: High mastery (>= 90)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(90.0), HIGH_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(95.0), HIGH_MASTERY_INTERVAL)
        self.assertEqual(SmartRevisionService.calculate_revision_interval(100.0), HIGH_MASTERY_INTERVAL)

    # -------------------------------------------------------------------------
    # 2. Acceleration for Knowledge Gaps and Declining Trends
    # -------------------------------------------------------------------------

    def test_02_acceleration_with_knowledge_gap(self):
        """
        Verify that knowledge gaps accelerate revision:
        - Score < 70: capped at max 1 day.
        - Score >= 70: capped at max 3 days.
        """
        base_time = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)

        # Score 65 (normally 3 days): accelerated to 1 day
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=65.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=True,
            trend="STABLE"
        )
        self.assertEqual((next_date - base_time).days, 1)

        # Score 85 (normally 7 days): accelerated to 3 days
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=85.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=True,
            trend="STABLE"
        )
        self.assertEqual((next_date - base_time).days, 3)

        # Score 95 (normally 14 days): accelerated to 3 days
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=95.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=True,
            trend="STABLE"
        )
        self.assertEqual((next_date - base_time).days, 3)

        # Score 50 (< 60, normally 1 day): remains 1 day
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=50.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=True,
            trend="STABLE"
        )
        self.assertEqual((next_date - base_time).days, 1)

    def test_03_acceleration_with_declining_trend(self):
        """Verify that declining trend without explicit knowledge gap flag also triggers acceleration."""
        base_time = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)

        # Score 65 (< 70) with DECLINING trend -> capped at 1 day
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=65.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=False,
            trend="DECLINING"
        )
        self.assertEqual((next_date - base_time).days, 1)

        # Score 85 (>= 70) with DECLINING trend -> capped at 3 days
        next_date = SmartRevisionService.calculate_next_review_date(
            mastery_score=85.0,
            last_reviewed_at=base_time,
            has_knowledge_gap=False,
            trend="DECLINING"
        )
        self.assertEqual((next_date - base_time).days, 3)

    def test_04_no_acceleration_when_stable_and_no_gap(self):
        """Verify standard intervals are used when there is no gap and trend is STABLE."""
        base_time = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)

        self.assertEqual(
            (SmartRevisionService.calculate_next_review_date(50.0, base_time, False, "STABLE") - base_time).days, 1
        )
        self.assertEqual(
            (SmartRevisionService.calculate_next_review_date(65.0, base_time, False, "STABLE") - base_time).days, 3
        )
        self.assertEqual(
            (SmartRevisionService.calculate_next_review_date(85.0, base_time, False, "STABLE") - base_time).days, 7
        )
        self.assertEqual(
            (SmartRevisionService.calculate_next_review_date(95.0, base_time, False, "STABLE") - base_time).days, 14
        )

    # -------------------------------------------------------------------------
    # 3. Dynamic Status Calculation Tests
    # -------------------------------------------------------------------------

    def test_05_dynamic_status(self):
        """Verify dynamic status correctly evaluates past, today, future, and None dates."""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        today = now
        tomorrow = now + timedelta(days=1)
        future = now + timedelta(days=5)

        self.assertEqual(SmartRevisionService.get_dynamic_status(yesterday), "OVERDUE")
        self.assertEqual(SmartRevisionService.get_dynamic_status(today), "DUE")
        self.assertEqual(SmartRevisionService.get_dynamic_status(tomorrow), "UPCOMING")
        self.assertEqual(SmartRevisionService.get_dynamic_status(future), "UPCOMING")
        self.assertEqual(SmartRevisionService.get_dynamic_status(None), "DUE")

    # -------------------------------------------------------------------------
    # 4. Priority Scoring and Failed Attempts
    # -------------------------------------------------------------------------

    def test_06_priority_scoring_components(self):
        """Verify priority scoring formula: base + gap bonus + trend bonus + overdue bonus + fail bonus."""
        # Baseline: mastery 80, no gap, stable, upcoming, 0 fails -> 100 - 80 = 20.0
        score = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=False,
            trend="STABLE",
            status="UPCOMING",
            failed_attempts=0
        )
        self.assertEqual(score, 20.0)

        # Add gap (+50)
        score_gap = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=True,
            trend="STABLE",
            status="UPCOMING",
            failed_attempts=0
        )
        self.assertEqual(score_gap, 70.0)

        # Add declining trend (+30)
        score_declining = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=True,
            trend="DECLINING",
            status="UPCOMING",
            failed_attempts=0
        )
        self.assertEqual(score_declining, 100.0)

        # Add overdue status (+20)
        score_overdue = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=True,
            trend="DECLINING",
            status="OVERDUE",
            failed_attempts=0
        )
        self.assertEqual(score_overdue, 120.0)

        # Add failed attempts (+5 per fail, capped at 20)
        score_fails = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=True,
            trend="DECLINING",
            status="OVERDUE",
            failed_attempts=2
        )
        self.assertEqual(score_fails, 130.0)

        # Cap check: 6 failed attempts (6 * 5 = 30) should cap at 20 bonus
        score_capped_fails = SmartRevisionService.calculate_priority_score(
            mastery_score=80.0,
            has_knowledge_gap=False,
            trend="STABLE",
            status="UPCOMING",
            failed_attempts=6
        )
        self.assertEqual(score_capped_fails, 40.0)

    # -------------------------------------------------------------------------
    # 5. Schedule Update, Single Review Count, and Roadmap Integrity
    # -------------------------------------------------------------------------

    def test_07_update_revision_schedule_lifecycle(self):
        """
        Verify update_revision_schedule creates new schedule with review_count=1,
        and subsequent update preserves previous mastery and increments review_count by exactly 1.
        """
        # First creation
        sched = SmartRevisionService.update_revision_schedule(
            db=self.db,
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            new_mastery_score=60.0
        )
        self.assertIsNotNone(sched)
        self.assertEqual(sched.review_count, 1)
        self.assertEqual(sched.current_mastery_score, 60.0)
        self.assertEqual(sched.last_mastery_score, 60.0)

        # Second update
        sched2 = SmartRevisionService.update_revision_schedule(
            db=self.db,
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            new_mastery_score=85.0
        )
        self.assertEqual(sched2.id, sched.id)
        self.assertEqual(sched2.review_count, 2)
        self.assertEqual(sched2.last_mastery_score, 60.0)
        self.assertEqual(sched2.current_mastery_score, 85.0)

    def test_08_roadmap_status_not_prematurely_overwritten_to_mastered(self):
        """
        Verify that update_revision_schedule updates RoadmapItem.mastery_score and last_evaluated_at,
        but does NOT prematurely force status = 'MASTERED' at mastery >= 80%.
        Canonical RoadmapService requirements (mastery >= 85% and attempts >= 2) must be preserved.
        """
        roadmap = models.Roadmap(
            user_id=self.user_id,
            target_role="Backend Engineer",
            status="active"
        )
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)

        # Create a RoadmapItem in IN_PROGRESS status
        r_item = models.RoadmapItem(
            roadmap_id=roadmap.id,
            user_id=self.user_id,
            topic_id=self.topic_b_id,
            topic_name=self.topic_b_name,
            order_index=1,
            status="IN_PROGRESS",
            mastery_score=50.0
        )
        self.db.add(r_item)
        self.db.commit()

        # Update revision schedule with mastery 82.0 (>= 80% but not eligible for canonical MASTERED)
        SmartRevisionService.update_revision_schedule(
            db=self.db,
            user_id=self.user_id,
            topic_id=self.topic_b_id,
            new_mastery_score=82.0
        )

        self.db.refresh(r_item)
        self.assertEqual(r_item.mastery_score, 82.0)
        self.assertEqual(r_item.status, "IN_PROGRESS", "RoadmapItem status must not be hardcoded to MASTERED!")
        self.assertIsNotNone(r_item.last_evaluated_at)

    # -------------------------------------------------------------------------
    # 6. Categorization, Priority Sorting, and Synthetic Evaluation Isolation
    # -------------------------------------------------------------------------

    def test_09_categorization_and_synthetic_evaluation_isolation(self):
        """
        Verify get_user_revisions correctly categorizes overdue, due_today, tomorrow, upcoming,
        sorts by priority score, and accurately computes failed_attempts and attempt_count
        using genuine study evaluations only (ignoring synthetic interview evaluations).
        """
        now = datetime.now(timezone.utc)

        # Create genuine evaluations: 1 fail (55) and 1 pass (85)
        self._create_genuine_eval(topic_id=self.topic_a_id, score=55, days_ago=3)
        self._create_genuine_eval(topic_id=self.topic_a_id, score=85, days_ago=1)

        # Create 2 synthetic interview evaluations (scores 40, 50) for the same topic
        self._create_synthetic_eval(topic_id=self.topic_a_id, score=40, days_ago=5)
        self._create_synthetic_eval(topic_id=self.topic_a_id, score=50, days_ago=4)

        # Create 3 RevisionSchedule records for user:
        # Schedule A (Topic A): OVERDUE
        sched_a = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            current_mastery_score=75.0,
            last_mastery_score=55.0,
            next_review_at=now - timedelta(days=2),
            last_reviewed_at=now - timedelta(days=5),
            review_count=1,
            status="OVERDUE"
        )
        # Schedule B (Topic B): DUE TODAY
        sched_b = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_b_id,
            current_mastery_score=65.0,
            last_mastery_score=65.0,
            next_review_at=now,
            last_reviewed_at=now - timedelta(days=3),
            review_count=1,
            status="DUE"
        )
        # Schedule C (Topic C): TOMORROW
        sched_c = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_c_id,
            current_mastery_score=90.0,
            last_mastery_score=80.0,
            next_review_at=now + timedelta(days=1),
            last_reviewed_at=now - timedelta(days=2),
            review_count=2,
            status="UPCOMING"
        )
        self.db.add_all([sched_a, sched_b, sched_c])
        self.db.commit()

        # Run get_user_revisions
        result = SmartRevisionService.get_user_revisions(self.db, self.user_id)

        # Check categorization
        self.assertEqual(len(result["overdue"]), 1)
        self.assertEqual(result["overdue"][0]["topic_id"], self.topic_a_id)

        self.assertEqual(len(result["due_today"]), 1)
        self.assertEqual(result["due_today"][0]["topic_id"], self.topic_b_id)

        self.assertEqual(len(result["tomorrow"]), 1)
        self.assertEqual(result["tomorrow"][0]["topic_id"], self.topic_c_id)

        # Check attempt count and failed_attempts on Topic A:
        # Exactly 2 genuine attempts, 1 failed attempt (< 70%).
        # Synthetic evaluations MUST NOT inflate attempts to 4 or failed_attempts to 3.
        card_a = result["overdue"][0]
        self.assertEqual(card_a["attempts"], 2, "Synthetic evaluations must be excluded from attempts count!")

        # Priority calculation check for Topic A:
        # base: 100 - 75 = 25.0
        # overdue bonus: +20
        # failed_attempts bonus: 1 * 5 = +5
        # Total expected without gap/trend: 25 + 20 + 5 = 50.0
        self.assertGreaterEqual(card_a["priority_score"], 50.0)

        # Check summary structure
        summary = result["summary"]
        self.assertEqual(summary["overdue_count"], 1)
        self.assertEqual(summary["due_today_count"], 1)
        self.assertEqual(summary["tomorrow_count"], 1)
        self.assertEqual(summary["total_scheduled"], 3)

    # -------------------------------------------------------------------------
    # 7. User Data Isolation
    # -------------------------------------------------------------------------

    def test_10_user_isolation(self):
        """Verify User A's revision items never leak into User B's revision list or summary."""
        # Seed schedule for User A (self.user)
        SmartRevisionService.update_revision_schedule(
            db=self.db,
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            new_mastery_score=70.0
        )

        # Seed User B
        suffix_b = uuid.uuid4().hex[:6]
        user_b = models.User(
            name="User B",
            username=f"user_b_{suffix_b}",
            email=f"user_b_{suffix_b}@example.com",
            password_hash=auth.hash_password("Password123!")
        )
        self.db.add(user_b)
        self.db.commit()
        self.db.refresh(user_b)

        token_b = auth.create_access_token({"sub": str(user_b.id)})
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Query User B's revisions via service
        rev_b = SmartRevisionService.get_user_revisions(self.db, user_b.id)
        self.assertEqual(rev_b["summary"]["total_scheduled"], 0)
        self.assertEqual(len(rev_b["due_today"]), 0)
        self.assertEqual(len(rev_b["overdue"]), 0)

        # Query User B via API endpoint
        res = self.client.get("/api/revisions", headers=headers_b)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["summary"]["total_scheduled"], 0)

        # Cleanup User B
        self.db.query(models.User).filter(models.User.id == user_b.id).delete()
        self.db.commit()

    # -------------------------------------------------------------------------
    # 8. API Endpoints Integration Tests
    # -------------------------------------------------------------------------

    def test_11_api_get_revisions_endpoints(self):
        """Verify /api/revisions, /summary, /today, /overdue, /upcoming endpoints."""
        now = datetime.now(timezone.utc)
        sched = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            current_mastery_score=65.0,
            last_mastery_score=65.0,
            next_review_at=now,
            last_reviewed_at=now - timedelta(days=1),
            review_count=1,
            status="DUE"
        )
        self.db.add(sched)
        self.db.commit()

        # GET /api/revisions
        res = self.client.get("/api/revisions", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("summary", data)
        self.assertIn("due_today", data)

        # GET /api/revisions/summary
        res_sum = self.client.get("/api/revisions/summary", headers=self.headers)
        self.assertEqual(res_sum.status_code, 200)
        self.assertIn("due_today_count", res_sum.json())

        # GET /api/revisions/today
        res_today = self.client.get("/api/revisions/today", headers=self.headers)
        self.assertEqual(res_today.status_code, 200)
        self.assertEqual(len(res_today.json()), 1)

        # GET /api/revisions/overdue
        res_overdue = self.client.get("/api/revisions/overdue", headers=self.headers)
        self.assertEqual(res_overdue.status_code, 200)
        self.assertIsInstance(res_overdue.json(), list)

        # GET /api/revisions/upcoming
        res_up = self.client.get("/api/revisions/upcoming", headers=self.headers)
        self.assertEqual(res_up.status_code, 200)
        self.assertIn("tomorrow", res_up.json())
        self.assertIn("upcoming", res_up.json())

    def test_12_api_revision_history_and_briefing(self):
        """Verify /api/revisions/{topic_id}/start and /history endpoints."""
        # Seed genuine evaluation
        self._create_genuine_eval(topic_id=self.topic_b_id, score=78, days_ago=2)

        # Seed revision schedule
        sched = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_b_id,
            current_mastery_score=78.0,
            last_mastery_score=78.0,
            next_review_at=datetime.now(timezone.utc) + timedelta(days=3),
            review_count=1
        )
        self.db.add(sched)
        self.db.commit()

        # POST /api/revisions/{topic_id}/start
        res_start = self.client.post(f"/api/revisions/{self.topic_b_id}/start", headers=self.headers)
        self.assertEqual(res_start.status_code, 200)
        briefing = res_start.json()
        self.assertEqual(briefing["topic_id"], self.topic_b_id)
        self.assertEqual(briefing["current_mastery"], 78.0)
        self.assertIn("revision_goal", briefing)

        # GET /api/revisions/{topic_id}/history
        res_hist = self.client.get(f"/api/revisions/{self.topic_b_id}/history", headers=self.headers)
        self.assertEqual(res_hist.status_code, 200)
        history = res_hist.json()
        self.assertEqual(history["topic_id"], self.topic_b_id)
        self.assertEqual(history["total_attempts"], 1)
        self.assertEqual(history["latest_score"], 78)

        # Test non-existent topic returns 404
        res_404 = self.client.post("/api/revisions/999999/start", headers=self.headers)
        self.assertEqual(res_404.status_code, 404)

    # -------------------------------------------------------------------------
    # 9. Complete Revision Session and Single Review Count Increment
    # -------------------------------------------------------------------------

    @patch("app.routes.evaluations_routes.evaluate_explanation", new_callable=AsyncMock)
    def test_13_complete_revision_session_increments_review_count_exactly_once(self, mock_evaluate):
        """
        Verify POST /api/revisions/{topic_id}/complete:
        1. Correctly parses and passes explanation to evaluation pipeline.
        2. Increments review_count by EXACTLY 1 (fixing the duplicate increment bug).
        3. Correctly tracks previous_mastery, new_mastery, and improvement.
        4. Accurately updates RevisionSchedule record in the database.
        """
        mock_evaluate.return_value = {
            "technicalAccuracy": 85,
            "conceptUnderstanding": 85,
            "completeness": 85,
            "examples": 85,
            "relevance": 85,
            "communication": 85,
            "grammar": 85,
            "vocabulary": 85,
            "feedback": "Outstanding explanation of cache invalidation techniques.",
            "strengths": ["Clear breakdown of write-through vs write-back caching"],
            "weaknesses": []
        }

        # Seed initial revision schedule with current_mastery 60.0 and review_count 1
        initial_sched = models.RevisionSchedule(
            user_id=self.user_id,
            topic_id=self.topic_a_id,
            current_mastery_score=60.0,
            last_mastery_score=60.0,
            next_review_at=datetime.now(timezone.utc),
            review_count=1,
            status="DUE"
        )
        self.db.add(initial_sched)
        self.db.commit()

        # Call complete revision endpoint
        payload = {
            "explanation": "Cache invalidation ensures that stale cached entries are evicted upon update.",
            "learning_mode": "technical"
        }
        res = self.client.post(
            f"/api/revisions/{self.topic_a_id}/complete",
            headers=self.headers,
            json=payload
        )

        self.assertEqual(res.status_code, 200, f"Expected 200 but got: {res.text}")
        data = res.json()

        # Verify response structure and calculations
        self.assertEqual(data["topic_id"], self.topic_a_id)
        self.assertEqual(data["previous_mastery"], 60.0)
        self.assertEqual(data["new_mastery"], 85.0)
        self.assertEqual(data["improvement"], 25.0)
        self.assertEqual(data["improvement_formatted"], "+25.0%")
        self.assertIn("next_revision_days", data)
        self.assertIn("next_review_at", data)

        # CRITICAL CHECK: Verify database record review_count is EXACTLY 2 (not 3)
        self.db.expire_all()
        updated_db_sched = self.db.query(models.RevisionSchedule).filter(
            models.RevisionSchedule.user_id == self.user_id,
            models.RevisionSchedule.topic_id == self.topic_a_id
        ).first()

        self.assertEqual(
            updated_db_sched.review_count, 2,
            f"Expected review_count to be 2, but found {updated_db_sched.review_count}! Duplicate update detected."
        )
        self.assertEqual(updated_db_sched.last_mastery_score, 60.0)
        self.assertEqual(updated_db_sched.current_mastery_score, 85.0)

    def test_14_complete_revision_input_validation(self):
        """Verify POST /api/revisions/{topic_id}/complete rejects empty or very short explanations."""
        res = self.client.post(
            f"/api/revisions/{self.topic_a_id}/complete",
            headers=self.headers,
            json={"explanation": "abc"}  # Less than 5 chars
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
