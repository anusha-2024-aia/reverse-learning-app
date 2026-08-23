import os
import sys
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, Base, engine
from app import models
from app.services.smart_revision_service import (
    SmartRevisionService,
    LOW_MASTERY_INTERVAL,
    MEDIUM_MASTERY_INTERVAL,
    GOOD_MASTERY_INTERVAL,
    HIGH_MASTERY_INTERVAL
)

def run_tests():
    print("--- STARTING PHASE 6 REVISION ENGINE TESTS ---")
    
    # 1. Test Centralized Rule-Based Intervals
    assert SmartRevisionService.calculate_revision_interval(52.0) == 1, "Failed Case 1: 52% -> 1 day"
    assert SmartRevisionService.calculate_revision_interval(68.0) == 3, "Failed Case 2: 68% -> 3 days"
    assert SmartRevisionService.calculate_revision_interval(81.0) == 7, "Failed Case 3: 81% -> 7 days"
    assert SmartRevisionService.calculate_revision_interval(92.0) == 14, "Failed Case 4: 92% -> 14 days"
    print("Test 1: Centralized Rule Intervals PASSED.")

    # 2. Test Dynamic Status Determination
    now = datetime.now(timezone.utc)
    today = now.date()
    
    assert SmartRevisionService.get_dynamic_status(now) == "DUE", "Failed today -> DUE"
    assert SmartRevisionService.get_dynamic_status(now - timedelta(days=1)) == "OVERDUE", "Failed past -> OVERDUE"
    assert SmartRevisionService.get_dynamic_status(now + timedelta(days=2)) == "UPCOMING", "Failed future -> UPCOMING"
    print("Test 2: Dynamic Status Determination PASSED.")

    # 3. Test Database Integration & Revision Updating
    db = SessionLocal()
    try:
        # Create test users
        user_a = db.query(models.User).filter(models.User.email == "test_rev_a@example.com").first()
        if not user_a:
            user_a = models.User(username="test_rev_a", email="test_rev_a@example.com", password_hash="hash")
            db.add(user_a)
            db.commit()
            db.refresh(user_a)

        user_b = db.query(models.User).filter(models.User.email == "test_rev_b@example.com").first()
        if not user_b:
            user_b = models.User(username="test_rev_b", email="test_rev_b@example.com", password_hash="hash")
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        # Get a test topic
        topic = db.query(models.Topic).first()
        assert topic is not None, "No topic found in DB to test"

        # Update User A's revision schedule with 52%
        sched_a = SmartRevisionService.update_revision_schedule(db, user_a.id, topic.id, 52.0)
        assert sched_a.current_mastery_score == 52.0, "Failed to save mastery score 52%"
        assert sched_a.status in ["DUE", "UPCOMING", "OVERDUE"], "Status missing"
        
        # Test performance drop: 90% -> 55%
        sched_a_high = SmartRevisionService.update_revision_schedule(db, user_a.id, topic.id, 90.0)
        assert sched_a_high.last_mastery_score == 52.0, "Failed last_mastery_score tracking"
        assert sched_a_high.current_mastery_score == 90.0, "Failed current_mastery_score tracking"

        sched_a_drop = SmartRevisionService.update_revision_schedule(db, user_a.id, topic.id, 55.0)
        assert sched_a_drop.last_mastery_score == 90.0, "Failed tracking previous mastery"
        assert sched_a_drop.current_mastery_score == 55.0, "Failed drop to 55%"
        interval = SmartRevisionService.calculate_revision_interval(sched_a_drop.current_mastery_score)
        assert interval == 1, "Failed performance drop interval calculation"
        print("Test 3: Revision updating and performance drop PASSED.")

        # 4. Test User Isolation
        data_a = SmartRevisionService.get_user_revisions(db, user_a.id)
        data_b = SmartRevisionService.get_user_revisions(db, user_b.id)

        # User B should NOT see User A's scheduled items
        assert any(item["topic_id"] == topic.id for item in (data_a["due_today"] + data_a["overdue"] + data_a["tomorrow"] + data_a["upcoming"])), "User A schedule missing"
        assert not any(item["topic_id"] == topic.id for item in (data_b["due_today"] + data_b["overdue"] + data_b["tomorrow"] + data_b["upcoming"])), "User Isolation Failed: User B saw User A data!"
        print("Test 4: User Isolation PASSED.")

        print("--- ALL PHASE 6 REVISION TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
