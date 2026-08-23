import re
import json
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app import models
from app.ai_service.gemini_agent import client, model_name

COMMON_FILLERS = [
    "um", "uh", "like", "actually", "basically", "you know", "so", "i mean"
]

class CommunicationCoachService:

    @staticmethod
    def detect_filler_words(transcript: str) -> dict:
        """
        Detects filler words using regex boundary matching to prevent miscounting meaningful words.
        Returns total filler count and frequency breakdown.
        """
        if not transcript:
            return {"total_count": 0, "breakdown": {}, "most_used": []}

        clean_text = transcript.lower()
        breakdown = {}
        total_count = 0

        for filler in COMMON_FILLERS:
            # Match whole phrase or word
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = re.findall(pattern, clean_text)
            count = len(matches)
            if count > 0:
                breakdown[filler] = count
                total_count += count

        # Sort breakdown by frequency descending
        sorted_most_used = sorted(
            [{"filler": k, "count": v} for k, v in breakdown.items()],
            key=lambda x: x["count"],
            reverse=True
        )

        return {
            "total_count": total_count,
            "breakdown": breakdown,
            "most_used": sorted_most_used
        }

    @staticmethod
    def analyze_speaking_pace(transcript: str, duration_seconds: Optional[float] = None) -> dict:
        """
        Analyzes speaking pace. If duration_seconds is reliably provided, computes exact WPM.
        Otherwise falls back cleanly without fabricating metrics.
        """
        if not transcript or not transcript.strip():
            return {"pace": "Good", "wpm": None, "pause_count": None}

        words = transcript.strip().split()
        word_count = len(words)

        if duration_seconds and duration_seconds > 0:
            wpm = round((word_count / duration_seconds) * 60)
            if wpm < 110:
                pace = "Slow"
            elif wpm > 185:
                pace = "Fast"
            else:
                pace = "Good"

            # Estimate significant pauses if duration is provided
            expected_seconds = (word_count / 140) * 60
            pause_diff = max(0, duration_seconds - expected_seconds)
            pause_count = min(10, round(pause_diff / 1.5)) if pause_diff > 1.0 else 0

            return {
                "pace": pace,
                "wpm": wpm,
                "pause_count": pause_count
            }

        # Qualitative fallback when duration is omitted
        if word_count < 10:
            pace = "Slow"
        elif word_count > 120:
            pace = "Fast"
        else:
            pace = "Good"

        return {
            "pace": pace,
            "wpm": None,
            "pause_count": None
        }

    @staticmethod
    def calculate_overall_communication_score(
        clarity: int,
        grammar: int,
        vocabulary: int,
        structure: int,
        pace: str,
        filler_count: int
    ) -> int:
        """
        Transparent, weighted communication scoring formula:
        - Clarity: 25%
        - Grammar: 20%
        - Answer Structure: 20%
        - Vocabulary: 15%
        - Speaking Pace Control: 10%
        - Filler Word Control: 10%
        """
        pace_score = 90 if pace == "Good" else 70

        if filler_count == 0:
            filler_score = 100
        elif filler_count <= 2:
            filler_score = 85
        elif filler_count <= 5:
            filler_score = 70
        else:
            filler_score = 50

        overall = (
            (clarity * 0.25) +
            (grammar * 0.20) +
            (structure * 0.20) +
            (vocabulary * 0.15) +
            (pace_score * 0.10) +
            (filler_score * 0.10)
        )
        return min(100, max(0, round(overall)))

    @staticmethod
    async def analyze_communication_quality(transcript: str, question_text: str = "") -> dict:
        """
        Evaluates grammar, vocabulary, clarity, and answer structure using Gemini AI (with fallback).
        """
        clean_ans = transcript.strip()
        word_count = len(clean_ans.split())

        if not client:
            # Rule-based fallback evaluator
            if word_count < 10:
                clarity, grammar, vocab, struct = 60, 65, 60, 58
                g_explanation = "Your response is very short. Expand on your reasoning to improve clarity and sentence structure."
                corrections = [{"incorrect": clean_ans, "improved": f"In response to the question, {clean_ans} because it provides key advantages."}]
            elif word_count < 30:
                clarity, grammar, vocab, struct = 78, 76, 75, 74
                g_explanation = "Your explanation is understandable, but some sentences would benefit from better structural transitions."
                corrections = []
            else:
                clarity, grammar, vocab, struct = 85, 82, 84, 82
                g_explanation = "Clear, professional, and well-structured answer with good technical vocabulary."
                corrections = []

            return {
                "clarity_score": clarity,
                "grammar_score": grammar,
                "vocabulary_score": vocab,
                "structure_score": struct,
                "grammar_feedback": g_explanation,
                "grammar_improvements": corrections,
                "vocabulary_feedback": "Good use of domain terms with minor word repetition.",
                "clarity_feedback": "Your primary concept was communicated effectively.",
                "structure_feedback": "Follows a logical flow. Adding a concrete example would make it even stronger.",
                "ai_coach_recommendation": "Practice explaining your approach using a Point → Explanation → Example structure."
            }

        prompt = f"""
        You are an expert executive speech coach analyzing a candidate's voice response in an interview.

        QUESTION ASKED: "{question_text}"
        CANDIDATE TRANSCRIPT: "{transcript}"

        Evaluate communication quality across 4 key areas (0-100 scale):
        1. clarity_score: Directness, logical flow, ease of understanding.
        2. grammar_score: Grammatical precision, correct tense usage, articles, prepositions.
        3. vocabulary_score: Technical word choice, variety, domain terminology.
        4. structure_score: Logical answer framework (Point -> Explanation -> Example -> Conclusion).

        Provide 1-2 specific grammar improvements if errors are present:
        "grammar_improvements": [
            {{"incorrect": "I have developed this project yesterday.", "improved": "I developed this project yesterday."}}
        ]

        Return ONLY a strict JSON object inside <json>...</json>:

        <json>
        {{
            "clarity_score": 82,
            "grammar_score": 74,
            "vocabulary_score": 80,
            "structure_score": 78,
            "grammar_feedback": "Your explanation is understandable, but sentence tense consistency can be improved.",
            "grammar_improvements": [
                {{"incorrect": "I have used MySQL because it was easy.", "improved": "I selected MySQL because it offered structured relational data."}}
            ],
            "vocabulary_feedback": "Good use of technical terms like relational data, but 'used' was repeated.",
            "clarity_feedback": "Main idea is clear, though the transition could be more direct.",
            "structure_feedback": "Good explanation; adding a performance result would make the structure stronger.",
            "ai_coach_recommendation": "Practice answering using a Point -> Explanation -> Example format to reduce hesitations."
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
                data = json.loads(resp_text[start:end].strip() if end != -1 else resp_text[start:].strip(), strict=False)
            else:
                start = resp_text.find("{")
                end = resp_text.rfind("}")
                data = json.loads(resp_text[start:end+1], strict=False)

            return {
                "clarity_score": min(100, max(0, int(data.get("clarity_score", 75)))),
                "grammar_score": min(100, max(0, int(data.get("grammar_score", 75)))),
                "vocabulary_score": min(100, max(0, int(data.get("vocabulary_score", 75)))),
                "structure_score": min(100, max(0, int(data.get("structure_score", 75)))),
                "grammar_feedback": data.get("grammar_feedback", "Good grammatical structure."),
                "grammar_improvements": data.get("grammar_improvements", []),
                "vocabulary_feedback": data.get("vocabulary_feedback", "Appropriate technical vocabulary."),
                "clarity_feedback": data.get("clarity_feedback", "Clear communication."),
                "structure_feedback": data.get("structure_feedback", "Logical structure."),
                "ai_coach_recommendation": data.get("ai_coach_recommendation", "Focus on clear sentence structure.")
            }
        except Exception as err:
            print(f"Gemini communication quality analysis error: {err}")
            return {
                "clarity_score": 75,
                "grammar_score": 72,
                "vocabulary_score": 76,
                "structure_score": 74,
                "grammar_feedback": "Response is understandable with standard phrasing.",
                "grammar_improvements": [],
                "vocabulary_feedback": "Relevant vocabulary used.",
                "clarity_feedback": "Clear explanation.",
                "structure_feedback": "Adheres to logical explanation flow.",
                "ai_coach_recommendation": "Practice structured technical responses."
            }

    @staticmethod
    async def process_and_save_communication_analysis(
        db: Session,
        user_id: int,
        transcript: str,
        question_text: str = "",
        interview_id: Optional[int] = None,
        answer_id: Optional[int] = None,
        duration_seconds: Optional[float] = None
    ) -> models.CommunicationAnalysis:
        """
        Runs full communication analysis pipeline (fillers, pace, grammar, clarity, structure)
        and persists record to DB.
        """
        filler_info = CommunicationCoachService.detect_filler_words(transcript)
        pace_info = CommunicationCoachService.analyze_speaking_pace(transcript, duration_seconds)
        eval_info = await CommunicationCoachService.analyze_communication_quality(transcript, question_text)

        overall_score = CommunicationCoachService.calculate_overall_communication_score(
            clarity=eval_info["clarity_score"],
            grammar=eval_info["grammar_score"],
            vocabulary=eval_info["vocabulary_score"],
            structure=eval_info["structure_score"],
            pace=pace_info["pace"],
            filler_count=filler_info["total_count"]
        )

        record = models.CommunicationAnalysis(
            user_id=user_id,
            interview_id=interview_id,
            answer_id=answer_id,
            communication_score=overall_score,
            clarity_score=eval_info["clarity_score"],
            grammar_score=eval_info["grammar_score"],
            vocabulary_score=eval_info["vocabulary_score"],
            structure_score=eval_info["structure_score"],
            speaking_pace=pace_info["pace"],
            words_per_minute=pace_info["wpm"],
            pause_count=pace_info["pause_count"],
            filler_word_count=filler_info["total_count"],
            filler_words_json=json.dumps(filler_info["breakdown"]),
            grammar_feedback=eval_info["grammar_feedback"],
            grammar_improvements_json=json.dumps(eval_info["grammar_improvements"]),
            vocabulary_feedback=eval_info["vocabulary_feedback"],
            clarity_feedback=eval_info["clarity_feedback"],
            structure_feedback=eval_info["structure_feedback"],
            ai_coach_recommendation=eval_info["ai_coach_recommendation"]
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_communication_progress(db: Session, user_id: int) -> dict:
        """
        Calculates communication progress over time across multiple interviews for user_id.
        """
        records = db.query(models.CommunicationAnalysis).filter(
            models.CommunicationAnalysis.user_id == user_id
        ).order_by(models.CommunicationAnalysis.created_at.asc()).all()

        if not records:
            return {
                "has_data": False,
                "history_trend": [],
                "overall_improvement_delta": 0,
                "filler_word_delta": 0,
                "filler_percentage_reduction": 0,
                "submetric_trends": {"clarity": [], "grammar": [], "vocabulary": [], "structure": []},
                "before_vs_latest": None
            }

        # Group by interview or step sequence
        history_trend = []
        clarity_trend = []
        grammar_trend = []
        vocab_trend = []
        struct_trend = []
        fillers_trend = []

        for idx, rec in enumerate(records):
            seq_num = idx + 1
            history_trend.append({
                "interview": f"Interview {seq_num}",
                "score": rec.communication_score,
                "date": rec.created_at.strftime("%Y-%m-%d") if rec.created_at else f"Session {seq_num}"
            })
            clarity_trend.append(rec.clarity_score)
            grammar_trend.append(rec.grammar_score)
            vocab_trend.append(rec.vocabulary_score)
            struct_trend.append(rec.structure_score)
            fillers_trend.append(rec.filler_word_count)

        first_rec = records[0]
        latest_rec = records[-1]

        score_delta = latest_rec.communication_score - first_rec.communication_score
        filler_delta = latest_rec.filler_word_count - first_rec.filler_word_count
        
        if first_rec.filler_word_count > 0:
            filler_pct_reduction = round(((first_rec.filler_word_count - latest_rec.filler_word_count) / first_rec.filler_word_count) * 100)
        else:
            filler_pct_reduction = 0

        # Aggregate filler word counts across all sessions
        total_fillers_map = {}
        for r in records:
            if r.filler_words_json:
                try:
                    f_map = json.loads(r.filler_words_json)
                    for k, v in f_map.items():
                        total_fillers_map[k] = total_fillers_map.get(k, 0) + v
                except:
                    pass

        sorted_total_fillers = sorted(
            [{"filler": k, "count": v} for k, v in total_fillers_map.items()],
            key=lambda x: x["count"],
            reverse=True
        )

        return {
            "has_data": True,
            "total_interviews_analyzed": len(records),
            "history_trend": history_trend,
            "overall_improvement_delta": score_delta,
            "filler_word_delta": filler_delta,
            "filler_percentage_reduction": max(0, filler_pct_reduction),
            "submetric_trends": {
                "clarity": clarity_trend,
                "grammar": grammar_trend,
                "vocabulary": vocab_trend,
                "structure": struct_trend
            },
            "top_filler_words": sorted_total_fillers,
            "before_vs_latest": {
                "first_interview": {
                    "overall": first_rec.communication_score,
                    "clarity": first_rec.clarity_score,
                    "grammar": first_rec.grammar_score,
                    "vocabulary": first_rec.vocabulary_score,
                    "structure": first_rec.structure_score,
                    "filler_words": first_rec.filler_word_count,
                    "pace": first_rec.speaking_pace
                },
                "latest_interview": {
                    "overall": latest_rec.communication_score,
                    "clarity": latest_rec.clarity_score,
                    "grammar": latest_rec.grammar_score,
                    "vocabulary": latest_rec.vocabulary_score,
                    "structure": latest_rec.structure_score,
                    "filler_words": latest_rec.filler_word_count,
                    "pace": latest_rec.speaking_pace
                }
            }
        }

    @staticmethod
    def get_personalized_coach_summary(db: Session, user_id: int) -> dict:
        """
        Generates personalized AI Communication Coach profile and recommendation summary.
        """
        progress = CommunicationCoachService.get_communication_progress(db, user_id)
        if not progress["has_data"]:
            return {
                "communication_score": 70,
                "target_goal": 85,
                "strongest_area": "Clarity",
                "improving_area": "Vocabulary",
                "needs_focus": "Grammar",
                "recommendation": "Complete your first AI Mock Interview using voice input to unlock your personalized communication profile!"
            }

        latest = progress["before_vs_latest"]["latest_interview"]
        metrics = [
            ("Clarity", latest["clarity"]),
            ("Grammar", latest["grammar"]),
            ("Vocabulary", latest["vocabulary"]),
            ("Answer Structure", latest["structure"])
        ]

        sorted_metrics = sorted(metrics, key=lambda x: x[1], reverse=True)
        strongest = sorted_metrics[0][0]
        needs_focus = sorted_metrics[-1][0]
        improving = sorted_metrics[1][0] if len(sorted_metrics) > 1 else "Vocabulary"

        current_score = latest["overall"]
        goal_score = min(100, current_score + 10) if current_score < 85 else 90

        rec_text = f"Your communication score is currently {current_score}%. Your strongest area is {strongest}. Focus on {needs_focus} by practicing 2-minute explanations using a clear Point → Explanation → Example structure."

        return {
            "communication_score": current_score,
            "target_goal": goal_score,
            "strongest_area": strongest,
            "improving_area": improving,
            "needs_focus": needs_focus,
            "recommendation": rec_text
        }
