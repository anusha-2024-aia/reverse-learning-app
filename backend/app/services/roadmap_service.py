import json
import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Roadmap, RoadmapItem, RoadmapChange, User, Topic, Evaluation
from app.ai_service.gemini_agent import generate_ai_roadmap, get_fallback_roadmap
from app.services.knowledge_gap_engine import analyze_user_knowledge

class RoadmapService:
    @staticmethod
    async def generate_initial_roadmap(db: Session, user: User, onboarding_data: dict = None) -> dict:
        """
        Processes onboarding data, saves user profile preferences, calls AI generator,
        and saves a structured learning roadmap to the database.
        """
        data = onboarding_data or {}
        
        # 1. Save onboarding data to user profile
        user.target_role = data.get("target_role") or user.target_role or "Full Stack Developer"
        user.experience_level = data.get("experience_level") or user.experience_level or "BEGINNER"
        user.learning_goals = data.get("career_goal") or user.learning_goals or "Get placement as a software engineer"
        user.hours_per_day = float(data.get("hours_per_day", 2.0))
        user.days_per_week = int(data.get("days_per_week", 6))
        
        skills_raw = data.get("current_skills", [])
        if isinstance(skills_raw, list):
            user.current_skills = json.dumps(skills_raw)
        else:
            user.current_skills = json.dumps([s.strip() for s in str(skills_raw).split(",") if s.strip()])
            
        prefs_raw = data.get("preferred_areas", [])
        if isinstance(prefs_raw, list):
            user.preferred_areas = json.dumps(prefs_raw)
        else:
            user.preferred_areas = json.dumps([p.strip() for p in str(prefs_raw).split(",") if p.strip()])
            
        user.onboarding_completed = True
        db.commit()
        db.refresh(user)

        # 2. Get demonstrated performance data & knowledge gaps from DB
        eval_gaps = analyze_user_knowledge(db, user.id)
        
        # 3. Call AI to generate roadmap structure
        current_skills_list = json.loads(user.current_skills or "[]")
        preferred_areas_list = json.loads(user.preferred_areas or "[]")
        
        ai_res = await generate_ai_roadmap(
            target_role=user.target_role,
            current_skills=current_skills_list,
            experience_level=user.experience_level,
            career_goal=user.learning_goals,
            hours_per_day=user.hours_per_day,
            days_per_week=user.days_per_week,
            preferred_areas=preferred_areas_list,
            performance_data=eval_gaps,
            knowledge_gaps=eval_gaps
        )
        
        topics_data = ai_res.get("topics", [])

        # 4. Archive old active roadmaps for this user
        existing_roadmaps = db.query(Roadmap).filter(Roadmap.user_id == user.id, Roadmap.status == "active").all()
        for rm in existing_roadmaps:
            rm.status = "archived"
        db.commit()

        # 5. Create new active Roadmap record
        new_roadmap = Roadmap(
            user_id=user.id,
            target_role=user.target_role,
            career_goal=user.learning_goals,
            experience_level=user.experience_level,
            hours_per_day=user.hours_per_day,
            days_per_week=user.days_per_week,
            preferred_areas=user.preferred_areas,
            version=1,
            progress=0.0,
            estimated_hours=sum(t.get("estimated_hours", 15) for t in topics_data),
            status="active"
        )
        db.add(new_roadmap)
        db.commit()
        db.refresh(new_roadmap)

        # 6. Save RoadmapItems
        db_topics = db.query(Topic).all()
        topic_map = {t.name.lower(): t.id for t in db_topics}

        for idx, item in enumerate(topics_data):
            t_name = item.get("topic_name", f"Topic {idx+1}")
            matched_topic_id = topic_map.get(t_name.lower())

            roadmap_item = RoadmapItem(
                roadmap_id=new_roadmap.id,
                user_id=user.id,
                topic_name=t_name,
                category=item.get("category", "General"),
                description=item.get("description", ""),
                importance=item.get("importance", "HIGH"),
                difficulty=item.get("difficulty", "BEGINNER"),
                prerequisites=json.dumps(item.get("prerequisites", [])),
                estimated_hours=item.get("estimated_hours", 15),
                mastery_score=0.0,
                priority_score=0.0,
                status="NOT_STARTED",
                reason=item.get("reason", ""),
                skills_gained=json.dumps(item.get("skills_gained", [])),
                order_index=idx + 1,
                topic_id=matched_topic_id
            )
            db.add(roadmap_item)

        db.commit()

        # 7. Log Change Record
        change = RoadmapChange(
            roadmap_id=new_roadmap.id,
            user_id=user.id,
            change_type="INITIAL_GENERATED",
            topic_name="Roadmap",
            reason=f"Initial roadmap created for role: {user.target_role} ({len(topics_data)} topics)."
        )
        db.add(change)
        db.commit()

        # 8. Run deterministic recalculation to apply real scores & status
        RoadmapService.recalculate_roadmap(db, user.id)

        return RoadmapService.get_my_roadmap(db, user.id)

    @staticmethod
    def recalculate_roadmap(db: Session, user_id: int) -> dict:
        """
        Deterministic Dynamic Engine: Recalculates topic mastery, unlocks prerequisites,
        surfaces weak prerequisites, computes priority scores, updates statuses, reorders queue,
        updates overall progress %, and logs changes.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.status == "active").first()
        if not roadmap:
            return None

        items = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.order_index.asc()).all()
        if not items:
            return None

        # Fetch actual evaluated knowledge gaps from Knowledge Gap Engine
        knowledge_gaps = analyze_user_knowledge(db, user_id)
        gap_dict = {g["topic_name"].lower(): g for g in knowledge_gaps}
        
        # Also check by topic_id
        gap_id_dict = {g["topic_id"]: g for g in knowledge_gaps if g.get("topic_id")}

        # User's self-reported skills
        self_skills = [s.lower() for s in json.loads(user.current_skills or "[]")]

        # Step A: Evaluate mastery & baseline score for each item
        mastery_map = {} # topic_name.lower() -> mastery_score
        item_data_list = []

        for item in items:
            t_name_lower = item.topic_name.lower()
            
            # Find evaluation data
            eval_data = gap_dict.get(t_name_lower) or (gap_id_dict.get(item.topic_id) if item.topic_id else None)
            
            if eval_data:
                # Direct demonstrated score ALWAYS overrides self-reported claim
                mastery = float(eval_data["mastery_score"])
                attempts = eval_data["attempts"]
                trend = eval_data["trend"]
                severity = eval_data["severity"]
            else:
                # Check evaluations directly by topic_id or topic_name if gap engine missed it
                evals = []
                if item.topic_id:
                    evals = db.query(Evaluation).filter(Evaluation.user_id == user_id, Evaluation.topic_id == item.topic_id).all()
                if evals:
                    scores = [e.overall_score or e.ai_score or 0 for e in evals]
                    mastery = float(scores[-1])
                    attempts = len(scores)
                    trend = "STABLE"
                    severity = "LOW" if mastery >= 75 else "MEDIUM"
                elif any(sk in t_name_lower for sk in self_skills):
                    # Self reported skill with 0 evaluations -> default baseline 60%
                    mastery = 60.0
                    attempts = 0
                    trend = "STABLE"
                    severity = "LOW"
                else:
                    mastery = 0.0
                    attempts = 0
                    trend = "STABLE"
                    severity = "LOW"

            item.mastery_score = round(mastery, 1)
            mastery_map[t_name_lower] = item.mastery_score
            item_data_list.append({
                "item": item,
                "attempts": attempts,
                "trend": trend,
                "severity": severity,
                "eval_data": eval_data
            })

        # Step B: Evaluate Prerequisites and Determine Status
        has_weak_focus = False

        for entry in item_data_list:
            item = entry["item"]
            prereqs = json.loads(item.prerequisites or "[]")
            
            # Check if all prerequisites have sufficient mastery (>= 70%)
            prereqs_met = True
            unmet_prereqs = []
            for p_name in prereqs:
                p_score = mastery_map.get(p_name.lower(), 0.0)
                if p_score < 70.0:
                    prereqs_met = False
                    unmet_prereqs.append(p_name)

            mastery = item.mastery_score
            attempts = entry["attempts"]
            trend = entry["trend"]
            severity = entry["severity"]
            old_status = item.status

            # Mastered rule: >= 85% mastery with at least 2 evaluations
            if mastery >= 85.0 and attempts >= 2:
                new_status = "MASTERED"
            elif mastery >= 80.0:
                new_status = "PRACTICE" if trend == "DECLINING" else "STRONG"
            elif mastery >= 65.0:
                new_status = "PRACTICE"
            elif mastery >= 50.0:
                new_status = "REVIEW" if trend == "DECLINING" else "DEVELOPING"
            elif attempts > 0 and (trend == "DECLINING" or severity in ["HIGH", "CRITICAL"] or mastery < 50.0):
                new_status = "WEAK"
                has_weak_focus = True
            elif attempts > 0:
                new_status = "IN_PROGRESS"
            elif prereqs_met:
                new_status = "NOT_STARTED"
            else:
                new_status = "LOCKED"

            item.status = new_status

            # Log status change if changed
            if old_status and old_status != new_status:
                reason_text = f"Status changed from {old_status} to {new_status} (Mastery: {mastery}%)."
                if new_status == "WEAK":
                    reason_text = f"Marked as WEAK because demonstrated performance dropped to {mastery}%."
                elif new_status == "MASTERED":
                    reason_text = f"Marked as MASTERED after consistent high scores ({mastery}% across {attempts} evaluations)."

                change = RoadmapChange(
                    roadmap_id=roadmap.id,
                    user_id=user_id,
                    change_type="STATUS_CHANGED",
                    topic_name=item.topic_name,
                    reason=reason_text
                )
                db.add(change)

        # Step C: Surface Weak Prerequisites (Adaptive Prerequisite Insertion)
        for entry in item_data_list:
            item = entry["item"]
            if item.status in ["WEAK", "REVIEW"] or entry["severity"] in ["CRITICAL", "HIGH"]:
                # Find prerequisites of this weak topic that are weak or developing
                prereqs = json.loads(item.prerequisites or "[]")
                for p_name in prereqs:
                    for target_entry in item_data_list:
                        target_item = target_entry["item"]
                        if target_item.topic_name.lower() == p_name.lower() and target_item.mastery_score < 75.0:
                            # Pull this prerequisite forward!
                            target_item.status = "WEAK"
                            target_item.reason = f"Surfaced as priority prerequisite because you are struggling with {item.topic_name}."

        # Step D: Calculate Priority Score for Dynamic Reordering
        # Weights: Role Importance 20%, Weakness 25%, Knowledge Gap 15%, Recent Performance 10%, Trend 10%, Prerequisite Readiness 10%, Career Relevance 10%
        for entry in item_data_list:
            item = entry["item"]
            mastery = item.mastery_score
            trend = entry["trend"]
            severity = entry["severity"]

            importance_weight = 100.0 if item.importance == "HIGH" else (70.0 if item.importance == "MEDIUM" else 40.0)
            weakness_val = max(0.0, 100.0 - mastery)
            gap_val = 100.0 if severity == "CRITICAL" else (80.0 if severity == "HIGH" else (50.0 if severity == "MEDIUM" else 20.0))
            recent_val = 100.0 if (mastery < 65.0 and entry["attempts"] > 0) else 40.0
            trend_val = 100.0 if trend == "DECLINING" else (50.0 if trend == "STABLE" else 10.0)
            
            # Prerequisite readiness
            prereqs = json.loads(item.prerequisites or "[]")
            prereqs_met = all(mastery_map.get(p.lower(), 0.0) >= 70.0 for p in prereqs)
            readiness_val = 100.0 if prereqs_met else 0.0

            priority = (
                importance_weight * 0.20 +
                weakness_val * 0.25 +
                gap_val * 0.15 +
                recent_val * 0.10 +
                trend_val * 0.10 +
                readiness_val * 0.10 +
                80.0 * 0.10
            )

            # Locked topics capped at lower priority
            if item.status == "LOCKED":
                priority = min(30.0, priority)
            # Mastered topics lower priority
            elif item.status == "MASTERED":
                priority = min(25.0, priority)
            # Weak / Current Focus topics boosted
            elif item.status == "WEAK":
                priority = max(90.0, priority + 30.0)

            item.priority_score = round(min(100.0, priority), 1)

            # Generate explainable reason
            if item.status == "WEAK":
                item.reason = f"CURRENT FOCUS: Mastery is {mastery}%. Recent performance requires remediation."
            elif item.status == "MASTERED":
                item.reason = f"MASTERED ({mastery}%): Strong understanding demonstrated across evaluations."
            elif item.status == "LOCKED":
                item.reason = f"LOCKED: Complete prerequisites first ({', '.join(prereqs)})."
            elif item.status in ["STRONG", "PRACTICE"]:
                item.reason = f"Available for practice. Demonstrated mastery: {mastery}%."
            else:
                item.reason = f"Next topic in your {user.target_role} roadmap."

        # Step E: Reorder Queue
        # Status rank order: WEAK (1), IN_PROGRESS (2), REVIEW (3), PRACTICE (4), NOT_STARTED (5), STRONG (6), MASTERED (7), LOCKED (8)
        status_rank = {
            "WEAK": 1,
            "IN_PROGRESS": 2,
            "REVIEW": 3,
            "PRACTICE": 4,
            "NOT_STARTED": 5,
            "STRONG": 6,
            "MASTERED": 7,
            "LOCKED": 8
        }

        # Sort items deterministically
        sorted_items = sorted(
            items,
            key=lambda x: (status_rank.get(x.status, 5), -x.priority_score, x.order_index)
        )

        for idx, item in enumerate(sorted_items):
            old_idx = item.order_index
            new_idx = idx + 1
            if old_idx != new_idx and abs(old_idx - new_idx) >= 2:
                # Log reorder event
                change = RoadmapChange(
                    roadmap_id=roadmap.id,
                    user_id=user_id,
                    change_type="REORDERED",
                    topic_name=item.topic_name,
                    old_position=old_idx,
                    new_position=new_idx,
                    reason=f"Moved to position {new_idx} (Status: {item.status}, Priority: {item.priority_score})."
                )
                db.add(change)

            item.order_index = new_idx

        # Step F: Overall Roadmap Progress & Time Calculation
        total_items = len(items)
        if total_items > 0:
            weighted_mastery_sum = sum(min(100.0, i.mastery_score) for i in items)
            roadmap.progress = round(weighted_mastery_sum / total_items, 1)

        remaining_hours = sum(i.estimated_hours for i in items if i.status != "MASTERED")
        roadmap.estimated_hours = remaining_hours
        roadmap.updated_at = datetime.now(timezone.utc)

        db.commit()
        return RoadmapService.get_my_roadmap(db, user_id)

    @staticmethod
    def get_my_roadmap(db: Session, user_id: int) -> dict:
        """
        Retrieves active roadmap for user with full topics list, current focus,
        progress %, estimated completion time, and daily plan.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"roadmap": None, "onboarding_completed": False}

        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.status == "active").first()
        if not roadmap:
            return {"roadmap": None, "onboarding_completed": bool(user.onboarding_completed)}

        items = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.order_index.asc()).all()

        formatted_items = []
        for item in items:
            prereqs = json.loads(item.prerequisites or "[]")
            skills = json.loads(item.skills_gained or "[]")
            formatted_items.append({
                "id": item.id,
                "topic_name": item.topic_name,
                "category": item.category or "Engineering",
                "description": item.description or "",
                "importance": item.importance or "HIGH",
                "difficulty": item.difficulty or "BEGINNER",
                "prerequisites": prereqs,
                "estimated_hours": item.estimated_hours or 10,
                "mastery_score": item.mastery_score or 0.0,
                "priority_score": item.priority_score or 0.0,
                "status": item.status or "NOT_STARTED",
                "reason": item.reason or "",
                "skills_gained": skills,
                "order_index": item.order_index,
                "topic_id": item.topic_id
            })

        # Calculate estimated completion days based on available hours/day
        hours_per_day = roadmap.hours_per_day or user.hours_per_day or 2.0
        days_per_week = roadmap.days_per_week or user.days_per_week or 6
        remaining_hours = roadmap.estimated_hours or sum(i["estimated_hours"] for i in formatted_items if i["status"] != "MASTERED")
        
        estimated_days = math.ceil(remaining_hours / max(0.5, hours_per_day)) if remaining_hours > 0 else 0

        # Current Focus Topic
        current_focus = None
        for item in formatted_items:
            if item["status"] in ["WEAK", "IN_PROGRESS", "REVIEW", "NOT_STARTED"]:
                current_focus = item
                break
        if not current_focus and formatted_items:
            current_focus = formatted_items[0]

        # Recent Changes History
        recent_changes = db.query(RoadmapChange).filter(RoadmapChange.roadmap_id == roadmap.id).order_by(RoadmapChange.created_at.desc()).limit(10).all()
        history = [
            {
                "id": c.id,
                "change_type": c.change_type,
                "topic_name": c.topic_name,
                "old_position": c.old_position,
                "new_position": c.new_position,
                "reason": c.reason,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in recent_changes
        ]

        # Today's Learning Plan
        daily_plan = RoadmapService.generate_daily_plan_struct(current_focus, hours_per_day)

        return {
            "roadmap_id": roadmap.id,
            "target_role": roadmap.target_role,
            "career_goal": roadmap.career_goal or user.learning_goals,
            "experience_level": roadmap.experience_level or user.experience_level,
            "hours_per_day": hours_per_day,
            "days_per_week": days_per_week,
            "preferred_areas": json.loads(roadmap.preferred_areas or "[]"),
            "progress": roadmap.progress,
            "version": roadmap.version,
            "estimated_hours": remaining_hours,
            "estimated_days": estimated_days,
            "current_focus": current_focus,
            "daily_plan": daily_plan,
            "items": formatted_items,
            "history": history,
            "onboarding_completed": True
        }

    @staticmethod
    def generate_daily_plan_struct(current_focus: dict, hours_per_day: float) -> dict:
        """
        Generates a structured daily learning plan tailored to available hours/day.
        """
        total_mins = int(hours_per_day * 60)
        topic_name = current_focus["topic_name"] if current_focus else "Core Technical Skills"
        
        # Breakdown ratio: 20% review, 40% core concept, 25% practice, 15% evaluation
        review_mins = max(15, int(total_mins * 0.20))
        concept_mins = max(20, int(total_mins * 0.40))
        practice_mins = max(15, int(total_mins * 0.25))
        explain_mins = max(10, total_mins - (review_mins + concept_mins + practice_mins))

        return {
            "total_minutes": total_mins,
            "hours_per_day": hours_per_day,
            "focus_topic": topic_name,
            "schedule": [
                {
                    "step": 1,
                    "title": f"Review & Prerequisites",
                    "duration_mins": review_mins,
                    "description": f"Quick 15-30 min revision of prerequisite concepts for {topic_name}."
                },
                {
                    "step": 2,
                    "title": f"Core Learning: {topic_name}",
                    "duration_mins": concept_mins,
                    "description": f"Deep dive into fundamental concepts and patterns of {topic_name}."
                },
                {
                    "step": 3,
                    "title": "Hands-on Practice",
                    "duration_mins": practice_mins,
                    "description": "Solve 2-3 practical exercises or build a small code snippet."
                },
                {
                    "step": 4,
                    "title": "Reverse Learning Explanation",
                    "duration_mins": explain_mins,
                    "description": f"Explain {topic_name} in your own words in the Study Room to evaluate mastery."
                }
            ]
        }

    @staticmethod
    def get_current_focus(db: Session, user_id: int) -> dict:
        data = RoadmapService.get_my_roadmap(db, user_id)
        if not data or not data.get("current_focus"):
            return None
        return {
            "target_role": data.get("target_role"),
            "current_focus": data.get("current_focus"),
            "daily_plan": data.get("daily_plan")
        }

    @staticmethod
    def get_roadmap_history(db: Session, user_id: int) -> list:
        data = RoadmapService.get_my_roadmap(db, user_id)
        if not data:
            return []
        return data.get("history", [])

    @staticmethod
    async def update_preferences(db: Session, user_id: int, preferences: dict) -> dict:
        """
        Updates profile preferences. If target_role changes, regenerates roadmap.
        Otherwise recalculates workload and daily plan.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        old_role = user.target_role
        new_role = preferences.get("target_role") or old_role
        
        user.target_role = new_role
        if "hours_per_day" in preferences:
            user.hours_per_day = float(preferences["hours_per_day"])
        if "days_per_week" in preferences:
            user.days_per_week = int(preferences["days_per_week"])
        if "career_goal" in preferences:
            user.learning_goals = preferences["career_goal"]
        if "experience_level" in preferences:
            user.experience_level = preferences["experience_level"]
        if "preferred_areas" in preferences:
            user.preferred_areas = json.dumps(preferences["preferred_areas"])

        db.commit()

        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.status == "active").first()
        if roadmap:
            roadmap.hours_per_day = user.hours_per_day
            roadmap.days_per_week = user.days_per_week
            roadmap.career_goal = user.learning_goals
            roadmap.experience_level = user.experience_level
            roadmap.preferred_areas = user.preferred_areas
            db.commit()

        # If target role changed, re-generate full roadmap
        if old_role != new_role:
            return await RoadmapService.generate_initial_roadmap(db, user, {
                "target_role": new_role,
                "experience_level": user.experience_level,
                "career_goal": user.learning_goals,
                "hours_per_day": user.hours_per_day,
                "days_per_week": user.days_per_week,
                "current_skills": json.loads(user.current_skills or "[]"),
                "preferred_areas": json.loads(user.preferred_areas or "[]")
            })

        # Recalculate
        return RoadmapService.recalculate_roadmap(db, user_id)
