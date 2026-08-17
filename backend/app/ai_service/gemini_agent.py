import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini using OpenAI SDK
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables. AI features will not work.")
    client = None
else:
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

model_name = "gemini-2.5-flash"

async def stream_evaluate_explanation(topic: str, user_explanation: str, learning_mode: str = "general"):
    """
    Evaluates the user's explanation using Grok in a streaming fashion.
    Incorporates the learning_mode to tune the evaluation style.
    """
    if not client:
        yield "<thinking>Error occurred: GEMINI_API_KEY is not configured</thinking>"
        yield '<json>{"score": 0, "missing_concepts": ["System Error"], "feedback": "GEMINI_API_KEY is missing."}</json>'
        return
    
    # Mode-specific focus instructions
    mode_instructions = {
        "technical": "Focus heavily on algorithmic logic, data structures, and Time/Space complexity analysis.",
        "fluency": "Focus on grammatical precision, advanced vocabulary usage, professional tone, and pronunciation nuances.",
        "general": "Focus on high-level conceptual clarity, effective analogies, and overall intuition."
    }
    
    focus = mode_instructions.get(learning_mode, mode_instructions["general"])

    system_prompt = f"""
    You are a strict but encouraging teacher specialized in '{learning_mode.upper()}'. 
    Your goal is to evaluate a student's explanation of a specific topic to gauge their comprehension.
    
    CONTEXTUAL FOCUS: {focus}
    You must strictly check grammar, core technicals, and overall clarity. It must perfectly work out.

    PART 1: THINKING PHASE
    Analyze the explanation silently. Identify factual errors, missing key concepts, and logical gaps.
    Always check grammar regardless of mode. For technical mode, pay special attention to core technicals and logic.
    
    PART 2: FINAL EVALUATION
    Evaluate and provide structured JSON ONLY.
    
    FORMATTING RULES:
    1. Start your response with <thinking> followed by your reasoning.
    2. End the thinking section with </thinking>.
    3. Then, provide the final evaluation strictly as a JSON object inside <json>...</json> tags.
    
    The JSON must have EXACTLY these fields:
    - "score": (1-10 integer)
    - "summary": "(2-3 sentences: praise + 1 area to improve)"
    - "strengths": ["strength1", "strength2", "strength3"]
    - "weaknesses": ["weakness1", "weakness2"]
    - "correct_version": "(Ideal answer 200-300 words)"
    - "follow_up_question": "(A deeper question to challenge student)"
    - "learning_suggestions": ["Topic/Skill 1", "Practice Exercise 2", "Advanced Concept 3"]
    - "communication_score": (1-100 integer)
    - "speaking_pace_score": (1-100 integer)
    - "clarity_score": (1-100 integer)
    - "grammar_score": (1-100 integer)
    - "vocabulary_score": (1-100 integer)
    - "filler_words": (integer, count of filler words like um, ah, like)
    - "feedback_sections": [
        {{
            "title": "TECHNICAL EVALUATION",
            "icon": "code",
            "content": "(Technical assessment 100 words)"
        }},
        {{
            "title": "COMMUNICATION CLARITY",
            "icon": "message-circle",
            "content": "(How well explained 100 words)"
        }},
        {{
            "title": "COMPLETENESS",
            "icon": "check-circle",
            "content": "(Coverage assessment 100 words)"
        }}
    ]
    """

    user_prompt = f"Topic: {topic}\nStudent's Explanation: {user_explanation}"

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"Error in stream_evaluate_explanation: {e}")
        err_str = str(e)
        if "permission-denied" in err_str or "403" in err_str or "credits" in err_str.lower():
            user_msg = "Your Google account has an issue with credits or permissions. Please check Google AI Studio."
        elif "Model not found" in err_str or "400" in err_str:
            user_msg = "The AI model was not found. Please check the model name in the backend configuration."
        elif "401" in err_str or "Unauthorized" in err_str:
            user_msg = "Invalid GEMINI_API_KEY. Please check your .env file."
        else:
            user_msg = f"AI evaluation error: {err_str}"
        yield f"<thinking>Error occurred: {err_str}</thinking>"
        yield f'<json>{{"score": 0, "summary": "{user_msg}", "strengths": [], "weaknesses": ["System Error"], "correct_version": "N/A", "follow_up_question": "N/A", "learning_suggestions": [], "communication_score": 0, "speaking_pace_score": 0, "clarity_score": 0, "grammar_score": 0, "vocabulary_score": 0, "filler_words": 0, "feedback_sections": []}}</json>'

