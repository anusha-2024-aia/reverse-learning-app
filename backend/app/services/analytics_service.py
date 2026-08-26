import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, literal
from app.models import (
    User, Evaluation, Interview, InterviewQuestion, InterviewAnswer,
    CommunicationAnalysis, Roadmap, RoadmapItem, RevisionSchedule,
    UserMastery, LearningActivity, Topic, Curriculum, Streak
)
from app.services import insights_service, knowledge_gap_engine

class AnalyticsService:

    @staticmethod
    def _parse_range_days(range_str: str) -> Optional[int]:
        r = (range_str or "30d").strip().lower()
        if r in ["7d", "7"]:
            return 7
        elif r in ["30d", "30"]:
            return 30
        elif r in ["90d", "90", "3m"]:
            return 90
        elif r in ["180d", "180", "6m"]:
            return 180
        elif r in ["365d", "365", "1y"]:
            return 365
        elif r in ["all", "alltime"]:
            return None
        return 30

    @classmethod
    def get_comprehensive_analytics(cls, db: Session, user_id: int, range_param: str = "30d") -> Dict[str, Any]:
        days_limit = cls._parse_range_days(range_param)
        now_dt = datetime.now(timezone.utc)
        cutoff_date = (now_dt - timedelta(days=days_limit)) if days_limit else None
        cutoff_date_only = cutoff_date.date() if cutoff_date else None

        user = db.query(User).filter(User.id == user_id).first()

        # -------------------------------------------------------------
        # 1. Base Evaluations & Interviews Queries
        # -------------------------------------------------------------
        evals_query = db.query(Evaluation).filter(Evaluation.user_id == user_id)
        if cutoff_date:
            evals_query = evals_query.filter(Evaluation.created_at >= cutoff_date)
        evals = evals_query.order_by(Evaluation.created_at.asc()).all()

        all_evals = db.query(Evaluation).filter(Evaluation.user_id == user_id).all()

        ints_query = db.query(Interview).filter(Interview.user_id == user_id)
        if cutoff_date:
            ints_query = ints_query.filter(Interview.created_at >= cutoff_date)
        interviews = ints_query.order_by(Interview.created_at.asc()).all()

        all_interviews = db.query(Interview).filter(Interview.user_id == user_id).all()

        comms_query = db.query(CommunicationAnalysis).filter(CommunicationAnalysis.user_id == user_id)
        if cutoff_date:
            comms_query = comms_query.filter(CommunicationAnalysis.created_at >= cutoff_date)
        comms = comms_query.order_by(CommunicationAnalysis.created_at.asc()).all()

        # -------------------------------------------------------------
        # 2. KPI Summary Metrics
        # -------------------------------------------------------------
        eval_scores = [e.overall_score or e.ai_score for e in evals if (e.overall_score or e.ai_score) is not None]
        avg_eval_score = round(sum(eval_scores) / len(eval_scores)) if eval_scores else 0

        int_scores = [i.overall_score for i in interviews if i.overall_score is not None]
        avg_interview_score = round(sum(int_scores) / len(int_scores)) if int_scores else 0

        comm_scores = [c.communication_score for c in comms if c.communication_score is not None]
        if not comm_scores and evals:
            comm_scores = [e.communication_score for e in evals if e.communication_score is not None]
        avg_comm_score = round(sum(comm_scores) / len(comm_scores)) if comm_scores else 0

        tech_eval_scores = [e.technical_score for e in evals if e.technical_score is not None]
        tech_int_scores = [i.technical_score for i in interviews if i.technical_score is not None]
        all_tech = tech_eval_scores + tech_int_scores
        technical_mastery = round(sum(all_tech) / len(all_tech)) if all_tech else (avg_eval_score or 0)

        # Learning streak
        streak = insights_service.calculate_streak(db, user_id)
        consistency_score = min(100, round((streak / 14) * 100))

        # Weighted Overall Score
        total_weights = 0
        overall_val = 0
        if technical_mastery > 0:
            overall_val += technical_mastery * 0.40
            total_weights += 0.40
        if avg_comm_score > 0:
            overall_val += avg_comm_score * 0.20
            total_weights += 0.20
        if avg_interview_score > 0:
            overall_val += avg_interview_score * 0.30
            total_weights += 0.30
        overall_val += consistency_score * 0.10
        total_weights += 0.10

        overall_score = round(overall_val / total_weights) if total_weights > 0 else 0

        has_enough_data = (len(all_evals) > 0 or len(all_interviews) > 0)

        # -------------------------------------------------------------
        # 3. Overall Score Trend (Chronological points)
        # -------------------------------------------------------------
        score_trend = []
        combined_events = []

        for e in evals:
            s = e.overall_score or e.ai_score or 0
            combined_events.append({
                "timestamp": e.created_at,
                "date": e.created_at.strftime("%b %d") if e.created_at else "Attempt",
                "score": s,
                "technical": e.technical_score or s,
                "communication": e.communication_score or 70,
                "type": "evaluation"
            })

        for i in interviews:
            s = i.overall_score or 0
            combined_events.append({
                "timestamp": i.created_at,
                "date": i.created_at.strftime("%b %d") if i.created_at else "Interview",
                "score": s,
                "technical": i.technical_score or s,
                "communication": i.communication_score or 70,
                "type": "interview"
            })

        combined_events.sort(key=lambda x: x["timestamp"] if x["timestamp"] else now_dt)

        for idx, item in enumerate(combined_events):
            score_trend.append({
                "attempt": idx + 1,
                "date": item["date"],
                "overall": item["score"],
                "technical": item["technical"],
                "communication": item["communication"],
                "type": item["type"]
            })

        # -------------------------------------------------------------
        # 4. Topic Mastery & Strongest/Weakest Topics
        # -------------------------------------------------------------
        mastery_records = db.query(UserMastery, Topic).join(
            Topic, UserMastery.topic_id == Topic.id
        ).filter(UserMastery.user_id == user_id).all()

        topic_mastery_list = []
        for m, t in mastery_records:
            score = round(m.mastery_score, 1)
            if score >= 80:
                status = "Mastered"
            elif score >= 65:
                status = "Strong"
            elif score >= 50:
                status = "Practicing"
            else:
                status = "Needs Improvement"

            topic_mastery_list.append({
                "topic_id": t.id,
                "topic_name": t.name,
                "category": t.category or "Engineering",
                "mastery_score": score,
                "attempts": m.attempts or 0,
                "status": status
            })

        # Fallback to evaluations if UserMastery records are sparse
        if not topic_mastery_list and all_evals:
            topic_evals = {}
            for e in all_evals:
                if e.topic_id not in topic_evals:
                    topic_evals[e.topic_id] = []
                topic_evals[e.topic_id].append(e.overall_score or e.ai_score or 0)
            
            for t_id, scores in topic_evals.items():
                t = db.query(Topic).filter(Topic.id == t_id).first()
                if t:
                    avg_s = round(sum(scores) / len(scores), 1)
                    topic_mastery_list.append({
                        "topic_id": t.id,
                        "topic_name": t.name,
                        "category": t.category or "Engineering",
                        "mastery_score": avg_s,
                        "attempts": len(scores),
                        "status": "Mastered" if avg_s >= 80 else ("Strong" if avg_s >= 65 else "Needs Improvement")
                    })

        topic_mastery_list.sort(key=lambda x: x["mastery_score"], reverse=True)
        strongest_topics = topic_mastery_list[:3]
        weakest_topics = sorted(topic_mastery_list, key=lambda x: x["mastery_score"])[:3]

        # -------------------------------------------------------------
        # 5. Learning Activity & Weekly Activity Breakdown
        # -------------------------------------------------------------
        act_days = days_limit or 14
        start_date_activity = (now_dt - timedelta(days=act_days - 1)).date()
        
        act_query = db.query(LearningActivity).filter(
            LearningActivity.user_id == user_id,
            LearningActivity.date_logged >= start_date_activity
        )
        activities = act_query.all()

        daily_activity_map = {}
        for i in range(act_days):
            d = start_date_activity + timedelta(days=i)
            daily_activity_map[d] = {"evaluations": 0, "interviews": 0, "revisions": 0, "total": 0}

        for a in activities:
            if a.date_logged in daily_activity_map:
                atype = a.activity_type.lower()
                if "eval" in atype or "explain" in atype:
                    daily_activity_map[a.date_logged]["evaluations"] += 1
                elif "interview" in atype:
                    daily_activity_map[a.date_logged]["interviews"] += 1
                elif "revision" in atype:
                    daily_activity_map[a.date_logged]["revisions"] += 1
                daily_activity_map[a.date_logged]["total"] += 1

        # Also tally from Evaluation, Interview, Revision tables directly to ensure 100% accuracy
        for e in evals:
            if e.created_at:
                edate = e.created_at.date()
                if edate in daily_activity_map and daily_activity_map[edate]["evaluations"] == 0:
                    daily_activity_map[edate]["evaluations"] += 1
                    daily_activity_map[edate]["total"] += 1

        for i in interviews:
            if i.created_at:
                idate = i.created_at.date()
                if idate in daily_activity_map and daily_activity_map[idate]["interviews"] == 0:
                    daily_activity_map[idate]["interviews"] += 1
                    daily_activity_map[idate]["total"] += 1

        activity_chart = []
        for d, counts in daily_activity_map.items():
            activity_chart.append({
                "date": d.strftime("%Y-%m-%d"),
                "day_name": d.strftime("%a"),
                "count": counts["total"],
                "evaluations": counts["evaluations"],
                "interviews": counts["interviews"],
                "revisions": counts["revisions"]
            })

        # Weekly Activity Totals (Last 7 days)
        last_7_days = [start_date_activity + timedelta(days=act_days - 1 - i) for i in range(7)]
        weekly_eval_count = sum(daily_activity_map[d]["evaluations"] for d in last_7_days if d in daily_activity_map)
        weekly_interview_count = sum(daily_activity_map[d]["interviews"] for d in last_7_days if d in daily_activity_map)
        weekly_revision_count = sum(daily_activity_map[d]["revisions"] for d in last_7_days if d in daily_activity_map)

        weekly_summary = {
            "sessions": len(evals) + len(interviews),
            "concepts_practiced": len(set(e.topic_id for e in evals if e.topic_id)),
            "evaluations": len(evals),
            "interviews": len(interviews),
            "revisions": len([a for a in activities if "revision" in a.activity_type.lower()])
        }

        # -------------------------------------------------------------
        # 6. Career Goal Progress (Dynamic Learning Roadmap)
        # -------------------------------------------------------------
        roadmap = db.query(Roadmap).filter(
            Roadmap.user_id == user_id,
            Roadmap.status == "active"
        ).order_by(Roadmap.created_at.desc()).first()

        goal_progress = {
            "target_role": (user.target_role if user and user.target_role else "Full Stack Developer"),
            "progress": 0.0,
            "completed_skills": 0,
            "total_skills": 0,
            "roadmap_id": None,
            "status": "NOT_STARTED",
            "items_summary": []
        }

        if roadmap:
            items = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.order_index.asc()).all()
            completed_count = sum(1 for item in items if item.status in ["STRONG", "MASTERED"])
            total_items = len(items)
            progress_pct = round((completed_count / total_items * 100), 1) if total_items > 0 else 0.0

            items_list = []
            for item in items[:6]:
                st = item.status
                if st in ["STRONG", "MASTERED"]:
                    badge_status = "Completed"
                elif st in ["IN_PROGRESS", "REVIEW", "PRACTICE"]:
                    badge_status = "In Progress"
                elif st == "WEAK":
                    badge_status = "Needs Improvement"
                else:
                    badge_status = "Locked"

                items_list.append({
                    "id": item.id,
                    "topic_name": item.topic_name,
                    "importance": item.importance,
                    "status": badge_status
                })

            goal_progress = {
                "target_role": roadmap.target_role or (user.target_role if user else "Full Stack Developer"),
                "progress": progress_pct,
                "completed_skills": completed_count,
                "total_skills": total_items,
                "roadmap_id": roadmap.id,
                "status": "IN_PROGRESS" if progress_pct > 0 else "NOT_STARTED",
                "items_summary": items_list
            }

        # -------------------------------------------------------------
        # 7. Communication Progress (Phase 10 Coach Data)
        # -------------------------------------------------------------
        comm_trend = []
        for idx, c in enumerate(comms):
            comm_trend.append({
                "interview": f"Session {idx + 1}",
                "date": c.created_at.strftime("%b %d") if c.created_at else f"#{idx+1}",
                "overall": c.communication_score,
                "clarity": c.clarity_score,
                "grammar": c.grammar_score,
                "vocabulary": c.vocabulary_score,
                "structure": c.structure_score
            })

        first_comm = comms[0].communication_score if comms else 0
        latest_comm = comms[-1].communication_score if comms else 0
        comm_delta = latest_comm - first_comm if comms else 0

        first_clarity = comms[0].clarity_score if comms else 0
        latest_clarity = comms[-1].clarity_score if comms else 0
        first_grammar = comms[0].grammar_score if comms else 0
        latest_grammar = comms[-1].grammar_score if comms else 0
        first_vocab = comms[0].vocabulary_score if comms else 0
        latest_vocab = comms[-1].vocabulary_score if comms else 0

        communication_analytics = {
            "first_score": first_comm,
            "latest_score": latest_comm,
            "improvement": comm_delta,
            "metrics": {
                "clarity": {"first": first_clarity, "latest": latest_clarity},
                "grammar": {"first": first_grammar, "latest": latest_grammar},
                "vocabulary": {"first": first_vocab, "latest": latest_vocab}
            },
            "trend": comm_trend
        }

        # -------------------------------------------------------------
        # 8. Interview Performance & Difficulty Progression (Phase 9)
        # -------------------------------------------------------------
        interview_trend_list = []
        diff_progression = []

        for idx, i in enumerate(interviews):
            s = i.overall_score or 0
            interview_trend_list.append({
                "session": f"Interview {idx + 1}",
                "date": i.created_at.strftime("%b %d") if i.created_at else f"#{idx+1}",
                "role": i.target_role,
                "score": s,
                "technical": i.technical_score or s,
                "communication": i.communication_score or s
            })

            diff_progression.append({
                "interview_id": i.id,
                "session": f"Interview {idx + 1}",
                "starting_difficulty": i.starting_difficulty or "MEDIUM",
                "final_difficulty": i.current_difficulty or "MEDIUM",
                "transition": f"{i.starting_difficulty or 'MEDIUM'} → {i.current_difficulty or 'MEDIUM'}"
            })

        int_techs = [i.technical_score for i in interviews if i.technical_score is not None]
        int_comms = [i.communication_score for i in interviews if i.communication_score is not None]
        int_projs = [i.project_knowledge_score for i in interviews if i.project_knowledge_score is not None]
        int_probs = [i.problem_solving_score for i in interviews if i.problem_solving_score is not None]

        interview_performance = {
            "completed": len(all_interviews),
            "average_score": avg_interview_score,
            "best_score": max([i.overall_score for i in all_interviews if i.overall_score], default=0),
            "technical_avg": round(sum(int_techs) / len(int_techs)) if int_techs else avg_interview_score,
            "communication_avg": round(sum(int_comms) / len(int_comms)) if int_comms else avg_comm_score,
            "project_knowledge_avg": round(sum(int_projs) / len(int_projs)) if int_projs else avg_interview_score,
            "problem_solving_avg": round(sum(int_probs) / len(int_probs)) if int_probs else avg_interview_score,
            "trend": interview_trend_list,
            "difficulty_progression": diff_progression
        }

        # -------------------------------------------------------------
        # 9. Revision Analytics (Phase 6 Smart Revision)
        # -------------------------------------------------------------
        revisions = db.query(RevisionSchedule).filter(RevisionSchedule.user_id == user_id).all()
        due_today = sum(1 for r in revisions if r.status in ["DUE", "OVERDUE"])
        rev_completed = sum(1 for r in revisions if r.status == "COMPLETED")
        overdue = sum(1 for r in revisions if r.status == "OVERDUE")
        total_revs = len(revisions)
        rev_success = round((rev_completed / total_revs * 100), 1) if total_revs > 0 else 0.0

        revision_stats = {
            "due_today": due_today,
            "completed": rev_completed,
            "overdue": overdue,
            "success_rate": rev_success
        }

        # -------------------------------------------------------------
        # 10. Knowledge Gap Analytics (Phase 2)
        # -------------------------------------------------------------
        open_gaps = sum(1 for m in topic_mastery_list if m["mastery_score"] < 60)
        improving_gaps = sum(1 for m in topic_mastery_list if 60 <= m["mastery_score"] < 80)
        resolved_gaps = sum(1 for m in topic_mastery_list if m["mastery_score"] >= 80)
        total_gaps = len(topic_mastery_list)
        gap_resolution_rate = round((resolved_gaps / total_gaps * 100), 1) if total_gaps > 0 else 0.0

        gap_details = []
        for m in topic_mastery_list:
            gap_details.append({
                "topic_name": m["topic_name"],
                "score": m["mastery_score"],
                "status": m["status"]
            })

        knowledge_gap_stats = {
            "open_gaps": open_gaps,
            "improving_gaps": improving_gaps,
            "resolved_gaps": resolved_gaps,
            "resolution_rate": gap_resolution_rate,
            "gaps": gap_details
        }

        # -------------------------------------------------------------
        # 11. AI Learning Insight & Recommended Next Action
        # -------------------------------------------------------------
        insight_text = cls._generate_ai_insight(
            user_name=user.name or user.username if user else "Student",
            overall_score=overall_score,
            technical_mastery=technical_mastery,
            comm_score=avg_comm_score,
            strong_topics=strongest_topics,
            weak_topics=weakest_topics,
            comm_delta=comm_delta
        )

        next_rec = knowledge_gap_engine.get_next_best_action(db, user_id)

        return {
            "summary": {
                "overallScore": overall_score,
                "technicalMastery": technical_mastery,
                "communicationScore": avg_comm_score,
                "interviewReadiness": avg_interview_score,
                "learningStreak": streak
            },
            "scoreTrend": score_trend,
            "topicMastery": topic_mastery_list,
            "strongestTopics": strongest_topics,
            "weakestTopics": weakest_topics,
            "learningActivity": activity_chart,
            "weeklySummary": weekly_summary,
            "goalProgress": goal_progress,
            "communicationAnalytics": communication_analytics,
            "interviewPerformance": interview_performance,
            "revisionStats": revision_stats,
            "knowledgeGapStats": knowledge_gap_stats,
            "aiInsight": {"text": insight_text},
            "recommendedNextAction": next_rec,
            "has_enough_data": has_enough_data,
            "range": range_param
        }

    @staticmethod
    def _generate_ai_insight(user_name: str, overall_score: int, technical_mastery: int, comm_score: int, strong_topics: List[dict], weak_topics: List[dict], comm_delta: int) -> str:
        strong_str = ", ".join([t["topic_name"] for t in strong_topics[:2]]) if strong_topics else "your core skills"
        weak_str = ", ".join([t["topic_name"] for t in weak_topics[:2]]) if weak_topics else "newer topics"

        if overall_score >= 80:
            return f"Excellent performance, {user_name}! Your technical mastery ({technical_mastery}%) is strong, especially in {strong_str}. Keep practicing {weak_str} to maintain your high readiness."
        elif overall_score >= 60:
            return f"Solid progress, {user_name}! You've reached an overall score of {overall_score}%. Your strongest area is {strong_str}, while {weak_str} remain key focus areas for revision."
        else:
            return f"Keep going, {user_name}! You are building your foundation. Focus on completing evaluations in {weak_str} to boost your overall technical score."
