import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.routes.evaluations_routes import get_current_user

class TestMockedAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def override_get_db():
            mock_db = MagicMock()
            mock_topic = MagicMock()
            mock_topic.name = "Test Topic"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_topic
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
            return mock_db

        def override_get_current_user():
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.username = "testuser"
            return mock_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    @patch("app.routes.evaluations_routes.ActivityService")
    @patch("app.routes.evaluations_routes.achievement_service")
    @patch("app.routes.evaluations_routes.AdaptiveEngine")
    @patch("app.routes.evaluations_routes.SmartRevisionService")
    @patch("app.routes.evaluations_routes.RoadmapService")
    @patch("app.routes.evaluations_routes.calculate_next_recommendation")
    @patch("app.routes.evaluations_routes.evaluate_explanation", new_callable=AsyncMock)
    def test_evaluate_endpoint(self, mock_evaluate, mock_rec, mock_roadmap, mock_revision, mock_adaptive, mock_achievement, mock_activity):
        mock_evaluate.return_value = {
            "overallScore": 85,
            "technicalAccuracy": {"score": 85, "feedback": "Good logic"},
            "conceptUnderstanding": {"score": 85, "feedback": "Solid concepts"},
            "completeness": {"score": 85, "feedback": "Fairly complete"},
            "examples": {"score": 85, "feedback": "Good example"},
            "relevance": {"score": 85, "feedback": "Highly relevant"},
            "communication": {"score": 85, "feedback": "Clear explanation"},
            "grammar": {"score": 85, "feedback": "No major grammar errors"},
            "vocabulary": {"score": 85, "feedback": "Good vocabulary"},
            "knowledgeGaps": [],
            "actionItems": ["Keep practicing"],
            "improvedVersion": "Polished version"
        }
        
        payload = {
            "topic_id": 1,
            "explanation": "This is my test transcript explaining recursion.",
            "learning_mode": "general"
        }
        
        response = self.client.post("/api/evaluate", json=payload)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("score", json_data)
        self.assertEqual(json_data["score"], 85)

    def test_health_check_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

if __name__ == "__main__":
    unittest.main()
