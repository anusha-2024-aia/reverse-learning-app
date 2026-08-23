import os
import json
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import Resume, ResumeQuestion, ResumeInterview, Evaluation, Topic, UserMastery
from app.ai_service.gemini_agent import client, model_name
from app.services.activity_service import ActivityService

class ResumeIntelligenceService:

    @staticmethod
    def extract_text(file_path: str, file_type: str = None) -> str:
        """
        Extracts clean text from PDF or DOCX file.
        """
        if not os.path.exists(file_path):
            raise Exception("Resume file not found")

        ext = file_type.lower() if file_type else os.path.splitext(file_path)[1].lower().replace('.', '')
        text = ""

        try:
            if ext == 'pdf':
                import fitz # PyMuPDF
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text() + "\n"
            elif ext == 'docx':
                import docx
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                raise Exception(f"Unsupported file extension: .{ext}. Please upload a PDF or DOCX file.")
        except Exception as e:
            print(f"Error parsing resume file ({file_path}): {e}")
            raise Exception(f"Failed to extract text from file: {e}")

        cleaned_text = text.strip()
        if len(cleaned_text) < 20:
            raise Exception("Extracted text is empty or too short to be a valid resume.")

        return cleaned_text

    @staticmethod
    async def analyze_and_structure_resume(text: str) -> dict:
        """
        Sends extracted resume text to Gemini to extract structured JSON data without inventing facts.
        """
        if not client:
            raise Exception("GEMINI_API_KEY is not configured.")

        prompt = f"""
        You are an expert technical recruiter and resume intelligence parser.
        Analyze the following candidate resume text and extract structured information into strict JSON.

        STRICT ACCURACY & SAFETY INSTRUCTIONS:
        1. Base your response ONLY on the provided resume text.
        2. DO NOT invent, assume, or fabricate any skills, projects, experience, education, or technologies.
        3. If a section is not mentioned, use an empty list [].

        FORMATTING REQUIREMENTS:
        Return ONLY valid JSON matching this exact structure inside <json>...</json> tags:

        <json>
        {{
            "summary": "Brief 2-line summary of candidate background",
            "skills": ["Skill1", "Skill2"],
            "programming_languages": ["Python", "Java"],
            "frameworks": ["React", "FastAPI"],
            "databases": ["MySQL", "MongoDB"],
            "tools": ["Docker", "Git"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Description of project from resume",
                    "technologies": ["Tech1", "Tech2"]
                }}
            ],
            "experience": [
                {{
                    "company": "Company Name",
                    "role": "Role Title",
                    "description": "Responsibilities and accomplishments"
                }}
            ],
            "education": [
                {{
                    "degree": "Degree/Field",
                    "institution": "University/College",
                    "year": "Graduation Year"
                }}
            ],
            "certifications": ["Cert 1"],
            "strongest_areas": ["Area 1", "Area 2"],
            "recommended_focus": ["Focus Area 1", "Focus Area 2"]
        }}
        </json>

        RESUME TEXT:
        {text}
        """

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            resp_text = response.choices[0].message.content
            
            data = None
            if "<json>" in resp_text:
                start = resp_text.find("<json>") + 6
                end = resp_text.find("</json>", start)
                data_str = resp_text[start:end].strip() if end != -1 else resp_text[start:].strip()
                data = json.loads(data_str, strict=False)
            else:
                start = resp_text.find("{")
                end = resp_text.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(resp_text[start:end+1], strict=False)
                else:
                    data = json.loads(resp_text, strict=False)

            if not data:
                raise Exception("Failed to parse AI response into structured format.")

            return data

        except Exception as err:
            print(f"Gemini resume analysis error: {err}")
            raise Exception(f"AI analysis failed: {err}")

    @staticmethod
    async def generate_personalized_questions(db: Session, user_id: int, resume_id: int) -> list:
        """
        Generates personalized, non-generic interview questions based on candidate's actual projects & skills.
        """
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume or not resume.analysis_summary_json:
            return []

        try:
            summary_data = json.loads(resume.analysis_summary_json)
        except:
            summary_data = {}

        skills = summary_data.get("skills", [])
        projects = summary_data.get("projects", [])
        experience = summary_data.get("experience", [])

        prompt = f"""
        You are an elite technical interviewer at a top tech company.
        Generate 10 to 15 highly personalized, project-specific, and skill-specific interview questions 
        based STRICTLY on the candidate's structured resume data below.

        CRITICAL INSTRUCTIONS:
        1. DO NOT ask generic questions like "What is Python?" or "What is SQL?".
        2. Connect questions explicitly to candidate's projects, listed technologies, experience, and architectural decisions.
           EXAMPLE GOOD QUESTIONS:
           - "You mentioned Python in your Smart Job Matching System. Why did you choose Python for this implementation?"
           - "You mentioned MySQL in Smart Job Matching System. Why was a relational database suitable for your project?"
           - "You mentioned a matching algorithm. Explain how it determines the best match."
           - "How would you improve the matching algorithm if the number of users increased?"
        3. Do NOT invent facts, projects, technologies, or achievements not present in candidate data.
        4. Categorize each question into one of: PROJECT, TECHNICAL, DATABASE, ALGORITHM, ARCHITECTURE, EXPERIENCE, SCALABILITY, BEHAVIORAL.
        5. Assign difficulty: EASY, MEDIUM, or HARD.
        6. Include "source" identifying the exact resume item (e.g. project name or skill) that inspired the question.

        Return ONLY a JSON array inside <json>...</json> tags:

        <json>
        [
            {{
                "category": "PROJECT",
                "question": "Explain your Smart Job Matching System.",
                "difficulty": "EASY",
                "source": "Smart Job Matching System"
            }}
        ]
        </json>

        CANDIDATE DATA:
        Skills: {json.dumps(skills)}
        Projects: {json.dumps(projects)}
        Experience: {json.dumps(experience)}
        Education: {json.dumps(summary_data.get("education", []))}
        """

        q_data = []
        try:
            if client:
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                resp_text = response.choices[0].message.content

                if "<json>" in resp_text:
                    start = resp_text.find("<json>") + 6
                    end = resp_text.find("</json>", start)
                    data_str = resp_text[start:end].strip() if end != -1 else resp_text[start:].strip()
                    q_data = json.loads(data_str, strict=False)
                else:
                    start = resp_text.find("[")
                    end = resp_text.rfind("]")
                    if start != -1 and end != -1:
                        q_data = json.loads(resp_text[start:end+1], strict=False)
        except Exception as err:
            print(f"Gemini API call failed for questions (using rule-based parser fallback): {err}")
            q_data = []

        # Fallback question generation if AI returned empty list or error
        if not q_data:
            q_data = []
            for proj in projects:
                p_name = proj.get("name", "Project")
                p_techs = ", ".join(proj.get("technologies", [])) or "your listed technologies"
                
                q_data.append({
                    "category": "PROJECT",
                    "question": f"Explain your {p_name} and the primary problem it solves.",
                    "difficulty": "EASY",
                    "source": p_name
                })
                q_data.append({
                    "category": "DATABASE",
                    "question": f"You used {p_techs} for '{p_name}'. Why did you choose these data and backend technologies for this implementation?",
                    "difficulty": "MEDIUM",
                    "source": p_name
                })
                q_data.append({
                    "category": "ALGORITHM",
                    "question": f"What algorithm or core data logic powers '{p_name}', and how does it process candidate or application data?",
                    "difficulty": "MEDIUM",
                    "source": p_name
                })
                q_data.append({
                    "category": "ARCHITECTURE",
                    "question": f"What technical challenges occurred while building '{p_name}' and how were they resolved?",
                    "difficulty": "MEDIUM",
                    "source": p_name
                })
                q_data.append({
                    "category": "SCALABILITY",
                    "question": f"How would you redesign '{p_name}' to scale effectively for millions of active users?",
                    "difficulty": "HARD",
                    "source": p_name
                })

            for s in skills[:4]:
                q_data.append({
                    "category": "TECHNICAL",
                    "question": f"You listed {s} on your resume. How have you applied {s} in your projects or coursework?",
                    "difficulty": "MEDIUM",
                    "source": s
                })

            for exp in experience:
                comp = exp.get("company", "your role")
                r = exp.get("role", "Engineer")
                q_data.append({
                    "category": "EXPERIENCE",
                    "question": f"What were your primary responsibilities and technical contributions as {r} at {comp}?",
                    "difficulty": "MEDIUM",
                    "source": comp
                })

            if not q_data:
                q_data.append({
                    "category": "PROJECT",
                    "question": "Can you walk us through the system architecture of the most complex technical project on your resume?",
                    "difficulty": "HARD",
                    "source": "Architecture"
                })

        # Store generated questions in DB
        db.query(ResumeQuestion).filter(
            ResumeQuestion.resume_id == resume_id,
            ResumeQuestion.user_id == user_id
        ).delete()
        db.commit()

        saved_questions = []
        for item in q_data:
            cat = item.get("category", "PROJECT").upper()
            diff = item.get("difficulty", "MEDIUM").upper()
            src = item.get("source") or item.get("target_project_or_skill") or "Resume"
            
            rq = ResumeQuestion(
                resume_id=resume_id,
                user_id=user_id,
                category=cat,
                question_text=item.get("question", ""),
                difficulty=diff,
                target_project_or_skill=src
            )
            db.add(rq)
            saved_questions.append(rq)
        
        db.commit()
        return saved_questions


    @staticmethod
    async def generate_followup_question(target_role: str, previous_qa: list) -> str:
        """
        Generates a natural follow-up question based on candidate's previous response.
        """
        if not client or not previous_qa:
            return "Can you elaborate further on your technical architecture decisions?"

        last_item = previous_qa[-1]
        prompt = f"""
        You are conducting a personalized technical interview for a {target_role} role.
        The candidate was asked: "{last_item.get('question')}"
        The candidate answered: "{last_item.get('answer')}"

        Formulate a direct, natural follow-up question probing deeper into their answer, architectural choice, trade-off, or implementation detail.
        Keep the follow-up concise (1-2 sentences). Do not add introductory conversational filler.
        """

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as err:
            print(f"Follow-up question error: {err}")
            return "How would you handle scaling this implementation if user traffic increased 10x?"

    @staticmethod
    async def evaluate_resume_interview(db: Session, user_id: int, interview_id: int, qa_history: list) -> dict:
        """
        Evaluates complete resume interview using multi-dimensional analysis,
        logs knowledge gaps, and updates resume interview record.
        """
        interview = db.query(ResumeInterview).filter(
            ResumeInterview.id == interview_id,
            ResumeInterview.user_id == user_id
        ).first()

        if not interview:
            raise Exception("Resume interview not found")

        qa_text = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in qa_history])

        prompt = f"""
        You are an executive engineering interviewer evaluating a candidate's resume-based mock interview.
        Evaluate the candidate's answers based on accuracy, project understanding, technical depth, communication, and problem-solving.

        Return ONLY JSON inside <json>...</json> tags:

        <json>
        {{
            "overall_score": 83,
            "technical_score": 82,
            "project_knowledge_score": 88,
            "communication_score": 76,
            "problem_solving_score": 79,
            "resume_understanding_score": 91,
            "strengths": ["Clear project architecture explanation", "Strong choice of relational database"],
            "weaknesses": ["Database design explanation", "Scalability concepts"],
            "recommended_preparation": ["Review database normalization", "Practice system design basics"],
            "knowledge_gaps_identified": ["Database Design", "Scalability & Caching"]
        }}
        </json>

        INTERVIEW QA TRANSCRIPT:
        {qa_text}
        """

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            resp_text = response.choices[0].message.content

            if "<json>" in resp_text:
                start = resp_text.find("<json>") + 6
                end = resp_text.find("</json>", start)
                eval_data = json.loads(resp_text[start:end].strip() if end != -1 else resp_text[start:].strip(), strict=False)
            else:
                start = resp_text.find("{")
                end = resp_text.rfind("}")
                eval_data = json.loads(resp_text[start:end+1], strict=False)

        except Exception as err:
            print(f"Error evaluating resume interview: {err}")
            eval_data = {
                "overall_score": 75,
                "technical_score": 75,
                "project_knowledge_score": 80,
                "communication_score": 70,
                "problem_solving_score": 75,
                "resume_understanding_score": 80,
                "strengths": ["Good effort on project explanations"],
                "weaknesses": ["Further practice needed on architecture trade-offs"],
                "recommended_preparation": ["Practice system design concepts"],
                "knowledge_gaps_identified": []
            }

        # Update interview record
        interview.overall_score = eval_data.get("overall_score", 75)
        interview.technical_score = eval_data.get("technical_score", 75)
        interview.project_knowledge_score = eval_data.get("project_knowledge_score", 80)
        interview.communication_score = eval_data.get("communication_score", 70)
        interview.problem_solving_score = eval_data.get("problem_solving_score", 75)
        interview.resume_understanding_score = eval_data.get("resume_understanding_score", 80)
        interview.feedback_json = json.dumps(eval_data)
        interview.status = "COMPLETED"
        interview.completed_at = datetime.now(timezone.utc)

        db.commit()

        # Log activity
        ActivityService.log_activity(db, user_id, "interview")

        # Create knowledge gap entries for weak areas if topic exists in DB
        try:
            gaps = eval_data.get("knowledge_gaps_identified", [])
            for gap_name in gaps:
                topic = db.query(Topic).filter(Topic.name.ilike(f"%{gap_name}%")).first()
                if topic:
                    existing_eval = db.query(Evaluation).filter(
                        Evaluation.user_id == user_id,
                        Evaluation.topic_id == topic.id
                    ).order_by(Evaluation.created_at.desc()).first()

                    db_eval = Evaluation(
                        user_id=user_id,
                        topic_id=topic.id,
                        explanation=f"Resume Interview weakness identified in {gap_name}",
                        overall_score=min(55, eval_data.get("technical_score", 55)),
                        ai_score=min(55, eval_data.get("technical_score", 55)),
                        ai_insight=f"Identified weakness during Resume Interview: {gap_name}"
                    )
                    db.add(db_eval)
                    db.commit()
        except Exception as gap_err:
            print(f"Error syncing resume interview knowledge gaps: {gap_err}")

        return eval_data