async def evaluate_explanation(topic: str, user_explanation: str, learning_mode: str = "general"):
    """
    Legacy non-streaming version (kept for compatibility).
    """
    full_text = ""
    async for chunk in stream_evaluate_explanation(topic, user_explanation, learning_mode):
        full_text += chunk
    
    try:
        if "<json>" in full_text:
            start_index = full_text.find("<json>") + 6
            end_index = full_text.find("</json>", start_index)
            if end_index != -1:
                json_str = full_text[start_index:end_index].strip()
            else:
                json_str = full_text[start_index:].strip()
            return json.loads(json_str, strict=False)
        
        start_index = full_text.find("{")
        end_index = full_text.rfind("}")
        if start_index != -1 and end_index != -1:
            json_str = full_text[start_index:end_index+1]
            return json.loads(json_str, strict=False)
            
        return json.loads(full_text, strict=False)
    except Exception as e:
        print(f"Parsing error: {e}")
        return {
            "score": 0,
            "missing_concepts": ["Parsing Error"],
            "feedback": f"Failed to parse AI response. Error: {str(e)}"
        }

async def generate_interview_question(notes: str, previous_qa: list) -> str:
    """
    Generates the next interview question based on the user's notes and previous Q&A.
    """
    if not client:
        return "I encountered an error generating the next question because GEMINI_API_KEY is missing."

    history = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in previous_qa])
    
    system_prompt = f"""
    You are an expert technical interviewer and tutor conducting a mock interview.
    
    The user provided the following notes to study from:
    {notes}
    
    Here is the interview history so far:
    {history}
    
    Your task:
    Generate ONE relevant, challenging, and conversational follow-up question based on the notes and the user's previous answers (if any).
    If this is the first question, ask them to explain a core concept from the notes.
    If they answered a previous question, ask a follow-up or move to the next concept.
    
    Do NOT provide any preamble or formatting. Output ONLY the question text.
    """
    
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": system_prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in generate_interview_question: {e}")
        return "I encountered an error generating the next question. Please tell me more about your notes."

async def evaluate_interview_performance(notes: str, interview_transcript: list) -> dict:
    """
    Evaluates the entire interview transcript against the notes.
    """
    if not client:
        return {
            "overall_score": 0,
            "confidence_score": 0,
            "grammar_score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "summary": "GEMINI_API_KEY is missing.",
            "technical_feedback": "N/A",
            "filler_words_used": "N/A",
            "grammar_issues": [],
            "strengths": [],
            "areas_for_improvement": []
        }

    history = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in interview_transcript])
    
    system_prompt = f"""
    You are an expert technical interviewer evaluating a candidate's mock interview.
    
    The candidate provided these study notes:
    {notes}
    
    Here is the transcript of the interview:
    {history}
    
    Your task:
    Provide a comprehensive final evaluation of the candidate's performance. Focus on four key areas:
    1. Technical accuracy (compared to their notes)
    2. Grammatical fluency
    3. Communication flow
    4. Speaking confidence (look for hesitation, repetition, and filler words like "um", "uh", "like" in the transcript)
    
    FORMATTING RULES:
    Output your response strictly as a JSON object inside <json>...</json> tags.
    
    The JSON must have EXACTLY these fields:
    - "overall_score": (integer out of 10, average of the other 4 scores)
    - "confidence_score": (integer out of 10)
    - "grammar_score": (integer out of 10)
    - "technical_score": (integer out of 10)
    - "communication_score": (integer out of 10)
    - "summary": (A brief, encouraging summary of their overall performance)
    - "technical_feedback": (A paragraph evaluating their technical understanding of the notes)
    - "filler_words_used": (A string noting detected hesitations and conversational crutches. If none, say so.)
    - "grammar_issues": (A list of specific string messages about grammar/clarity errors they made)
    - "strengths": (A list of 2-3 things they did well)
    - "areas_for_improvement": (A list of 2-3 specific technical or communication areas to improve)
    """
    
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": system_prompt}]
        )
        text = response.choices[0].message.content
        
        if "<json>" in text:
            start = text.find("<json>") + 6
            end = text.find("</json>", start)
            if end != -1:
                return json.loads(text[start:end].strip(), strict=False)
        
        # Fallback parsing
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1], strict=False)
            
        return json.loads(text, strict=False)
    except Exception as e:
        print(f"Error in evaluate_interview_performance: {e}")
        return {
            "overall_score": 0,
            "confidence_score": 0,
            "grammar_score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "summary": "An error occurred during evaluation.",
            "technical_feedback": "N/A",
            "filler_words_used": "N/A",
            "grammar_issues": [],
            "strengths": [],
            "areas_for_improvement": []
        }
