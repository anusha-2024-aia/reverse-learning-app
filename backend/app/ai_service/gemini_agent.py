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
    You are an expert educational assessment system specializing in '{learning_mode.upper()}'.
    Your goal is to evaluate a student's explanation of a given concept across 8 key dimensions.

    CONTEXTUAL FOCUS: {focus}

    PART 1: THINKING PHASE
    Analyze the explanation silently inside <thinking>...</thinking> tags.

    PART 2: FINAL EVALUATION
    Provide a strict JSON object inside <json>...</json> tags.
    Every score MUST be an integer between 0 and 100.

    The JSON MUST have EXACTLY these fields:
    - "technicalAccuracy": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "conceptUnderstanding": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "completeness": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "examples": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "relevance": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "communication": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "grammar": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "vocabulary": {{"score": 0-100, "feedback": "Short concise feedback..."}}
    - "strengths": ["Specific strength 1", "Specific strength 2"]
    - "weaknesses": ["Specific weakness 1", "Specific weakness 2"]
    - "knowledgeGaps": [
        {{"concept": "Specific Concept Name", "severity": "HIGH", "evidence": "Direct quote or mistake from student answer"}}
      ]
    - "summary": "(2-3 sentence executive summary)"
    - "correct_version": "(Ideal answer, 150-250 words)"
    - "follow_up_question": "(A challenging follow-up question)"
    - "learning_suggestions": ["Actionable step 1", "Actionable step 2"]
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

async def generate_improvement_insight(attempt_history: list) -> str:
    """
    Generates a concise AI insight comparing evaluation attempts over time.
    """
    if not client or not attempt_history or len(attempt_history) < 2:
        return "Keep practicing to generate longitudinal performance trends!"

    formatted_attempts = json.dumps(attempt_history, indent=2)

    system_prompt = """
    You are a learning-progress analyst.
    Analyze the provided student attempt history across dimensions over time.
    
    RULES:
    1. Only use facts present in the data. Do NOT invent improvements.
    2. Be concise (2-3 sentences max).
    3. Identify: biggest improvement area, main remaining weakness, and one actionable tip.
    4. Output plain text ONLY (no Markdown or preamble).
    """

    user_prompt = f"Attempt History:\n{formatted_attempts}"

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in generate_improvement_insight: {e}")
        return "Your explanation shows clear progress across your recent attempts. Focus on edge cases and completeness."

async def generate_ai_roadmap(
    target_role: str,
    current_skills: list,
    experience_level: str,
    career_goal: str,
    hours_per_day: float,
    days_per_week: int,
    preferred_areas: list,
    performance_data: list = None,
    knowledge_gaps: list = None
) -> dict:
    """
    Generates a structured career learning roadmap for a target role using Gemini.
    Validates prerequisites, schema, and detects circular dependencies.
    """
    if not client:
        return get_fallback_roadmap(target_role, experience_level)

    system_prompt = f"""
    You are an expert career learning-path designer.

    Create a practical, sequential, job-ready learning roadmap required to become a:
    Target Role: {target_role}

    USER PROFILE:
    - Current Self-Reported Skills: {json.dumps(current_skills)}
    - Experience Level: {experience_level}
    - Career Goal: {career_goal}
    - Available Study Time: {hours_per_day} hours/day, {days_per_week} days/week
    - Preferred Areas: {json.dumps(preferred_areas)}
    - Demonstrated Performance History: {json.dumps(performance_data or [])}
    - Detected Knowledge Gaps: {json.dumps(knowledge_gaps or [])}

    RULES & INSTRUCTIONS:
    1. Do not include unnecessary or irrelevant technologies. Focus on essential skills needed for {target_role}.
    2. Do not assume a skill is fully mastered simply because the student listed it.
    3. Generate between 8 and 12 logical, progressive topics.
    4. For every topic, specify valid prerequisite topic names (must be exact topic_names of earlier topics in this roadmap).
    5. No circular dependencies in prerequisites!

    FORMATTING REQUIREMENTS:
    Output strictly inside <json>...</json> tags.

    The JSON MUST have this EXACT structure:
    {{
      "topics": [
        {{
          "topic_name": "Exact Name",
          "category": "Frontend / Backend / Database / CS / Soft Skills",
          "description": "Short 1-2 sentence description",
          "importance": "HIGH",
          "difficulty": "BEGINNER",
          "prerequisites": ["Prerequisite Topic 1"],
          "estimated_hours": 15,
          "reason": "Why this topic is needed for the target role",
          "skills_gained": ["Skill 1", "Skill 2"]
        }}
      ]
    }}
    """

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": system_prompt}]
        )
        text = response.choices[0].message.content.strip()

        data = None
        if "<json>" in text:
            start = text.find("<json>") + 6
            end = text.find("</json>", start)
            raw = text[start:end].strip() if end != -1 else text[start:].strip()
            data = json.loads(raw, strict=False)
        else:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(text[start:end+1], strict=False)
            else:
                data = json.loads(text, strict=False)

        topics = data.get("topics", []) if isinstance(data, dict) else []
        validated_topics = validate_and_sanitize_roadmap_topics(topics, target_role)
        return {"status": "success", "topics": validated_topics}

    except Exception as e:
        print(f"Error in generate_ai_roadmap: {e}")
        return get_fallback_roadmap(target_role, experience_level)

