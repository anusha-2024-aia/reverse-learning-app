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
    # 2. Adaptive Learning Engine Mastery Update Unit Tests (0-100 Scale)
    # -------------------------------------------------------------
    def test_adaptive_engine_update_mastery(self):
        # Attempt 1: score 42/100 -> failure (< 70), initial mastery = 42.0
        m1 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 42)
        self.assertEqual(m1.attempts, 1)
        self.assertEqual(m1.failed_attempts, 1)
        self.assertEqual(m1.successful_attempts, 0)
        self.assertEqual(m1.mastery_score, 42.0)

        # Attempt 2: score 92/100 -> success (>= 70), EMA: 0.3*92 + 0.7*42 = 27.6 + 29.4 = 57.0
        m2 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 92)
        self.assertEqual(m2.attempts, 2)
        self.assertEqual(m2.failed_attempts, 1)
        self.assertEqual(m2.successful_attempts, 1)
        self.assertEqual(m2.mastery_score, 57.0)

        # Attempt 3: score 70/100 -> success (boundary >= 70), EMA: 0.3*70 + 0.7*57 = 21.0 + 39.9 = 60.9
        m3 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 70)
        self.assertEqual(m3.attempts, 3)
        self.assertEqual(m3.failed_attempts, 1)
        self.assertEqual(m3.successful_attempts, 2)
        self.assertAlmostEqual(m3.mastery_score, 60.9, places=2)

        # Attempt 4: score 0/100 -> failure
        m4 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 0)
        self.assertEqual(m4.attempts, 4)
        self.assertEqual(m4.failed_attempts, 2)
        self.assertEqual(m4.successful_attempts, 2)
        self.assertTrue(0.0 <= m4.mastery_score <= 100.0)

        # Attempt 5: score 100/100 -> success
        m5 = AdaptiveEngine.update_mastery(self.db, self.user.id, self.topic.id, 100)
        self.assertEqual(m5.attempts, 5)
        self.assertEqual(m5.failed_attempts, 2)
        self.assertEqual(m5.successful_attempts, 3)
        self.assertTrue(0.0 <= m5.mastery_score <= 100.0)

    def test_adaptive_engine_mastery_never_exceeds_100(self):
        # Fresh topic for boundary validation
        t_bound = models.Topic(name="Boundary Topic", category="DSA", description="Test Boundaries")
        self.db.add(t_bound)
        self.db.commit()
        self.db.refresh(t_bound)

        # Even with out-of-range input like 150, mastery is clamped to <= 100
        m_high = AdaptiveEngine.update_mastery(self.db, self.user.id, t_bound.id, 150)
        self.assertEqual(m_high.mastery_score, 100.0)
        self.assertEqual(m_high.successful_attempts, 1)

        # Repeated 100 scores keep mastery at 100.0 (never exceeds)
        m_high2 = AdaptiveEngine.update_mastery(self.db, self.user.id, t_bound.id, 100)
        self.assertEqual(m_high2.mastery_score, 100.0)

        # Negative input clamped to >= 0
        t_neg = models.Topic(name="Negative Topic", category="DSA", description="Test Negatives")
        self.db.add(t_neg)
        self.db.commit()
        self.db.refresh(t_neg)
        m_neg = AdaptiveEngine.update_mastery(self.db, self.user.id, t_neg.id, -25)
        self.assertEqual(m_neg.mastery_score, 0.0)
        self.assertEqual(m_neg.failed_attempts, 1)

    # -------------------------------------------------------------
    # 3. Spaced Repetition Scheduler Unit Tests (0-100 Scale)
    # -------------------------------------------------------------
    def test_spaced_repetition_intervals(self):
        now = datetime.now(timezone.utc)

        # Score < 60 -> short interval (24h * 0.5 * 1.2 = 14.4 hours on attempt 1)
        next_low = SpacedRepetition.calculate_next_review(mastery_score=42.0, attempts=1, current_score=42)
        diff_low_hours = (next_low - now).total_seconds() / 3600.0
        self.assertAlmostEqual(diff_low_hours, 14.4, delta=0.5)

        # Score in [60, 80) -> medium interval (24h * 1.0 * 1.2 = 28.8 hours on attempt 1)
        next_med = SpacedRepetition.calculate_next_review(mastery_score=60.0, attempts=1, current_score=70)
        diff_med_hours = (next_med - now).total_seconds() / 3600.0
        self.assertAlmostEqual(diff_med_hours, 28.8, delta=0.5)

        # Score >= 80 -> extended interval: 24h * (1.5 + 85.0/50.0) * (1.0 + 3*0.2) = 24 * 3.2 * 1.6 = 122.88 hours
        next_high = SpacedRepetition.calculate_next_review(mastery_score=85.0, attempts=3, current_score=92)
        diff_high_hours = (next_high - now).total_seconds() / 3600.0
        self.assertAlmostEqual(diff_high_hours, 122.88, delta=0.5)

        self.assertTrue(next_high > next_med > next_low)

        # 720-hour maximum interval cap
        next_capped = SpacedRepetition.calculate_next_review(mastery_score=100.0, attempts=50, current_score=100)
        diff_capped_hours = (next_capped - now).total_seconds() / 3600.0
        self.assertAlmostEqual(diff_capped_hours, 720.0, delta=0.5)

        # Out-of-bounds mastery is safely constrained
        next_clamped_mastery = SpacedRepetition.calculate_next_review(mastery_score=800.0, attempts=1, current_score=90)
        diff_clamped_hours = (next_clamped_mastery - now).total_seconds() / 3600.0
        # Clamped mastery 100.0 -> interval_multiplier = 1.5 + 2.0 = 3.5 -> 24 * 3.5 * 1.2 = 100.8 hours
        self.assertAlmostEqual(diff_clamped_hours, 100.8, delta=0.5)

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
