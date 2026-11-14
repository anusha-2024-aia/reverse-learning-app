import unittest
import warnings
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

from app.main import app
from app.database import get_db
from app.auth import get_current_user
from app.routes.topics_routes import get_topics as topics_get_topics

class TestRouteContracts(unittest.TestCase):
    """
    Regression and contract tests ensuring route uniqueness, OpenAPI integrity,
    topic list contracts, and Knowledge Gaps endpoint behaviors.
    """

    def setUp(self):
        app.dependency_overrides.clear()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    # -----------------------------------------------------------------
    # 1. Route Uniqueness & Collision Prevention
    # -----------------------------------------------------------------
    def test_01_no_duplicate_routes(self):
        """
        Verify that no two APIRoutes share the same HTTP method and path combination.
        Specifically verifies that /api/topics is registered exactly once to topics_routes.
        """
        seen_routes = {}
        for r in app.routes:
            if isinstance(r, APIRoute):
                for method in r.methods:
                    key = (method, r.path)
                    self.assertNotIn(
                        key, 
                        seen_routes, 
                        f"Duplicate route detected: {method} {r.path} registered by {r.endpoint} "
                        f"collides with previously registered {seen_routes.get(key)}"
                    )
                    seen_routes[key] = f"{r.endpoint.__module__}.{r.endpoint.__name__}"

        # Confirm GET /api/topics is exclusively handled by topics_routes.get_topics
        topic_routes = [
            r for r in app.routes 
            if isinstance(r, APIRoute) and r.path == "/api/topics" and "GET" in r.methods
        ]
        self.assertEqual(len(topic_routes), 1, "Expected exactly one GET /api/topics route")
        self.assertIs(topic_routes[0].endpoint, topics_get_topics)

    def test_02_no_duplicate_openapi_operation_ids(self):
        """
        Verify that app.openapi() generates with strictly unique operation IDs and
        produces zero duplicate operation ID warnings.
        """
        # Invalidate cached schema to force full regeneration
        app.openapi_schema = None

        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            schema = app.openapi()

            # Ensure no Duplicate Operation ID warnings were emitted
            dup_warnings = [
                w for w in captured_warnings 
                if issubclass(w.category, UserWarning) and "Duplicate Operation ID" in str(w.message)
            ]
            self.assertEqual(len(dup_warnings), 0, f"OpenAPI duplicate operation warnings: {dup_warnings}")

        # Check all operationIds in schema for uniqueness
        operation_ids = []
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if isinstance(operation, dict) and "operationId" in operation:
                    operation_ids.append(operation["operationId"])

        self.assertEqual(
            len(operation_ids), 
            len(set(operation_ids)), 
            "Found duplicate operationId values in OpenAPI schema"
        )

    # -----------------------------------------------------------------
    # 2. /api/topics Endpoint Contracts
    # -----------------------------------------------------------------
    def test_03_get_topics_response_structure(self):
        """
        Verify GET /api/topics returns a dictionary {'topics': [...]} containing
        expected topic properties, matching frontend expectations.
        """
        mock_db = MagicMock()
        mock_topic = MagicMock()
        mock_topic.id = 101
        mock_topic.name = "Recursion & Trees"
        mock_topic.curriculum_id = 1
        mock_topic.description = "Deep dive into recursion"

        mock_db.query.return_value.all.return_value = [mock_topic]
        app.dependency_overrides[get_db] = lambda: mock_db

        res = self.client.get("/api/topics")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Must be a dict with 'topics' list (NOT a raw array)
        self.assertIsInstance(data, dict)
        self.assertIn("topics", data)
        self.assertIsInstance(data["topics"], list)
        self.assertEqual(len(data["topics"]), 1)
        self.assertEqual(data["topics"][0]["id"], 101)
        self.assertEqual(data["topics"][0]["name"], "Recursion & Trees")
        self.assertEqual(data["topics"][0]["curriculum_id"], 1)
        self.assertEqual(data["topics"][0]["description"], "Deep dive into recursion")

    def test_04_get_topics_curriculum_filter(self):
        """
        Verify GET /api/topics?curriculum_id=2 applies filtering by curriculum_id.
        """
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = []

        app.dependency_overrides[get_db] = lambda: mock_db

        res = self.client.get("/api/topics?curriculum_id=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"topics": []})
        mock_query.filter.assert_called_once()

    # -----------------------------------------------------------------
    # 3. Knowledge Gaps Endpoint Contracts & Security
    # -----------------------------------------------------------------
    def test_05_knowledge_gaps_unauthenticated_returns_401(self):
        """
        Verify GET /api/knowledge-gaps requires authentication and returns 401 Unauthorized
        when called without credentials.
        """
        res = self.client.get("/api/knowledge-gaps")
        self.assertEqual(res.status_code, 401)

    @patch("app.routes.knowledge_gap_routes.analyze_user_knowledge")
    def test_06_knowledge_gaps_empty_user_receives_empty_list(self, mock_analyze):
        """
        Verify an authenticated user with no evaluation history receives {'gaps': []}.
        """
        mock_user = MagicMock()
        mock_user.id = 42
        mock_db = MagicMock()

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        mock_analyze.return_value = []

        res = self.client.get("/api/knowledge-gaps")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"gaps": []})
        mock_analyze.assert_called_once_with(mock_db, 42)

    @patch("app.routes.knowledge_gap_routes.analyze_user_knowledge")
    def test_07_knowledge_gaps_populated_history_has_all_nine_fields(self, mock_analyze):
        """
        Verify an authenticated user with evaluation history receives all nine expected fields:
        topic_id, topic_name, severity, trend, mastery_score, recent_score, average_score,
        attempts, recommendation.
        """
        mock_user = MagicMock()
        mock_user.id = 42
        mock_db = MagicMock()

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        mock_analyze.return_value = [
            {
                "topic_id": 12,
                "topic_name": "Dynamic Programming",
                "mastery_score": 52,
                "recent_score": 48,
                "average_score": 50,
                "attempts": 3,
                "severity": "CRITICAL",
                "trend": "DECLINING",
                "recommendation": "URGENT: Review Dynamic Programming fundamentals immediately."
            }
        ]

        res = self.client.get("/api/knowledge-gaps")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gaps", data)
        self.assertEqual(len(data["gaps"]), 1)

        gap = data["gaps"][0]
        expected_fields = [
            "topic_id", "topic_name", "severity", "trend",
            "mastery_score", "recent_score", "average_score",
            "attempts", "recommendation"
        ]
        for field in expected_fields:
            self.assertIn(field, gap, f"Missing expected field '{field}' in knowledge gap item")

        self.assertEqual(gap["topic_id"], 12)
        self.assertEqual(gap["severity"], "CRITICAL")
        self.assertEqual(gap["trend"], "DECLINING")
        self.assertEqual(gap["mastery_score"], 52)

    # -----------------------------------------------------------------
    # 4. Backward Compatibility for Dashboard Knowledge Gap URLs
    # -----------------------------------------------------------------
    def test_08_dashboard_knowledge_gap_both_urls_preserved(self):
        """
        Verify both /api/dashboard/knowledge-gap and /api/dashboard/knowledge-gap/
        remain functional, return HTTP 200, and preserve the existing response structure.
        """
        mock_user = MagicMock()
        mock_user.id = 42
        mock_db = MagicMock()

        # Mock an evaluation and a topic for the dashboard card
        mock_eval = MagicMock()
        mock_eval.topic_id = 7
        mock_eval.ai_score = 55
        mock_eval.ai_feedback_json = '{"weaknesses": ["Missed edge cases"]}'

        mock_topic = MagicMock()
        mock_topic.id = 7
        mock_topic.name = "Binary Search"

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_eval]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_topic

        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db

        # Test both path variants
        for path in ["/api/dashboard/knowledge-gap", "/api/dashboard/knowledge-gap/"]:
            with self.subTest(path=path):
                res = self.client.get(path)
                self.assertEqual(res.status_code, 200, f"Failed for path {path}")
                data = res.json()
                self.assertTrue(data.get("has_gap"))
                self.assertEqual(data.get("topic_id"), 7)
                self.assertEqual(data.get("topic"), "Binary Search")
                self.assertEqual(data.get("score"), 55)
                self.assertIn("status", data)
                self.assertIn("reason", data)
                self.assertIn("recommendation", data)

if __name__ == "__main__":
    unittest.main()