def validate_and_sanitize_roadmap_topics(topics: list, target_role: str) -> list:
    """
    Validates topics structure, removes duplicate names, and prevents circular prerequisite dependencies.
    """
    if not isinstance(topics, list) or len(topics) == 0:
        return get_fallback_roadmap(target_role, "BEGINNER")["topics"]

    sanitized = []
    seen_names = set()

    for idx, t in enumerate(topics):
        if not isinstance(t, dict):
            continue
        name = str(t.get("topic_name", f"Topic {idx+1}")).strip()
        if not name or name in seen_names:
            continue
        seen_names.add(name)

        prereqs = t.get("prerequisites", [])
        if not isinstance(prereqs, list):
            prereqs = []
        # Filter prereqs to only include already known previous topic names (prevents forward/circular references)
        valid_prereqs = [p for p in prereqs if p in seen_names and p != name]

        sanitized.append({
            "topic_name": name,
            "category": str(t.get("category", "Engineering")).strip(),
            "description": str(t.get("description", f"Master core concepts of {name}")).strip(),
            "importance": str(t.get("importance", "HIGH")).upper() if str(t.get("importance")).upper() in ["HIGH", "MEDIUM", "LOW"] else "HIGH",
            "difficulty": str(t.get("difficulty", "BEGINNER")).upper() if str(t.get("difficulty")).upper() in ["BEGINNER", "INTERMEDIATE", "ADVANCED"] else "BEGINNER",
            "prerequisites": valid_prereqs,
            "estimated_hours": max(5, min(100, int(t.get("estimated_hours", 15)))),
            "reason": str(t.get("reason", f"Required core skill for {target_role}")).strip(),
            "skills_gained": t.get("skills_gained", [name]) if isinstance(t.get("skills_gained"), list) else [name],
            "order_index": len(sanitized) + 1
        })

    return sanitized if len(sanitized) >= 3 else get_fallback_roadmap(target_role, "BEGINNER")["topics"]

