import pytest
import json
from unittest.mock import patch
from app.ai_service.gemini_agent import evaluate_explanation

class MockChunk:
    def __init__(self, content):
        self.choices = [MockChunkChoice(content)]

class MockChunkChoice:
    def __init__(self, content):
        self.delta = MockDelta(content)

class MockDelta:
    def __init__(self, content):
        self.content = content

class MockStreamResponse:
    def __init__(self, content):
        self._content = content
        
    async def __aiter__(self):
        # Yield the content as a single chunk for simplicity in mocking
        yield MockChunk(self._content)

@pytest.mark.asyncio
@patch("app.ai_service.gemini_agent.client.chat.completions.create")
async def test_evaluate_explanation_perfect_score(mock_create):
    mock_json = {
        "score": 10,
        "summary": "Excellent explanation with perfect grammar.",
        "strengths": ["Perfect grammar", "Clear explanation"],
        "weaknesses": [],
        "correct_version": "This is the perfect explanation.",
        "follow_up_question": "What is the next topic?",
        "learning_suggestions": [],
        "feedback_sections": []
    }
    mock_response_content = f"<thinking>Perfect</thinking><json>{json.dumps(mock_json)}</json>"
    mock_create.return_value = MockStreamResponse(mock_response_content)
    
    result = await evaluate_explanation("Test Topic", "Perfect explanation", "fluency")
    assert result["score"] == 10
    assert len(result["weaknesses"]) == 0
    assert result["summary"] == "Excellent explanation with perfect grammar."

@pytest.mark.asyncio
@patch("app.ai_service.gemini_agent.client.chat.completions.create")
async def test_evaluate_explanation_errors_found(mock_create):
    mock_json = {
        "score": 5,
        "summary": "Good effort but has technical flaws.",
        "strengths": ["Good attempt"],
        "weaknesses": ["Missed core concept", "Incorrect terminology"],
        "correct_version": "This is the corrected explanation.",
        "follow_up_question": "Can you explain the core concept?",
        "learning_suggestions": ["Review terminology"],
        "feedback_sections": []
    }
    mock_response_content = f"<thinking>Errors found</thinking><json>{json.dumps(mock_json)}</json>"
    mock_create.return_value = MockStreamResponse(mock_response_content)
    
    result = await evaluate_explanation("Test Topic", "Flawed explanation", "technical")
    assert result["score"] == 5
    assert len(result["weaknesses"]) == 2
    assert "Missed core concept" in result["weaknesses"]
