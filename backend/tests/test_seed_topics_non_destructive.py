import os
import sys
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import models
from app.main import seed_topics

class TestNonDestructiveSeeding(unittest.TestCase):
    def setUp(self):
        # Use a fresh, isolated in-memory SQLite database for every test
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False}
        )
        models.Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_initial_seeding_creates_all_curricula_and_topics(self):
        """Verify seed_topics creates all expected curricula and topics on a fresh database."""
        seed_topics(db_session=self.db)

        curricula = self.db.query(models.Curriculum).all()
        topics = self.db.query(models.Topic).all()

        self.assertGreaterEqual(len(curricula), 9)
        self.assertGreaterEqual(len(topics), 100)

        # Verify all topics have valid curriculum_id and order_in_curriculum
        for t in topics:
            self.assertIsNotNone(t.curriculum_id)
            self.assertIsNotNone(t.order_in_curriculum)
            self.assertEqual(t.category, "Engineering")

    def test_seeding_twice_is_idempotent_and_creates_no_duplicates(self):
        """Verify executing seed_topics repeatedly does not duplicate topics or alter IDs."""
        seed_topics(db_session=self.db)
        initial_topics = self.db.query(models.Topic).order_by(models.Topic.id).all()
        initial_count = len(initial_topics)
        initial_id_map = {t.name: t.id for t in initial_topics}

        # Run seeding second time
        seed_topics(db_session=self.db)
        second_topics = self.db.query(models.Topic).order_by(models.Topic.id).all()
        second_count = len(second_topics)
        second_id_map = {t.name: t.id for t in second_topics}

        self.assertEqual(initial_count, second_count)
        self.assertEqual(initial_id_map, second_id_map)

    def test_existing_topic_ids_and_student_records_preserved(self):
        """
        Verify that when a curriculum has pre-existing topics and associated student records,
        running seed_topics inserts missing topics while preserving pre-existing topic IDs and records.
        """
        # 1. Manually create Python Mastery with only 2 initial topics
        cur = models.Curriculum(name="Python Mastery", description="Test desc", difficulty="beginner")
        self.db.add(cur)
        self.db.commit()
        self.db.refresh(cur)

        t1 = models.Topic(name="Introduction to Python & Setup", category="Engineering", curriculum_id=cur.id, order_in_curriculum=1)
        t2 = models.Topic(name="Variables, Data Types & Operators", category="Engineering", curriculum_id=cur.id, order_in_curriculum=2)
        self.db.add_all([t1, t2])
        self.db.commit()
        self.db.refresh(t1)
        self.db.refresh(t2)

        original_t1_id = t1.id
        original_t2_id = t2.id

        # 2. Create student user and link historical student records to these topics
        user = models.User(
            name="Alice Student",
            username="alice",
            email="alice@example.com",
            password_hash="fakehash123"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        eval_record = models.Evaluation(
            user_id=user.id,
            topic_id=original_t1_id,
            overall_score=85,
            ai_score=85,
            explanation="Python is an interpreted high-level programming language."
        )
        session_record = models.StudySession(
            user_id=user.id,
            topic_id=original_t2_id
        )
        mastery_record = models.UserMastery(
            user_id=user.id,
            topic_id=original_t1_id,
            mastery_score=85.0
        )
        revision_record = models.RevisionSchedule(
            user_id=user.id,
            topic_id=original_t2_id,
            current_mastery_score=80.0
        )
        self.db.add_all([eval_record, session_record, mastery_record, revision_record])
        self.db.commit()

        eval_id = eval_record.id
        session_id = session_record.id

        # 3. Execute seed_topics: it should detect 14 missing topics for Python Mastery
        seed_topics(db_session=self.db)

        # 4. Verify pre-existing topics retained their exact original IDs
        t1_after = self.db.query(models.Topic).filter(models.Topic.name == "Introduction to Python & Setup").first()
        t2_after = self.db.query(models.Topic).filter(models.Topic.name == "Variables, Data Types & Operators").first()
        self.assertEqual(t1_after.id, original_t1_id)
        self.assertEqual(t2_after.id, original_t2_id)

        # 5. Verify missing topics were inserted
        python_topics = self.db.query(models.Topic).filter(models.Topic.curriculum_id == cur.id).all()
        self.assertEqual(len(python_topics), 16) # Full Python Mastery topic count

        # 6. Verify student records referencing original topic IDs are completely intact
        saved_eval = self.db.query(models.Evaluation).filter(models.Evaluation.id == eval_id).first()
        self.assertIsNotNone(saved_eval)
        self.assertEqual(saved_eval.topic_id, original_t1_id)
        self.assertEqual(saved_eval.overall_score, 85)

        saved_session = self.db.query(models.StudySession).filter(models.StudySession.id == session_id).first()
        self.assertIsNotNone(saved_session)
        self.assertEqual(saved_session.topic_id, original_t2_id)

        saved_mastery = self.db.query(models.UserMastery).filter(models.UserMastery.topic_id == original_t1_id).first()
        self.assertIsNotNone(saved_mastery)
        self.assertEqual(saved_mastery.user_id, user.id)

    def test_case_insensitive_and_whitespace_duplicate_prevention(self):
        """
        Verify that topics with different casing or leading/trailing whitespace
        are detected as existing, do not produce duplicates, and preserve original display names.
        """
        cur = models.Curriculum(name="Python Mastery", description="Test desc", difficulty="beginner")
        self.db.add(cur)
        self.db.commit()
        self.db.refresh(cur)

        # Pre-seed with distinct casing and extra whitespace
        t1 = models.Topic(name="  introduction to python & setup  ", category="Engineering", curriculum_id=cur.id, order_in_curriculum=1)
        t2 = models.Topic(name="VARIABLES, DATA TYPES & OPERATORS", category="Engineering", curriculum_id=cur.id, order_in_curriculum=2)
        self.db.add_all([t1, t2])
        self.db.commit()
        self.db.refresh(t1)
        self.db.refresh(t2)

        original_t1_id = t1.id
        original_t2_id = t2.id

        seed_topics(db_session=self.db)

        # 1. Total Python topics must be exactly 16 (no duplicates added for t1 or t2)
        python_topics = self.db.query(models.Topic).filter(models.Topic.curriculum_id == cur.id).all()
        self.assertEqual(len(python_topics), 16)

        # 2. Original display names must be preserved
        reloaded_t1 = self.db.query(models.Topic).filter(models.Topic.id == original_t1_id).first()
        reloaded_t2 = self.db.query(models.Topic).filter(models.Topic.id == original_t2_id).first()
        self.assertEqual(reloaded_t1.name, "  introduction to python & setup  ")
        self.assertEqual(reloaded_t2.name, "VARIABLES, DATA TYPES & OPERATORS")

    def test_atomic_rollback_on_failure_before_commit(self):
        """
        Verify that if an error occurs during seeding before the final commit,
        the entire transaction rolls back and leaves no partial data.
        """
        from unittest.mock import patch

        # Simulate a failure when processing topics for the 3rd curriculum
        original_add_all = self.db.add_all
        call_count = 0

        def failing_add_all(instances):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise RuntimeError("Simulated mid-seeding database error")
            return original_add_all(instances)

        with patch.object(self.db, "add_all", side_effect=failing_add_all):
            with self.assertRaises(RuntimeError):
                seed_topics(db_session=self.db)

        # After rollback, zero curricula and zero topics should be persisted
        # Create a new session on the engine to verify committed state
        verification_db = self.Session()
        try:
            curricula_count = verification_db.query(models.Curriculum).count()
            topics_count = verification_db.query(models.Topic).count()
            self.assertEqual(curricula_count, 0)
            self.assertEqual(topics_count, 0)
        finally:
            verification_db.close()

    def test_seed_topics_default_session(self):
        """Verify calling seed_topics without arguments uses default SessionLocal and closes properly."""
        from unittest.mock import patch, MagicMock
        mock_session = MagicMock()
        with patch('app.main.SessionLocal', return_value=mock_session):
            seed_topics()
            mock_session.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
