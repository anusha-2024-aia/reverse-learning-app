import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Using the specific 'gemini-2.5-flash' model requested by the user.
model_name = "gemini-2.5-flash" 
model = genai.GenerativeModel(model_name)

async def stream_evaluate_explanation(topic: str, user_explanation: str, learning_mode: str = "general"):
    """
    Evaluates the user's explanation using Gemini in a streaming fashion.
    Incorporates the learning_mode to tune the evaluation style.
    """
    
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

    Topic: {topic}
    Student's Explanation: {user_explanation}
    
    PART 1: THINKING PHASE
    Analyze the explanation silently. Identify factual errors, missing key concepts, and logical gaps.
    Always check grammar regardless of mode. For technical mode, pay special attention to core technicals and logic.
    
    PART 2: FINAL EVALUATION
    Provide a final score and a highly structured pedagogical evaluation.
    
    FORMATTING RULES:
    1. Start your response with <thinking> followed by your reasoning.
    2. End the thinking section with </thinking>.
    3. Then, provide the final evaluation strictly as a JSON object inside <json>...</json> tags.
    
    The JSON must have EXACTLY these fields:
    - "score": (integer out of 10)
    - "summary": (A brief, encouraging summary of overall progress and performance.)
    - "grammar_issues": (A list of specific string messages about grammar/clarity errors and their corrections. E.g., ["Use 'an' instead of 'a' before Apple."])
    - "vocabulary_suggestions": (A list of 3-5 important string keywords to memorize or use better.)
    - "advanced_version": (A more advanced, professional-level script of the explanation for the student to memorize.)
    - "missing_concepts": (A list of specific technical or conceptual points the student missed.)
    - "follow_up_question": (A challenging question that pushes the student to think deeper.)

    Example:
    <thinking>
    Analysis...
    </thinking>
    <json>
    {{
      "score": 4,
      "summary": "...",
      "grammar_issues": ["..."],
      "vocabulary_suggestions": ["..."],
      "advanced_version": "...",
      "missing_concepts": ["..."],
      "follow_up_question": "..."
    }}
    </json>
    """

    try:
        async_response = await model.generate_content_async(system_prompt, stream=True)
        
        async for chunk in async_response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        print(f"Error in stream_evaluate_explanation: {e}")
        yield f"<thinking>Error occurred: {str(e)}</thinking>"
        yield '<json>{"score": 0, "missing_concepts": ["System Error"], "feedback": "An error occurred while processing."}</json>'

async def evaluate_explanation(topic: str, user_explanation: str, learning_mode: str = "general"):
    """
    Legacy non-streaming version (kept for compatibility, but updated to use the new protocol).
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
            return json.loads(json_str)
        
        start_index = full_text.find("{")
        end_index = full_text.rfind("}")
        if start_index != -1 and end_index != -1:
            json_str = full_text[start_index:end_index+1]
            return json.loads(json_str)
            
        return json.loads(full_text)
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
        response = await model.generate_content_async(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_interview_question: {e}")
        return "I encountered an error generating the next question. Please tell me more about your notes."

async def evaluate_interview_performance(notes: str, interview_transcript: list) -> dict:
    """
    Evaluates the entire interview transcript against the notes.
    """
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
        response = await model.generate_content_async(system_prompt)
        text = response.text
        
        if "<json>" in text:
            start = text.find("<json>") + 6
            end = text.find("</json>", start)
            if end != -1:
                return json.loads(text[start:end].strip())
        
        # Fallback parsing
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
            
        return json.loads(text)
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