def get_fallback_roadmap(target_role: str, experience_level: str) -> dict:
    """
    Structured fallback roadmap template if AI generation fails or API key is absent.
    """
    role_clean = target_role.lower()
    
    if "full stack" in role_clean or "web" in role_clean:
        topics = [
            {"topic_name": "HTML & Semantic Web", "category": "Frontend", "description": "HTML5 semantic structure and accessibility", "importance": "HIGH", "difficulty": "BEGINNER", "prerequisites": [], "estimated_hours": 10, "reason": "Foundation of web applications", "skills_gained": ["HTML5", "Accessibility"]},
            {"topic_name": "CSS Modern Layouts", "category": "Frontend", "description": "CSS3 Flexbox, Grid, and Responsive Web Design", "importance": "HIGH", "difficulty": "BEGINNER", "prerequisites": ["HTML & Semantic Web"], "estimated_hours": 15, "reason": "Styling responsive UI components", "skills_gained": ["Flexbox", "Grid", "CSS3"]},
            {"topic_name": "JavaScript Fundamentals", "category": "Frontend", "description": "ES6+ syntax, variables, scope, functions, and DOM", "importance": "HIGH", "difficulty": "BEGINNER", "prerequisites": ["HTML & Semantic Web"], "estimated_hours": 20, "reason": "Core programming language for frontend & backend", "skills_gained": ["JavaScript", "DOM", "ES6"]},
            {"topic_name": "Async JavaScript & APIs", "category": "Frontend", "description": "Promises, async/await, Fetch API, and Event Loop", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["JavaScript Fundamentals"], "estimated_hours": 15, "reason": "Handling asynchronous data and server communications", "skills_gained": ["Promises", "Fetch API", "Async/Await"]},
            {"topic_name": "React Fundamentals", "category": "Frontend", "description": "Components, props, state, hooks, and lifecycle", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["Async JavaScript & APIs"], "estimated_hours": 25, "reason": "Modern component-driven UI architecture", "skills_gained": ["React.js", "State Management", "Hooks"]},
            {"topic_name": "Node.js & Express Basics", "category": "Backend", "description": "Server creation, RESTful routing, and middleware", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["JavaScript Fundamentals"], "estimated_hours": 20, "reason": "Backend server API development", "skills_gained": ["Node.js", "Express.js", "REST APIs"]},
            {"topic_name": "SQL & Relational Databases", "category": "Database", "description": "Relational schema design, queries, joins, and indexing", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["Node.js & Express Basics"], "estimated_hours": 18, "reason": "Persistent relational data storage", "skills_gained": ["SQL", "Schema Design", "Queries"]},
            {"topic_name": "Authentication & Security", "category": "Backend", "description": "JWT tokens, password hashing, OAuth, and CORS", "importance": "HIGH", "difficulty": "ADVANCED", "prerequisites": ["Node.js & Express Basics", "SQL & Relational Databases"], "estimated_hours": 15, "reason": "Securing web endpoints and user identity", "skills_gained": ["JWT", "Security", "Auth"]},
            {"topic_name": "System Architecture & Deployment", "category": "DevOps", "description": "CI/CD pipelines, Docker, cloud deployment, and scaling", "importance": "HIGH", "difficulty": "ADVANCED", "prerequisites": ["Authentication & Security"], "estimated_hours": 20, "reason": "Deploying production-ready applications", "skills_gained": ["Docker", "CI/CD", "Cloud Deployment"]}
        ]
    else:
        # Default software engineering fallback
        topics = [
            {"topic_name": "Programming Fundamentals", "category": "CS Core", "description": "Data types, logic, control structures, and recursion", "importance": "HIGH", "difficulty": "BEGINNER", "prerequisites": [], "estimated_hours": 15, "reason": "Foundation of software logic", "skills_gained": ["Logic", "Algorithms"]},
            {"topic_name": "Data Structures & Algorithms", "category": "CS Core", "description": "Arrays, lists, trees, graphs, and Big-O analysis", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["Programming Fundamentals"], "estimated_hours": 25, "reason": "Efficient problem solving and technical interviews", "skills_gained": ["Data Structures", "Algorithms"]},
            {"topic_name": "Database Systems & SQL", "category": "Database", "description": "Relational queries, transactions, and normalization", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["Programming Fundamentals"], "estimated_hours": 20, "reason": "Data persistence and manipulation", "skills_gained": ["SQL", "Database Design"]},
            {"topic_name": "API & Web Services", "category": "Backend", "description": "HTTP protocols, REST API design, and JSON payloads", "importance": "HIGH", "difficulty": "INTERMEDIATE", "prerequisites": ["Programming Fundamentals"], "estimated_hours": 15, "reason": "Inter-system communication and API engineering", "skills_gained": ["REST", "HTTP"]},
            {"topic_name": "System Design Basics", "category": "Architecture", "description": "Scalability, caching, load balancing, and microservices", "importance": "HIGH", "difficulty": "ADVANCED", "prerequisites": ["Database Systems & SQL", "API & Web Services"], "estimated_hours": 20, "reason": "Building scalable software applications", "skills_gained": ["System Design", "Architecture"]}
        ]

    for idx, t in enumerate(topics):
        t["order_index"] = idx + 1

    return {"status": "success", "topics": topics}


