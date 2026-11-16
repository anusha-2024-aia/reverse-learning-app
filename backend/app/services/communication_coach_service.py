import re
import json
import math
from datetime import datetime, timezone
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from app import models
from app.ai_service.gemini_agent import client, model_name
from app.core.logging_config import logger

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
    def classify_speaking_pace(wpm: Optional[Union[int, float]]) -> Optional[str]:
        """
        Classifies speaking pace based on Words Per Minute (WPM):
        - wpm < 110: Slow
        - wpm > 185: Fast
        - 110 <= wpm <= 185: Good
        Returns None if wpm is None, non-positive, or invalid.
        """
        if wpm is None or isinstance(wpm, bool):
            return None
        try:
            val = float(wpm)
            if math.isnan(val) or math.isinf(val) or val <= 0:
                return None
            if val < 110:
                return "Slow"
            elif val > 185:
                return "Fast"
            else:
                return "Good"
        except (ValueError, TypeError):
            return None

    @staticmethod
    def analyze_speaking_pace(transcript: str, duration_seconds: Optional[float] = None) -> dict:
        """
        Calculates Words Per Minute (WPM) and classifies speaking pace.
        WPM is calculated only when transcript word count and a valid positive duration are available.
        Elapsed recognition-session duration is an estimate, not exact acoustic speaking time.
        """
        if not transcript or not transcript.strip():
            return {"pace": None, "wpm": None, "pause_count": None}

        words = transcript.strip().split()
        word_count = len(words)

        is_valid_duration = False
        clean_duration = 0.0
        if duration_seconds is not None and not isinstance(duration_seconds, bool):
            try:
                parsed = float(duration_seconds)
                if not (math.isnan(parsed) or math.isinf(parsed)) and parsed > 0:
                    clean_duration = parsed
                    is_valid_duration = True
            except (ValueError, TypeError):
                is_valid_duration = False

        if is_valid_duration and word_count > 0:
            wpm = round((word_count / clean_duration) * 60)
            pace = CommunicationCoachService.classify_speaking_pace(wpm)

            # Do not fabricate pause counts without acoustic audio timestamps
            return {
                "pace": pace,
                "wpm": wpm,
                "pause_count": None
            }

        # If duration is missing, zero, negative, or invalid, do not classify pace from word count alone
        return {
            "pace": None,
            "wpm": None,
            "pause_count": None
        }

    @staticmethod
    def calculate_overall_communication_score(
        clarity: int,
        grammar: int,
        vocabulary: int,
        structure: int,
        pace: Optional[str],
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
        if pace == "Good":
            pace_score = 90
        elif pace in ("Slow", "Fast"):
            pace_score = 70
        else:
            pace_score = 75  # Neutral default when pace was not measured

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
            logger.error(f"Gemini communication quality analysis error: {err}")
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

        try:
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except Exception as err:
            try:
                db.rollback()
            except Exception:
                pass
            logger.error(f"Failed to persist communication analysis: {type(err).__name__}")
            raise

    @staticmethod
    def aggregate_interview_communication(db: Session, interview_id: int, user_id: int) -> Optional[dict]:
        """
        Aggregates communication analysis metrics across all answers for a specific interview session.
        Strictly filters by both interview_id and user_id.
        Excludes standalone practice sessions (interview_id is None) and other users/interviews.
        Returns None if no communication records exist for this interview.
        """
        if not interview_id or not user_id:
            return None

        records = db.query(models.CommunicationAnalysis).filter(
            models.CommunicationAnalysis.interview_id == interview_id,
            models.CommunicationAnalysis.user_id == user_id
        ).order_by(models.CommunicationAnalysis.id.asc()).all()

        if not records:
            return None

        # 1. Scores (non-null only)
        comm_scores = [r.communication_score for r in records if r.communication_score is not None]
        clarity_scores = [r.clarity_score for r in records if r.clarity_score is not None]
        grammar_scores = [r.grammar_score for r in records if r.grammar_score is not None]
        vocab_scores = [r.vocabulary_score for r in records if r.vocabulary_score is not None]
        struct_scores = [r.structure_score for r in records if r.structure_score is not None]

        avg_comm = round(sum(comm_scores) / len(comm_scores)) if comm_scores else None
        avg_clarity = round(sum(clarity_scores) / len(clarity_scores)) if clarity_scores else None
        avg_grammar = round(sum(grammar_scores) / len(grammar_scores)) if grammar_scores else None
        avg_vocab = round(sum(vocab_scores) / len(vocab_scores)) if vocab_scores else None
        avg_struct = round(sum(struct_scores) / len(struct_scores)) if struct_scores else None

        # 2. WPM & Speaking Pace (valid positive non-null WPM only)
        valid_wpms = [r.words_per_minute for r in records if r.words_per_minute is not None and r.words_per_minute > 0]
        has_voice_data = len(valid_wpms) > 0

        if has_voice_data:
            avg_wpm = round(sum(valid_wpms) / len(valid_wpms))
            overall_pace = CommunicationCoachService.classify_speaking_pace(avg_wpm)
        else:
            avg_wpm = None
            overall_pace = None

        # 3. Filler words aggregation
        recorded_filler_counts = [r.filler_word_count for r in records if r.filler_word_count is not None]
        total_filler_count = sum(recorded_filler_counts) if recorded_filler_counts else 0

        combined_fillers: dict[str, int] = {}
        for r in records:
            if r.filler_words_json and isinstance(r.filler_words_json, str):
                try:
                    parsed = json.loads(r.filler_words_json)
                    if isinstance(parsed, dict):
                        for word, count in parsed.items():
                            if isinstance(word, str) and isinstance(count, (int, float)) and count > 0:
                                clean_word = word.strip().lower()
                                combined_fillers[clean_word] = combined_fillers.get(clean_word, 0) + int(count)
                except Exception:
                    pass

        top_fillers = sorted(
            [{"word": word, "count": count} for word, count in combined_fillers.items()],
            key=lambda x: x["count"],
            reverse=True
        )

        # 4. Grammar improvement suggestions (deduplicate while preserving order)
        grammar_improvements = []
        seen_incorrect = set()
        for r in records:
            if r.grammar_improvements_json and isinstance(r.grammar_improvements_json, str):
                try:
                    parsed_tips = json.loads(r.grammar_improvements_json)
                    if isinstance(parsed_tips, list):
                        for tip in parsed_tips:
                            if isinstance(tip, dict):
                                inc = tip.get("incorrect")
                                if isinstance(inc, str) and inc.strip():
                                    key = inc.strip().lower()
                                    if key not in seen_incorrect:
                                        seen_incorrect.add(key)
                                        grammar_improvements.append({
                                            "incorrect": tip.get("incorrect", ""),
                                            "improved": tip.get("improved", ""),
                                            "explanation": tip.get("explanation", "")
                                        })
                except Exception:
                    pass

        # 5. Recommendation / feedback summary
        recommendations = [r.ai_coach_recommendation for r in records if r.ai_coach_recommendation and r.ai_coach_recommendation.strip()]
        coach_recommendation = recommendations[-1] if recommendations else None

        return {
            "total_answers_analyzed": len(records),
            "has_voice_data": has_voice_data,
            "average_communication_score": avg_comm,
            "average_clarity_score": avg_clarity,
            "average_grammar_score": avg_grammar,
            "average_vocabulary_score": avg_vocab,
            "average_structure_score": avg_struct,
            "average_wpm": avg_wpm,
            "overall_speaking_pace": overall_pace,
            "total_filler_words": total_filler_count,
            "top_filler_words": top_fillers,
            "grammar_improvements": grammar_improvements,
            "ai_coach_recommendation": coach_recommendation
        }

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
