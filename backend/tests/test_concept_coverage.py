import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.routes.evaluations_routes import get_current_user
from app.services.concept_coverage_service import calculate_concept_coverage, normalize_text

class TestConceptCoverage(unittest.TestCase):

    def test_01_all_concepts_covered(self):
        required = [
            {"concept": "Client", "aliases": ["client"]},
            {"concept": "Server", "aliases": ["server"]},
            {"concept": "Request", "aliases": ["request"]},
            {"concept": "Response", "aliases": ["response"]}
        ]
        explanation = "The client sends a request to the server, and the server returns a response."
        result = calculate_concept_coverage(explanation, "client-server architecture", required_concepts=required)
        
        self.assertEqual(result["required_count"], 4)
        self.assertEqual(result["covered_count"], 4)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertEqual(len(result["covered_concepts"]), 4)
        self.assertEqual(len(result["missing_concepts"]), 0)

    def test_02_half_concepts_covered(self):
        required = [
            {"concept": "Client", "aliases": ["client"]},
            {"concept": "Server", "aliases": ["server"]},
            {"concept": "Request", "aliases": ["request"]},
            {"concept": "Response", "aliases": ["response"]}
        ]
        explanation = "The client sends a message to the server."
        result = calculate_concept_coverage(explanation, "client-server architecture", required_concepts=required)
        
        self.assertEqual(result["required_count"], 4)
        self.assertEqual(result["covered_count"], 2)
        self.assertEqual(result["coverage_percentage"], 50.0)
        self.assertIn("Client", result["covered_concepts"])
        self.assertIn("Server", result["covered_concepts"])
        self.assertIn("Request", result["missing_concepts"])
        self.assertIn("Response", result["missing_concepts"])

    def test_03_no_concepts_covered(self):
        required = [
            {"concept": "Client", "aliases": ["client"]},
            {"concept": "Server", "aliases": ["server"]}
        ]
        explanation = "This is a completely unrelated text about cooking pizza."
        result = calculate_concept_coverage(explanation, "client-server architecture", required_concepts=required)
        
        self.assertEqual(result["required_count"], 2)
        self.assertEqual(result["covered_count"], 0)
        self.assertEqual(result["coverage_percentage"], 0.0)
        self.assertEqual(len(result["covered_concepts"]), 0)
        self.assertEqual(len(result["missing_concepts"]), 2)

    def test_04_case_insensitive_matching(self):
        required = [
            {"concept": "HTTP Protocol", "aliases": ["http"]}
        ]
        explanation = "The communication happens over HTTP."
        result = calculate_concept_coverage(explanation, "custom topic", required_concepts=required)
        
        self.assertEqual(result["covered_count"], 1)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertIn("HTTP Protocol", result["covered_concepts"])

    def test_05_punctuation_and_whitespace_normalization(self):
        required = [
            {"concept": "ACID Properties", "aliases": ["acid"]}
        ]
        explanation = "Does the database support ACID??? Yes, it does!"
        result = calculate_concept_coverage(explanation, "custom topic", required_concepts=required)
        
        self.assertEqual(result["covered_count"], 1)
        self.assertEqual(result["coverage_percentage"], 100.0)

    def test_06_missing_concepts_correctly_returned(self):
        required = [
            {"concept": "Client", "aliases": ["client"]},
            {"concept": "Server", "aliases": ["server"]},
            {"concept": "Statelessness", "aliases": ["stateless"]}
        ]
        explanation = "The client connects to the server."
        result = calculate_concept_coverage(explanation, "custom topic", required_concepts=required)
        
        self.assertIn("Statelessness", result["missing_concepts"])
        self.assertEqual(len(result["missing_concepts"]), 1)

    def test_07_zero_required_concepts_safety(self):
        result = calculate_concept_coverage("Some explanation", "custom topic", required_concepts=[])
        
        self.assertEqual(result["required_count"], 0)
        self.assertEqual(result["covered_count"], 0)
        self.assertIsNone(result["coverage_percentage"])

    def test_08_false_positive_prevention(self):
        required = [
            {"concept": "Inheritance", "aliases": ["inheritance"]}
        ]
        explanation = "You can inherit properties from a base class."
        result = calculate_concept_coverage(explanation, "custom topic", required_concepts=required)
        
        self.assertEqual(result["covered_count"], 0)
        self.assertIn("Inheritance", result["missing_concepts"])

    @patch("app.routes.evaluations_routes.ActivityService")
    @patch("app.routes.evaluations_routes.achievement_service")
    @patch("app.routes.evaluations_routes.AdaptiveEngine")
    @patch("app.routes.evaluations_routes.SmartRevisionService")
    @patch("app.routes.evaluations_routes.RoadmapService")
    @patch("app.routes.evaluations_routes.calculate_next_recommendation")
    @patch("app.routes.evaluations_routes.evaluate_explanation", new_callable=AsyncMock)
    def test_09_evaluate_endpoint_integration(self, mock_evaluate, mock_rec, mock_roadmap, mock_revision, mock_adaptive, mock_achievement, mock_activity):
        def override_get_db():
            mock_db = MagicMock()
            mock_topic = MagicMock()
            mock_topic.name = "Client-Server Architecture"
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
        client = TestClient(app)

        try:
            mock_evaluate.return_value = {
                "technicalAccuracy": {"score": 90, "feedback": "Great accuracy"},
                "conceptUnderstanding": {"score": 85, "feedback": "Good understanding"},
                "completeness": {"score": 80, "feedback": "Complete"},
                "examples": {"score": 75, "feedback": "Decent examples"},
                "relevance": {"score": 90, "feedback": "Relevant"},
                "communication": {"score": 85, "feedback": "Clear"},
                "grammar": {"score": 95, "feedback": "Good grammar"},
                "vocabulary": {"score": 90, "feedback": "Good vocab"},
                "strengths": ["Clear explanation"],
                "weaknesses": [],
                "knowledgeGaps": [],
                "summary": "Solid explanation.",
                "correct_version": "Ideal client-server explanation.",
                "follow_up_question": "What is statelessness?",
                "learning_suggestions": []
            }
            
            payload = {
                "topic_id": 1,
                "explanation": "The client sends a request to the server over HTTP, and the server returns a response.",
                "learning_mode": "technical"
            }
            
            response = client.post("/api/evaluate", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("concept_coverage", data)
            cc = data["concept_coverage"]
            self.assertGreater(cc["required_count"], 0)
            self.assertGreater(cc["covered_count"], 0)
            self.assertGreater(cc["coverage_percentage"], 0.0)
        finally:
            app.dependency_overrides.clear()

if __name__ == "__main__":
    unittest.main()
