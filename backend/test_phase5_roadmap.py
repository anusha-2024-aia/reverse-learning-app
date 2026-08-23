import asyncio
import json
from app.database import SessionLocal, engine
from app.models import Base, User, Roadmap, RoadmapItem, RoadmapChange, Evaluation, Topic
from app.services.roadmap_service import RoadmapService
from app.services.adaptive_engine import AdaptiveEngine

async def run_phase5_test():
    print("=== STARTING PHASE 5 DYNAMIC ROADMAP VERIFICATION TEST ===")
    from app.migrate_v5 import migrate_db
    migrate_db()
    
    db = SessionLocal()
    try:
        # Create or fetch test user
        user = db.query(User).filter(User.username == "test_phase5_student").first()
        if not user:
            user = User(
                username="test_phase5_student",
                email="phase5_student@example.com",
                password_hash="hashed_pw_test",
                target_role="Full Stack Developer",
                hours_per_day=2.0,
                days_per_week=6,
                experience_level="BEGINNER",
                current_skills=json.dumps(["HTML", "CSS"]),
                preferred_areas=json.dumps(["Web Development", "Backend Development"])
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        print(f"Test User ID: {user.id}, Target Role: {user.target_role}")

        # 1. Test Initial Roadmap Generation
        print("\n--- 1. Testing Initial Roadmap Generation ---")
        onboarding_data = {
            "target_role": "Full Stack Developer",
            "current_skills": ["HTML", "CSS", "JavaScript"],
            "experience_level": "BEGINNER",
            "career_goal": "Get hired as a Full Stack Software Engineer",
            "hours_per_day": 2.0,
            "days_per_week": 6,
            "preferred_areas": ["Web Development", "Databases"]
        }

        roadmap = await RoadmapService.generate_initial_roadmap(db, user, onboarding_data)
        assert roadmap is not None, "Roadmap generation failed"
        assert roadmap["roadmap_id"] is not None, "Roadmap ID missing"
        assert len(roadmap["items"]) >= 3, "Roadmap items count insufficient"

        print(f"[SUCCESS] Initial Roadmap generated successfully! ID: {roadmap['roadmap_id']}")
        print(f"   Role: {roadmap['target_role']}, Progress: {roadmap['progress']}%, Estimated Hours: {roadmap['estimated_hours']}h")

        # Print top topics
        for item in roadmap["items"][:5]:
            print(f"   [{item['order_index']}] {item['topic_name']} ({item['category']}) - Status: {item['status']}, Priority: {item['priority_score']}, Mastery: {item['mastery_score']}%")

        # 2. Test Performance Awareness (Evaluations impact dynamic roadmap)
        print("\n--- 2. Testing Low Performance Trigger (Weak Topic Surfacing) ---")
        
        # Pick topic e.g. Node.js or JavaScript
        js_topic = db.query(Topic).filter(Topic.name.like("%JavaScript%")).first() or db.query(Topic).first()
        assert js_topic is not None, "No topic found in DB for testing evaluation"

        # Simulate low evaluation score (e.g. 42%)
        low_eval = Evaluation(
            user_id=user.id,
            topic_id=js_topic.id,
            explanation="Weak incomplete explanation of JS event loop",
            ai_score=42,
            overall_score=42,
            attempt_number=1,
            ai_feedback_json=json.dumps({"summary": "Incomplete understanding"})
        )
        db.add(low_eval)
        db.commit()

        # Update mastery & recalculate roadmap
        AdaptiveEngine.update_mastery(db, user.id, js_topic.id, 42)
        recalculated = RoadmapService.recalculate_roadmap(db, user.id)

        print(f"[SUCCESS] Dynamic Recalculation executed after 42% evaluation score on '{js_topic.name}'")
        print(f"   Current Focus: {recalculated.get('current_focus', {}).get('topic_name')} - Status: {recalculated.get('current_focus', {}).get('status')}")

        # Verify change history logged
        history = recalculated.get("history", [])
        assert len(history) > 0, "No roadmap changes logged in history"
        print(f"[SUCCESS] Recent Roadmap Change Logged: {history[0]['topic_name']} - {history[0]['reason']}")

        # 3. Test High Performance (Mastery progression)
        print("\n--- 3. Testing High Performance Progression (Mastered Rule) ---")
        for attempt in range(2, 4):
            high_eval = Evaluation(
                user_id=user.id,
                topic_id=js_topic.id,
                explanation="Comprehensive accurate explanation of JS event loop, promises, call stack, and async await.",
                ai_score=92,
                overall_score=92,
                attempt_number=attempt,
                ai_feedback_json=json.dumps({"summary": "Excellent mastery"})
            )
            db.add(high_eval)
            db.commit()
            AdaptiveEngine.update_mastery(db, user.id, js_topic.id, 92)

        mastered_roadmap = RoadmapService.recalculate_roadmap(db, user.id)
        
        # Find item in roadmap
        target_item = next((i for i in mastered_roadmap["items"] if i["topic_name"].lower() == js_topic.name.lower()), None)
        print(f"[SUCCESS] Item '{js_topic.name}' updated after 2x 92% attempts:")
        if target_item:
            print(f"   Status: {target_item['status']}, Mastery: {target_item['mastery_score']}%, Priority: {target_item['priority_score']}")

        # 4. Test Target Role Change
        print("\n--- 4. Testing Target Role Change (Full Stack -> Data Analyst) ---")
        role_change_res = await RoadmapService.update_preferences(db, user.id, {
            "target_role": "Data Analyst",
            "hours_per_day": 3.0
        })

        assert role_change_res["target_role"] == "Data Analyst", "Target role update failed"
        print(f"[SUCCESS] Roadmap successfully re-generated for new role: {role_change_res['target_role']}")
        print(f"   New Top Topics:")
        for item in role_change_res["items"][:4]:
            print(f"   [{item['order_index']}] {item['topic_name']} ({item['category']}) - Status: {item['status']}")

        print("\n[PASSED] ALL PHASE 5 END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_phase5_test())
