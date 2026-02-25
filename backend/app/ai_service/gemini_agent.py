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

    Topic: {topic}
    Student's Explanation: {user_explanation}
    
    PART 1: THINKING PHASE
    Analyze the explanation silently. Identify factual errors, missing key concepts, and logical gaps.
    For technical mode, pay special attention to Big O notation. For fluency, look for idiomatic expressions.
    
    PART 2: FINAL EVALUATION
    Provide a final score and a highly structured pedagogical evaluation.
    
    FORMATTING RULES:
    1. Start your response with <thinking> followed by your reasoning.
    2. End the thinking section with </thinking>.
    3. Then, provide the final evaluation strictly as a JSON object inside <json>...</json> tags.
    
    The JSON must have:
    - "score": (integer out of 10)
    - "grammatical_fixes": (Detailed analysis of errors with their CORRECTED forms. Be specific.)
    - "advanced_version": (A more advanced, professional-level script of the explanation for the student to memorize.)
    - "key_vocabulary": (A list of 3-5 important keywords or phrases to memorize for this topic.)
    - "feedback": (A brief, encouraging summary of overall progress.)
    - "missing_concepts": (A list of specific technical or conceptual points the student missed.)
    - "follow_up_question": (A challenging question that pushes the student to think deeper or apply the concept in a more complex scenario.)

    Example:
    <thinking>
    Analysis of the student's input...
    </thinking>
    <json>
    {{
      "score": 4,
      "grammatical_fixes": "...",
      "advanced_version": "...",
      "key_vocabulary": [],
      "feedback": "...",
      "missing_concepts": [],
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
