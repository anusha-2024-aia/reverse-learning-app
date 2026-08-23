import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app import models
from app.ai_service.gemini_agent import client, model_name
from app.services.activity_service import ActivityService

WEAK_THRESHOLD = 60
STRONG_THRESHOLD = 80

DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]

class AdaptiveInterviewService:

    @staticmethod
    def calculate_next_difficulty(current_difficulty: str, score: int) -> str:
        """
        Deterministic difficulty state machine:
        - Score < 60: Decrease difficulty by one level (HARD -> MEDIUM -> EASY).
        - 60 <= Score < 80: Maintain current difficulty.
        - Score >= 80: Increase difficulty by one level (EASY -> MEDIUM -> HARD).
        """
        curr = (current_difficulty or "MEDIUM").upper()
        if curr not in DIFFICULTY_LEVELS:
            curr = "MEDIUM"

        idx = DIFFICULTY_LEVELS.index(curr)

        if score < WEAK_THRESHOLD:
            new_idx = max(0, idx - 1)
        elif score >= STRONG_THRESHOLD:
            new_idx = min(len(DIFFICULTY_LEVELS) - 1, idx + 1)
        else:
            new_idx = idx

        return DIFFICULTY_LEVELS[new_idx]

    @staticmethod
    async def evaluate_single_answer(topic: str, question: str, answer: str) -> dict:
        """
        Evaluates a single student answer using Multi-Dimensional criteria.
        Returns technical, communication, completeness, relevance, and overall scores.
        """
        if not client:
            # Rule-based fallback evaluation based on content length and key indicators
            clean_ans = answer.strip()
            word_count = len(clean_ans.split())
            
            if word_count < 8:
                tech = 45
                comm = 50
                comp = 40
                rel = 55
            elif word_count < 25:
                tech = 65
                comm = 70
                comp = 60
                rel = 75
            else:
                tech = 85
                comm = 85
                comp = 80
                rel = 90
            
            overall = round((tech * 0.4) + (comm * 0.2) + (comp * 0.2) + (rel * 0.2))
            return {
                "technical_score": tech,
                "communication_score": comm,
                "completeness_score": comp,
                "relevance_score": rel,
                "overall_score": overall,
                "feedback": f"Your response is {'concise' if word_count < 20 else 'detailed'}. Focus on expanding technical architecture choices."
            }

        prompt = f"""
        You are an executive engineering interviewer evaluating a single answer in an adaptive mock interview.

        QUESTION ASKED: "{question}"
        TOPIC AREA: "{topic}"
        STUDENT ANSWER: "{answer}"

        Evaluate the response across 4 core dimensions on a scale of 0 to 100:
        1. technical_score: Accuracy of technical concepts, algorithms, frameworks, and system logic.
        2. communication_score: Clarity, structure, tone, and professional expression.
        3. completeness_score: Thoroughness in addressing all parts of the question.
        4. relevance_score: Direct adherence to what was asked without unnecessary filler.

        Calculate overall_score as the weighted average: (technical*0.4 + completeness*0.2 + relevance*0.2 + communication*0.2).

        Return ONLY a valid JSON object inside <json>...</json> tags:

        <json>
        {{
            "technical_score": 82,
            "communication_score": 78,
            "completeness_score": 80,
            "relevance_score": 85,
            "overall_score": 82,
            "feedback": "Strong technical explanation of API state management, but could elaborate on caching."
        }}
        </json>
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
                data_str = resp_text[start:end].strip() if end != -1 else resp_text[start:].strip()
                eval_data = json.loads(data_str, strict=False)
            else:
                start = resp_text.find("{")
                end = resp_text.rfind("}")
                eval_data = json.loads(resp_text[start:end+1], strict=False)

            tech = int(eval_data.get("technical_score", 70))
            comm = int(eval_data.get("communication_score", 70))
            comp = int(eval_data.get("completeness_score", 70))
            rel = int(eval_data.get("relevance_score", 70))
            overall = int(eval_data.get("overall_score", round((tech * 0.4) + (comm * 0.2) + (comp * 0.2) + (rel * 0.2))))

            return {
                "technical_score": min(100, max(0, tech)),
                "communication_score": min(100, max(0, comm)),
                "completeness_score": min(100, max(0, comp)),
                "relevance_score": min(100, max(0, rel)),
                "overall_score": min(100, max(0, overall)),
                "feedback": eval_data.get("feedback", "Good effort on your response.")
            }
        except Exception as err:
            print(f"Gemini single answer evaluation error: {err}")
            word_count = len(answer.strip().split())
            if word_count < 10:
                score = 48
            elif word_count < 25:
                score = 72
            else:
                score = 85

            return {
                "technical_score": score,
                "communication_score": score,
                "completeness_score": score,
                "relevance_score": score,
                "overall_score": score,
                "feedback": "Answer recorded successfully."
            }

    @staticmethod
    async def generate_adaptive_question(
        db: Session,
        user_id: int,
        interview: models.Interview,
        last_qa: dict = None
    ) -> dict:
        """
        Generates the next question using Gemini AI, adapting to target role, difficulty, previous answer,
        topic, and resume context. Prevents question repetition.
        """
        already_asked = [
            q.question_text for q in db.query(models.InterviewQuestion).filter(
                models.InterviewQuestion.interview_id == interview.id
            ).all()
        ]

        resume_skills = []
        resume_projects = []
        if interview.resume_id:
            resume = db.query(models.Resume).filter(
                models.Resume.id == interview.resume_id,
                models.Resume.user_id == user_id
            ).first()
            if resume:
                try:
                    resume_skills = json.loads(resume.parsed_skills or "[]")
                    resume_projects = json.loads(resume.parsed_projects or "[]")
                except:
                    pass

        target_role = interview.target_role or "Software Engineer"
        interview_type = interview.interview_type or "technical"
        current_diff = (interview.current_difficulty or "MEDIUM").upper()

        last_question_text = last_qa.get("question", "") if last_qa else ""
        last_answer_text = last_qa.get("answer", "") if last_qa else ""
        last_score = last_qa.get("score", 70) if last_qa else 70

        prompt = f"""
        You are an elite technical interviewer conducting an ADAPTIVE mock interview.

        CANDIDATE & SESSION CONTEXT:
        - Target Role: {target_role}
        - Interview Type: {interview_type}
        - Current Target Difficulty: {current_diff}
        - Resume Skills: {json.dumps(resume_skills)}
        - Resume Projects: {json.dumps(resume_projects)}
        - Already Asked Questions (DO NOT REPEAT ANY): {json.dumps(already_asked)}

        PREVIOUS STEP PERFORMANCE:
        - Previous Question: "{last_question_text}"
        - Student Answer: "{last_answer_text}"
        - Performance Score: {last_score}%

        ADAPTATION INSTRUCTIONS:
        1. If the previous score was WEAK (<60), ask an easier clarification or core concept question probing their weak response.
        2. If the previous score was STRONG (>=80), ask a more challenging technical, architectural, or scalability question.
        3. If no previous question exists (first question), ask a foundational question matching the target role and starting difficulty.
        4. Maintain topic continuity where natural before switching focus areas.
        5. DO NOT generate generic questions like "What is Python?". Connect questions to projects, decisions, trade-offs, and target role responsibilities.

        Return ONLY a JSON object inside <json>...</json> tags:

        <json>
        {{
            "question": "Specific question text...",
            "category": "PROJECT",
            "difficulty": "{current_diff}",
            "topic": "System Design",
            "is_followup": true,
            "source": "Smart Job Matching System",
            "reason": "Probing deeper into scalability after candidate gave a strong answer."
        }}
        </json>
        """

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
                    start = resp_text.find("{")
                    end = resp_text.rfind("}")
                    q_data = json.loads(resp_text[start:end+1], strict=False)

                q_text = q_data.get("question", "").strip()
                if q_text and q_text not in already_asked:
                    return {
                        "question": q_text,
                        "category": q_data.get("category", "TECHNICAL").upper(),
                        "difficulty": current_diff,
                        "topic": q_data.get("topic", target_role),
                        "is_followup": bool(q_data.get("is_followup", bool(last_qa))),
                        "source": q_data.get("source", "Interview Context")
                    }
        except Exception as err:
            print(f"Gemini adaptive question generation error: {err}")

        # Fallback Question Pool if AI is offline or repeated question generated
        return AdaptiveInterviewService._generate_fallback_question(
            target_role=target_role,
            interview_type=interview_type,
            difficulty=current_diff,
            already_asked=already_asked,
            resume_projects=resume_projects,
            resume_skills=resume_skills,
            last_score=last_score
        )

    @staticmethod
    def _generate_fallback_question(
        target_role: str,
        interview_type: str,
        difficulty: str,
        already_asked: list,
        resume_projects: list,
        resume_skills: list,
        last_score: int
    ) -> dict:
        """
        Rule-based question generator ensuring non-repetitive adaptive questions.
        """
        pool = []

        # Project / Resume questions
        for p in resume_projects:
            p_name = p.get("name", "Project")
            p_techs = ", ".join(p.get("technologies", [])) or "your technologies"
            
            if difficulty == "EASY":
                pool.append({
                    "question": f"Can you describe the primary goal of '{p_name}' and what role you played in developing it?",
                    "category": "PROJECT",
                    "topic": "Project Overview",
                    "source": p_name
                })
            elif difficulty == "HARD":
                pool.append({
                    "question": f"How would you re-architect '{p_name}' to handle 100k requests per second using microservices and Redis caching?",
                    "category": "SCALABILITY",
                    "topic": "System Architecture",
                    "source": p_name
                })
            else:
                pool.append({
                    "question": f"You built '{p_name}' using {p_techs}. What were the key architectural trade-offs you faced?",
                    "category": "ARCHITECTURE",
                    "topic": "Technical Trade-offs",
                    "source": p_name
                })

        # Technical / Skill questions
        for s in resume_skills[:4]:
            if difficulty == "HARD":
                pool.append({
                    "question": f"How do you handle memory management, concurrency, and performance profiling in {s}?",
                    "category": "TECHNICAL",
                    "topic": f"{s} Advanced",
                    "source": s
                })
            else:
                pool.append({
                    "question": f"How have you structured error handling and asynchronous operations in your {s} applications?",
                    "category": "TECHNICAL",
                    "topic": f"{s} Design",
                    "source": s
                })

        # Role-based questions
        role_questions = [
            {"q": f"How do you design secure RESTful APIs for {target_role} production applications?", "cat": "DATABASE", "top": "API Design", "diff": "MEDIUM"},
            {"q": f"When building applications as a {target_role}, how do you ensure high availability and database consistency?", "cat": "ARCHITECTURE", "top": "Database Consistency", "diff": "HARD"},
            {"q": f"Explain the HTTP request-response cycle and how data flows from frontend client to database in your projects.", "cat": "TECHNICAL", "top": "Web Fundamentals", "diff": "EASY"},
            {"q": f"Walk us through your process for debugging a memory leak or silent crash in production.", "cat": "BEHAVIORAL", "top": "Debugging & Operations", "diff": "MEDIUM"},
            {"q": f"How do you approach database schema normalization vs denormalization for heavy read workloads?", "cat": "DATABASE", "top": "Database Optimization", "diff": "HARD"},
            {"q": f"What strategies do you use to test critical business logic in your code?", "cat": "TECHNICAL", "top": "Software Testing", "diff": "EASY"}
        ]

        for rq in role_questions:
            pool.append({
                "question": rq["q"],
                "category": rq["cat"],
                "topic": rq["top"],
                "source": target_role
            })

        # Pick first unasked question
        for item in pool:
            if item["question"] not in already_asked:
                return {
                    "question": item["question"],
                    "category": item["category"],
                    "difficulty": difficulty,
                    "topic": item["topic"],
                    "is_followup": last_score < WEAK_THRESHOLD,
                    "source": item["source"]
                }

        # Guaranteed fallback if pool exhausted
        q_text = f"As a {target_role}, how would you approach optimizing the response time of a slow backend database query?"
        return {
            "question": q_text if q_text not in already_asked else f"Describe how you handle system security and data validation in {target_role} systems.",
            "category": "TECHNICAL",
            "difficulty": difficulty,
            "topic": "Backend Optimization",
            "is_followup": False,
            "source": target_role
        }

    @staticmethod
    async def evaluate_full_interview(db: Session, user_id: int, interview_id: int) -> dict:
        """
        Generates the final comprehensive adaptive interview report, calculates overall scores,
        creates performance timeline graphs, and logs weak topics to the Knowledge Gap Engine.
        """
        interview = db.query(models.Interview).filter(
            models.Interview.id == interview_id,
            models.Interview.user_id == user_id
        ).first()

        if not interview:
            raise Exception("Interview session not found")

        questions = db.query(models.InterviewQuestion).filter(
            models.InterviewQuestion.interview_id == interview_id
        ).order_by(models.InterviewQuestion.question_number.asc()).all()

        progression = []
        qa_history = []
        total_overall = 0
        total_tech = 0
        total_comm = 0
        strong_count = 0
        needs_improvement_count = 0
        weak_topics = []

        for q in questions:
            ans = db.query(models.InterviewAnswer).filter(
                models.InterviewAnswer.question_id == q.id
            ).first()

            score = ans.overall_score if (ans and ans.overall_score is not None) else 70
            tech = ans.technical_score if (ans and ans.technical_score is not None) else score
            comm = ans.communication_score if (ans and ans.communication_score is not None) else score

            if score >= STRONG_THRESHOLD:
                strong_count += 1
            elif score < WEAK_THRESHOLD:
                needs_improvement_count += 1
                if q.topic and q.topic not in weak_topics:
                    weak_topics.append(q.topic)

            total_overall += score
            total_tech += tech
            total_comm += comm

            progression.append({
                "question_number": q.question_number,
                "question": q.question_text,
                "difficulty": q.difficulty or "MEDIUM",
                "category": q.category or "TECHNICAL",
                "topic": q.topic or "General",
                "score": score,
                "answer": ans.answer_text if ans else ""
            })
            if ans:
                qa_history.append({"question": q.question_text, "answer": ans.answer_text, "score": score})

        q_count = len(questions) or 1
        avg_overall = round(total_overall / q_count)
        avg_tech = round(total_tech / q_count)
        avg_comm = round(total_comm / q_count)
        avg_proj = min(100, round(avg_tech * 1.05)) if any(q.category == "PROJECT" for q in questions) else avg_tech
        avg_problem = round((avg_overall + avg_tech) / 2)

        # Gemini Final Analysis for Report
        report_data = None
        if client and qa_history:
            try:
                transcript_str = "\n".join([f"Q{idx+1}: {item['question']}\nA: {item['answer']} (Score: {item['score']}%)" for idx, item in enumerate(qa_history)])
                prompt = f"""
                You are an executive interviewer evaluating a candidate's complete adaptive interview performance.

                INTERVIEW SUMMARY:
                Target Role: {interview.target_role}
                Questions Asked: {len(qa_history)}
                TRANSCRIPT:
                {transcript_str}

                Generate strict JSON inside <json>...</json>:

                <json>
                {{
                    "ai_insight": "Detailed 2-line performance insight describing growth during interview...",
                    "strengths": ["Clear architectural explanation", "Good project domain knowledge"],
                    "weaknesses": ["Database optimization depth", "Scalability trade-offs"],
                    "recommended_preparation": ["Review database indexing concepts", "Practice system design for high traffic"]
                }}
                </json>
                """
                resp = await client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                r_text = resp.choices[0].message.content
                if "<json>" in r_text:
                    s = r_text.find("<json>") + 6
                    e = r_text.find("</json>", s)
                    report_data = json.loads(r_text[s:e].strip() if e != -1 else r_text[s:].strip(), strict=False)
                else:
                    s = r_text.find("{")
                    e = r_text.rfind("}")
                    report_data = json.loads(r_text[s:e+1], strict=False)
            except Exception as err:
                print(f"Gemini final report analysis error: {err}")

        if not report_data:
            report_data = {
                "ai_insight": f"You completed {q_count} adaptive interview questions with an overall score of {avg_overall}%.",
                "strengths": ["Demonstrated solid core technical understanding", "Engaged well across difficulty shifts"],
                "weaknesses": ["Practice explaining complex architecture trade-offs under high difficulty"],
                "recommended_preparation": ["Review database indexing & system scalability", "Practice system design questions"]
            }

        report_payload = {
            "overall_score": avg_overall,
            "technical_score": avg_tech,
            "communication_score": avg_comm,
            "project_knowledge_score": avg_proj,
            "problem_solving_score": avg_problem,
            "total_questions": len(questions),
            "strong_answers_count": strong_count,
            "needs_improvement_count": needs_improvement_count,
            "progression": progression,
            "ai_insight": report_data.get("ai_insight", ""),
            "strengths": report_data.get("strengths", []),
            "weaknesses": report_data.get("weaknesses", []),
            "recommended_preparation": report_data.get("recommended_preparation", []),
            "weak_topics_logged": weak_topics
        }

        # Save to interview record
        interview.overall_score = avg_overall
        interview.technical_score = avg_tech
        interview.communication_score = avg_comm
        interview.project_knowledge_score = avg_proj
        interview.problem_solving_score = avg_problem
        interview.feedback_json = json.dumps(report_payload)
        interview.status = "COMPLETED"
        interview.completed_at = datetime.now(timezone.utc)
        db.commit()

        # Log Activity & check achievements
        ActivityService.log_activity(db, user_id, "interview")
        try:
            from app.services import achievement_service
            achievement_service.check_achievements_for_user(db, user_id)
        except Exception as ach_err:
            print(f"Error triggering achievements: {ach_err}")

        # Connect weak topics to Knowledge Gap Engine & Adaptive Recommendations
        try:
            for w_topic in weak_topics:
                topic_db = db.query(models.Topic).filter(
                    models.Topic.name.ilike(f"%{w_topic}%")
                ).first()

                if topic_db:
                    db_eval = models.Evaluation(
                        user_id=user_id,
                        topic_id=topic_db.id,
                        explanation=f"Identified weak performance during Adaptive Interview on '{w_topic}'",
                        overall_score=min(55, avg_tech),
                        ai_score=min(55, avg_tech),
                        ai_insight=f"Identified weakness in '{w_topic}' during Adaptive Interview."
                    )
                    db.add(db_eval)
                    db.commit()
        except Exception as gap_err:
            print(f"Error syncing knowledge gaps from interview: {gap_err}")

        return report_payload
