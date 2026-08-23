from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import datetime, timedelta, timezone
from app.models import RevisionSchedule, Topic, Evaluation, RoadmapItem
from app.services.knowledge_gap_engine import analyze_user_knowledge

# Rule-Based Centralized Configuration
LOW_MASTERY_INTERVAL = 1      # Mastery < 60% -> 1 day
MEDIUM_MASTERY_INTERVAL = 3   # Mastery 60%–79% -> 3 days
GOOD_MASTERY_INTERVAL = 7     # Mastery 80%–89% -> 7 days
HIGH_MASTERY_INTERVAL = 14    # Mastery >= 90% -> 14 days

class SmartRevisionService:

    @staticmethod
    def calculate_revision_interval(mastery_score: float) -> int:
        """
        Deterministic rule-based interval calculation.
        Mastery < 60%   → 1 day
        Mastery 60-79%  → 3 days
        Mastery 80-89%  → 7 days
        Mastery >= 90%  → 14 days
        """
        score = float(mastery_score)
        if score < 60.0:
            return LOW_MASTERY_INTERVAL
        elif score < 80.0:
            return MEDIUM_MASTERY_INTERVAL
        elif score < 90.0:
            return GOOD_MASTERY_INTERVAL
        else:
            return HIGH_MASTERY_INTERVAL

    @staticmethod
    def calculate_next_review_date(
        mastery_score: float, 
        last_reviewed_at: datetime = None, 
        has_knowledge_gap: bool = False,
        trend: str = "STABLE"
    ) -> datetime:
        """
        Calculates the next review date considering mastery score, 
        knowledge gap overrides, and performance trend.
        """
        if not last_reviewed_at:
            last_reviewed_at = datetime.now(timezone.utc)
            
        interval_days = SmartRevisionService.calculate_revision_interval(mastery_score)
        
        # Knowledge Gap Override: If unresolved knowledge gap exists, cap interval sooner
        if has_knowledge_gap and interval_days > 3:
            interval_days = 3
            
        # Downward Performance Trend: If score is declining, shorten interval
        if trend == "DECLINING" and interval_days > 3:
            interval_days = 3

        return last_reviewed_at + timedelta(days=interval_days)

    @staticmethod
    def get_dynamic_status(next_review_at: datetime) -> str:
        """
        Determines revision status dynamically from the current date.
        """
        if not next_review_at:
            return "DUE"
            
        today = datetime.now(timezone.utc).date()
        review_date = next_review_at.date()
        
        if review_date == today:
            return "DUE"
        elif review_date < today:
            return "OVERDUE"
        else:
            return "UPCOMING"

    @staticmethod
    def calculate_priority_score(
        mastery_score: float, 
        has_knowledge_gap: bool, 
        trend: str, 
        status: str,
        failed_attempts: int = 0
    ) -> float:
        """
        Calculates a priority score to rank due revisions intelligently.
        Priority factors:
        1. Knowledge Gap existence (+50)
        2. Low Mastery Score (100 - score)
        3. Declining trend (+30)
        4. Overdue status (+20)
        5. Failed attempts (+5 * failed_attempts)
        """
        base = max(0.0, 100.0 - float(mastery_score))
        gap_bonus = 50.0 if has_knowledge_gap else 0.0
        trend_bonus = 30.0 if trend == "DECLINING" else 0.0
        overdue_bonus = 20.0 if status == "OVERDUE" else 0.0
        fail_bonus = min(20.0, failed_attempts * 5.0)
        
        return base + gap_bonus + trend_bonus + overdue_bonus + fail_bonus

    @staticmethod
    def update_revision_schedule(db: Session, user_id: int, topic_id: int, new_mastery_score: float) -> RevisionSchedule:
        """
        Updates or creates a RevisionSchedule record for a user and topic after evaluation.
        Recalculates intervals, next review date, and status.
        """
        now = datetime.now(timezone.utc)
        
        # Check existing schedule
        schedule = db.query(RevisionSchedule).filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.topic_id == topic_id
        ).first()

        if not schedule:
            schedule = RevisionSchedule(
                user_id=user_id,
                topic_id=topic_id,
                last_mastery_score=float(new_mastery_score),
                current_mastery_score=float(new_mastery_score),
                last_reviewed_at=now,
                review_count=1,
                created_at=now
            )
            db.add(schedule)
        else:
            schedule.last_mastery_score = schedule.current_mastery_score
            schedule.current_mastery_score = float(new_mastery_score)
            schedule.last_reviewed_at = now
            schedule.review_count = (schedule.review_count or 0) + 1

        # Check knowledge gap & trend for this topic
        user_gaps = analyze_user_knowledge(db, user_id)
        topic_gap = next((g for g in user_gaps if g["topic_id"] == topic_id), None)
        has_knowledge_gap = bool(topic_gap and topic_gap.get("severity") in ["CRITICAL", "HIGH", "MEDIUM"])
        trend = topic_gap.get("trend", "STABLE") if topic_gap else "STABLE"

        # Calculate next review date
        schedule.next_review_at = SmartRevisionService.calculate_next_review_date(
            mastery_score=schedule.current_mastery_score,
            last_reviewed_at=now,
            has_knowledge_gap=has_knowledge_gap,
            trend=trend
        )
        
        schedule.status = SmartRevisionService.get_dynamic_status(schedule.next_review_at)
        schedule.updated_at = now

        db.commit()
        db.refresh(schedule)

        # Sync with Phase 5 RoadmapItem if exists
        try:
            roadmap_items = db.query(RoadmapItem).filter(
                RoadmapItem.user_id == user_id,
                RoadmapItem.topic_id == topic_id
            ).all()
            for r_item in roadmap_items:
                r_item.mastery_score = new_mastery_score
                r_item.last_evaluated_at = now
                if new_mastery_score >= 80.0:
                    r_item.status = "MASTERED"
                elif new_mastery_score < 60.0:
                    r_item.status = "WEAK"
                else:
                    r_item.status = "IN_PROGRESS"
            if roadmap_items:
                db.commit()
        except Exception as sync_err:
            print(f"Error syncing revision to roadmap: {sync_err}")

        return schedule

    @staticmethod
    def get_user_revisions(db: Session, user_id: int):
        """
        Fetches and categorizes revision schedules for the given authenticated user.
        Categorization:
        - overdue
        - due_today
        - tomorrow
        - upcoming
        - history
        - summary
        """
        # Ensure user knowledge gaps are loaded
        user_gaps = analyze_user_knowledge(db, user_id)
        gap_dict = {g["topic_id"]: g for g in user_gaps}

        # Query all revision schedules for user
        schedules = db.query(RevisionSchedule, Topic).join(
            Topic, RevisionSchedule.topic_id == Topic.id
        ).filter(RevisionSchedule.user_id == user_id).all()

        now = datetime.now(timezone.utc)
        today = now.date()
        tomorrow_date = today + timedelta(days=1)

        overdue_list = []
        due_today_list = []
        tomorrow_list = []
        upcoming_list = []
        
        for sched, topic in schedules:
            # Dynamically update status
            status = SmartRevisionService.get_dynamic_status(sched.next_review_at)
            sched.status = status
            
            topic_gap = gap_dict.get(topic.id)
            has_knowledge_gap = bool(topic_gap and topic_gap.get("severity") in ["CRITICAL", "HIGH", "MEDIUM"])
            target_concept = topic_gap.get("recommendation", "") if topic_gap else None
            trend = topic_gap.get("trend", "STABLE") if topic_gap else "STABLE"

            # Fetch attempts count from Evaluation table
            attempt_count = db.query(Evaluation).filter(
                Evaluation.user_id == user_id,
                Evaluation.topic_id == topic.id
            ).count()

            # Calculate Priority
            priority = SmartRevisionService.calculate_priority_score(
                mastery_score=sched.current_mastery_score,
                has_knowledge_gap=has_knowledge_gap,
                trend=trend,
                status=status,
                failed_attempts=max(0, attempt_count - 1)
            )

            # Days relative to today
            review_date = sched.next_review_at.date() if sched.next_review_at else today
            days_diff = (review_date - today).days

            interval_days = SmartRevisionService.calculate_revision_interval(sched.current_mastery_score)

            card = {
                "id": sched.id,
                "topic_id": topic.id,
                "topic_name": topic.name,
                "category": topic.category or "General",
                "mastery_score": round(sched.current_mastery_score, 1),
                "last_mastery_score": round(sched.last_mastery_score or sched.current_mastery_score, 1),
                "status": status,
                "next_review_at": sched.next_review_at.isoformat() if sched.next_review_at else None,
                "last_reviewed_at": sched.last_reviewed_at.isoformat() if sched.last_reviewed_at else None,
                "review_count": sched.review_count or 1,
                "attempts": attempt_count,
                "has_knowledge_gap": has_knowledge_gap,
                "knowledge_gap": topic_gap.get("recommendation") if has_knowledge_gap else None,
                "target_concept": target_concept,
                "trend": trend,
                "priority_score": priority,
                "interval_days": interval_days,
                "days_until_due": days_diff
            }

            if status == "OVERDUE":
                overdue_list.append(card)
            elif status == "DUE":
                due_today_list.append(card)
            elif review_date == tomorrow_date:
                tomorrow_list.append(card)
            else:
                upcoming_list.append(card)

        # Sort lists by priority score (descending)
        overdue_list.sort(key=lambda x: x["priority_score"], reverse=True)
        due_today_list.sort(key=lambda x: x["priority_score"], reverse=True)
        tomorrow_list.sort(key=lambda x: x["priority_score"], reverse=True)
        upcoming_list.sort(key=lambda x: (x["days_until_due"], -x["priority_score"]))

        # Group upcoming by interval label (e.g. In 3 Days, In 7 Days, In 14 Days, Later)
        grouped_upcoming = {}
        for item in upcoming_list:
            d = item["days_until_due"]
            if d <= 3:
                label = f"In {d} Days"
            elif d <= 7:
                label = "In 7 Days"
            elif d <= 14:
                label = "In 14 Days"
            else:
                label = "Later"
            
            if label not in grouped_upcoming:
                grouped_upcoming[label] = []
            grouped_upcoming[label].append(item)

        # Fetch overall revision history across topics
        history_list = SmartRevisionService.get_user_revision_history_all(db, user_id)

        return {
            "summary": {
                "due_today_count": len(due_today_list),
                "overdue_count": len(overdue_list),
                "tomorrow_count": len(tomorrow_list),
                "upcoming_count": len(upcoming_list) + len(tomorrow_list),
                "total_scheduled": len(schedules)
            },
            "due_today": due_today_list,
            "overdue": overdue_list,
            "tomorrow": tomorrow_list,
            "upcoming": upcoming_list,
            "grouped_upcoming": grouped_upcoming,
            "history": history_list
        }

    @staticmethod
    def get_user_revision_history_all(db: Session, user_id: int):
        """
        Fetches historical revision performance progression per topic for the user.
        """
        evals = db.query(Evaluation, Topic).join(
            Topic, Evaluation.topic_id == Topic.id
        ).filter(Evaluation.user_id == user_id).order_by(Evaluation.created_at.asc()).all()

        topic_evals = {}
        for e, t in evals:
            if t.id not in topic_evals:
                topic_evals[t.id] = {
                    "topic_id": t.id,
                    "topic_name": t.name,
                    "attempts": []
                }
            score = e.overall_score or e.ai_score or 0
            topic_evals[t.id]["attempts"].append({
                "evaluation_id": e.id,
                "score": score,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "date_formatted": e.created_at.strftime("%b %d") if e.created_at else "Recent"
            })

        result = []
        for t_id, data in topic_evals.items():
            attempts = data["attempts"]
            if not attempts:
                continue
            first_score = attempts[0]["score"]
            latest_score = attempts[-1]["score"]
            improvement = latest_score - first_score
            scores_progression = " → ".join([f"{a['score']}%" for a in attempts])
            
            # Fetch latest next_review_at for topic
            sched = db.query(RevisionSchedule).filter(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.topic_id == t_id
            ).first()

            result.append({
                "topic_id": t_id,
                "topic_name": data["topic_name"],
                "total_attempts": len(attempts),
                "first_score": first_score,
                "latest_score": latest_score,
                "improvement": improvement,
                "scores_progression": scores_progression,
                "history_attempts": attempts,
                "next_review_at": sched.next_review_at.isoformat() if sched and sched.next_review_at else None,
                "next_review_formatted": sched.next_review_at.strftime("%b %d") if sched and sched.next_review_at else "Not Scheduled"
            })

        return result

    @staticmethod
    def get_revision_briefing(db: Session, user_id: int, topic_id: int):
        """
        Prepares pre-revision briefing data for the focused revision experience.
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return None

        sched = db.query(RevisionSchedule).filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.topic_id == topic_id
        ).first()

        user_gaps = analyze_user_knowledge(db, user_id)
        topic_gap = next((g for g in user_gaps if g["topic_id"] == topic_id), None)
        
        target_concept = None
        if topic_gap and topic_gap.get("severity") in ["CRITICAL", "HIGH", "MEDIUM"]:
            target_concept = topic_gap.get("recommendation")

        current_mastery = round(sched.current_mastery_score, 1) if sched else 0.0

        return {
            "topic_id": topic.id,
            "topic_name": topic.name,
            "description": topic.description or topic.category,
            "current_mastery": current_mastery,
            "focus_concept": target_concept,
            "revision_goal": f"Master {topic.name} by explaining the concepts, handling boundary cases, and providing accurate examples."
        }
