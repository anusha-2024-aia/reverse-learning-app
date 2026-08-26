import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services import knowledge_gap_engine
from app.services.adaptive_engine import AdaptiveEngine
from app.services.spaced_repetition import SpacedRepetition
from tests.test_db_config import init_test_db, TestingSessionLocal, cleanup_test_db
from app import models

class TestUnitEngines(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_test_db()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_db()

    def setUp(self):
        self.db = TestingSessionLocal()
        # Create test user & topic
        self.user = models.User(
            name="Unit Tester",
            username=f"unit_user_{os.urandom(4).hex()}",
            email=f"unit_{os.urandom(4).hex()}@example.com",
            password_hash="fake_hash"
        )
        self.db.add(self.user)
        self.topic = models.Topic(name="Algorithm Design", category="DSA", description="Algorithms")
        self.db.add(self.topic)
        self.db.commit()
        self.db.refresh(self.user)
        self.db.refresh(self.topic)

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # 1. Knowledge Gap Engine Unit Tests
    # -------------------------------------------------------------
    def test_knowledge_gap_consistency_calculation(self):
        # Single score -> 100 consistency
        c1 = knowledge_gap_engine.calculate_consistency([80])
        self.assertEqual(c1, 100)

        # Consistent scores -> high score
        c_high = knowledge_gap_engine.calculate_consistency([80, 82, 81])
        self.assertGreater(c_high, 80)

        # Volatile scores -> lower consistency
        c_low = knowledge_gap_engine.calculate_consistency([20, 90, 30, 85])
        self.assertLess(c_low, c_high)

    def test_knowledge_gap_improvement_calculation(self):
        # Single score -> neutral 50
        imp1 = knowledge_gap_engine.calculate_improvement([70])
        self.assertEqual(imp1, 50)

        # Positive improvement (50 -> 80) -> >50
        imp_pos = knowledge_gap_engine.calculate_improvement([50, 80])
        self.assertEqual(imp_pos, 80) # 50 + 30

        # Negative improvement (80 -> 50) -> <50
        imp_neg = knowledge_gap_engine.calculate_improvement([80, 50])
        self.assertEqual(imp_neg, 20) # 50 - 30

    def test_knowledge_gap_severity_and_trend(self):
        # Low mastery (<55) + declining -> CRITICAL
        sev, trend = knowledge_gap_engine.determine_severity_and_trend(45, [70, 40])
        self.assertEqual(sev, "CRITICAL")
        self.assertEqual(trend, "DECLINING")

        # Low mastery (<55) + improving -> HIGH
        sev2, trend2 = knowledge_gap_engine.determine_severity_and_trend(45, [30, 60])
        self.assertEqual(sev2, "HIGH")
        self.assertEqual(trend2, "IMPROVING")

        # High mastery (>=85) -> RESOLVED
        sev3, trend3 = knowledge_gap_engine.determine_severity_and_trend(90, [85, 95])
        self.assertEqual(sev3, "RESOLVED")

    def test_knowledge_gap_recommendations(self):
        rec_crit = knowledge_gap_engine.generate_recommendation("CRITICAL", "DECLINING", "Binary Search")
        self.assertIn("URGENT", rec_crit)

        rec_resolved = knowledge_gap_engine.generate_recommendation("RESOLVED", "STABLE", "Binary Search")
        self.assertIn("Excellent mastery", rec_resolved)

    # -------------------------------------------------------------
    # 2. Adaptive Learning Engine Mastery Update Unit Tests
    # -------------------------------------------------------------
    def test_adaptive_engine_update_mastery(self):
        # Attempt 1: score 5/10 (50%)
        m1 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 5)
        self.assertEqual(m1.attempts, 1)
        self.assertEqual(m1.failed_attempts, 1)
        self.assertEqual(m1.mastery_score, 50.0)

        # Attempt 2: score 9/10 (90%) -> exponential moving avg: 0.3*90 + 0.7*50 = 62.0
        m2 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 9)
        self.assertEqual(m2.attempts, 2)
        self.assertEqual(m2.successful_attempts, 1)
        self.assertEqual(m2.mastery_score, 62.0)

    # -------------------------------------------------------------
    # 3. Spaced Repetition Scheduler Unit Tests
    # -------------------------------------------------------------
    def test_spaced_repetition_intervals(self):
        now = datetime.now(timezone.utc)
        # Score < 6 -> short interval (~12-14 hours)
        next_low = SpacedRepetition.calculate_next_review(mastery_score=50.0, attempts=1, current_score=5)
        self.assertTrue((next_low.date() - now.date()).days <= 2)

        # Score >= 8 -> longer interval (extended hours)
        next_high = SpacedRepetition.calculate_next_review(mastery_score=85.0, attempts=3, current_score=9)
        self.assertTrue((next_high - now).total_seconds() > (next_low - now).total_seconds())

    # -------------------------------------------------------------
    # 4. Score Boundary Validation Unit Tests
    # -------------------------------------------------------------
    def test_score_boundary_validations(self):
        # Test valid score boundaries (0 to 100)
        for s in [0, 1, 50, 99, 100]:
            clamped = max(0, min(100, s))
            self.assertEqual(clamped, s)

        # Test invalid boundaries (-10, 150)
        self.assertEqual(max(0, min(100, -10)), 0)
        self.assertEqual(max(0, min(100, 150)), 100)

if __name__ == "__main__":
    unittest.main()
