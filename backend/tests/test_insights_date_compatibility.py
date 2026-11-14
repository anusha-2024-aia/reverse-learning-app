import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timezone
from fastapi.testclient import TestClient

from app.services.insights_service import _coerce_to_date, calculate_streak, calculate_score_trend
from app.main import app
from app.database import get_db
from app.auth import get_current_user

class TestInsightsDateCompatibility(unittest.TestCase):
    
    # -----------------------------------------------------------------
    # 1. Unit Tests for _coerce_to_date helper
    # -----------------------------------------------------------------
    def test_coerce_from_date(self):
        d = date(2026, 11, 5)
        self.assertEqual(_coerce_to_date(d), d)

    def test_coerce_from_datetime(self):
        dt = datetime(2026, 11, 5, 14, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(_coerce_to_date(dt), date(2026, 11, 5))

    def test_coerce_from_iso_string(self):
        self.assertEqual(_coerce_to_date("2026-11-05"), date(2026, 11, 5))
        self.assertEqual(_coerce_to_date("  2026-11-05  "), date(2026, 11, 5))
        self.assertEqual(_coerce_to_date("2026-11-05T08:00:00Z"), date(2026, 11, 5))

    def test_coerce_from_invalid_type(self):
        with self.assertRaises(TypeError):
            _coerce_to_date(12345)
        with self.assertRaises(TypeError):
            _coerce_to_date(None)
        with self.assertRaises(TypeError):
            _coerce_to_date("")

    # -----------------------------------------------------------------
    # 2. calculate_streak with frozen reference date (2026-11-05)
    # -----------------------------------------------------------------
    def _mock_db_with_eval_dates(self, return_values):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_distinct = mock_filter.distinct.return_value
        mock_order = mock_distinct.order_by.return_value
        # Each row returned by SQLAlchemy query(func.date(...)) is a 1-tuple
        mock_order.all.return_value = [(v,) for v in return_values]
        return mock_db

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_empty_history(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        mock_db = self._mock_db_with_eval_dates([])
        
        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 0)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_postgresql_date_objects(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        # PostgreSQL returns Python datetime.date objects
        pg_dates = [date(2026, 11, 5), date(2026, 11, 4), date(2026, 11, 3)]
        mock_db = self._mock_db_with_eval_dates(pg_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 3)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_sqlite_strings(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        # SQLite returns string dates
        sqlite_dates = ["2026-11-05", "2026-11-04", "2026-11-03"]
        mock_db = self._mock_db_with_eval_dates(sqlite_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 3)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_datetime_objects(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        dt_dates = [datetime(2026, 11, 5, 9, 0), datetime(2026, 11, 4, 17, 30)]
        mock_db = self._mock_db_with_eval_dates(dt_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 2)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_broken(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        # Evaluated today and yesterday, but skipped day before
        broken_dates = [date(2026, 11, 5), date(2026, 11, 4), date(2026, 11, 2)]
        mock_db = self._mock_db_with_eval_dates(broken_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 2)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_older_than_yesterday(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        # Last evaluation was 2 days ago (2026-11-03)
        old_dates = [date(2026, 11, 3)]
        mock_db = self._mock_db_with_eval_dates(old_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 0)

    @patch("app.services.insights_service.datetime")
    def test_calculate_streak_yesterday_only(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        # User evaluated yesterday, not yet today -> streak is still active (1)
        yesterday_dates = [date(2026, 11, 4)]
        mock_db = self._mock_db_with_eval_dates(yesterday_dates)

        streak = calculate_streak(mock_db, user_id=1)
        self.assertEqual(streak, 1)

    # -----------------------------------------------------------------
    # 3. calculate_score_trend serialization consistency
    # -----------------------------------------------------------------
    def test_calculate_score_trend_with_date_objects(self):
        mock_db = MagicMock()
        stat1 = MagicMock()
        stat1.date = date(2026, 11, 4)
        stat1.avg_score = 85.0
        stat1.count = 2

        stat2 = MagicMock()
        stat2.date = "2026-11-05" # string variant
        stat2.avg_score = 90.0
        stat2.count = 3

        mock_db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = [stat1, stat2]

        result = calculate_score_trend(mock_db, user_id=1, days=7)
        trend = result["trend"]

        self.assertEqual(len(trend), 2)
        # Both must be ISO formatted strings
        self.assertEqual(trend[0]["date"], "2026-11-04")
        self.assertEqual(trend[1]["date"], "2026-11-05")
        self.assertIsInstance(trend[0]["date"], str)
        self.assertIsInstance(trend[1]["date"], str)

    # -----------------------------------------------------------------
    # 4. Endpoint integration test for /api/insights/summary
    # -----------------------------------------------------------------
    def test_api_insights_summary_endpoint(self):
        mock_db = MagicMock()
        # total_evals
        mock_db.query.return_value.filter.return_value.count.return_value = 0

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "test_insights_user"

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            client = TestClient(app)
            response = client.get("/api/insights/summary")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("total_evaluations", data)
            self.assertIn("current_streak", data)
            self.assertIn("average_score", data)
            self.assertIn("days_active", data)
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_current_user, None)

if __name__ == "__main__":
    unittest.main()

