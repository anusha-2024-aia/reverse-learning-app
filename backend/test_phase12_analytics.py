import sys
import os
import uuid
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models, auth

def run_phase12_analytics_tests():
    print("==================================================")
    print("STARTING PHASE 12 ANALYTICS & USER ISOLATION TESTS")
    print("==================================================")

    client = TestClient(app)

    # 1. Register User A
    email_a = f"sec_user_a_{uuid.uuid4().hex[:6]}@example.com"
    res_reg_a = client.post("/api/auth/register", json={
        "name": "Analytics User A",
        "email": email_a,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert res_reg_a.status_code == 200, f"User A registration failed: {res_reg_a.text}"
    token_a = res_reg_a.json()["access_token"]
    user_a_id = res_reg_a.json()["user_id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("[OK] Registered User A successfully")

    # 2. Register User B
    email_b = f"sec_user_b_{uuid.uuid4().hex[:6]}@example.com"
    res_reg_b = client.post("/api/auth/register", json={
        "name": "Analytics User B",
        "email": email_b,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert res_reg_b.status_code == 200, f"User B registration failed: {res_reg_b.text}"
    token_b = res_reg_b.json()["access_token"]
    user_b_id = res_reg_b.json()["user_id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("[OK] Registered User B successfully")

    # -------------------------------------------------------------
    # 3. Test Empty State (Brand New User B)
    # -------------------------------------------------------------
    res_empty_b = client.get("/api/analytics?range=30d", headers=headers_b)
    assert res_empty_b.status_code == 200, f"Analytics call for new user failed: {res_empty_b.text}"
    data_empty = res_empty_b.json()
    print("DEBUG data_empty:", data_empty)
    assert data_empty["has_enough_data"] is False, "New user with 0 evaluations must have has_enough_data == False"
    assert data_empty["summary"]["overallScore"] == 0
    print("[OK] Empty state verified for brand new User B (has_enough_data == False)")

    # -------------------------------------------------------------
    # 4. Populate User A with Rich Learning Data
    # -------------------------------------------------------------
    db = next(get_db())
    topic = db.query(models.Topic).first()
    if not topic:
        topic = models.Topic(name="Binary Search", category="Data Structures & Algorithms", description="Binary search algorithm")
        db.add(topic)
        db.commit()
        db.refresh(topic)
    topic_id = topic.id

    # Add Evaluation for User A
    res_eval_a = client.post("/api/evaluate", headers=headers_a, json={
        "topic_id": topic_id,
        "explanation": "Binary search works by dividing sorted array in half repeatedly.",
        "learning_mode": "EXPLAIN"
    })
    assert res_eval_a.status_code == 200, f"User A evaluation failed: {res_eval_a.text}"

    # Add Interview for User A
    res_int_a = client.post("/api/interview/start", headers=headers_a, json={
        "target_role": "Backend Engineer",
        "difficulty": "MEDIUM",
        "question_count": 5
    })
    assert res_int_a.status_code == 200, f"User A interview start failed: {res_int_a.text}"

    # Add Communication Analysis for User A
    res_comm_a = client.post("/api/communication/analyze", headers=headers_a, json={
        "transcript": "Um, basically binary search operates in log n time complexity, you know.",
        "duration_seconds": 25
    })
    assert res_comm_a.status_code == 200, f"User A communication analysis failed: {res_comm_a.text}"
    print("[OK] Populated User A with evaluations, interviews, and communication records")

    # -------------------------------------------------------------
    # 5. Verify User A Analytics Endpoint
    # -------------------------------------------------------------
    res_analytics_a = client.get("/api/analytics?range=30d", headers=headers_a)
    assert res_analytics_a.status_code == 200, f"User A analytics failed: {res_analytics_a.text}"
    data_a = res_analytics_a.json()
    assert data_a["has_enough_data"] is True, "User A with evaluation data must have has_enough_data == True"
    assert len(data_a["scoreTrend"]) > 0, "User A score trend must contain data points"
    assert "summary" in data_a and "technicalMastery" in data_a["summary"]
    assert "recommendedNextAction" in data_a
    assert "aiInsight" in data_a
    print("[OK] User A Analytics payload contains real non-empty aggregated data")

    # -------------------------------------------------------------
    # 6. Test Date Range Filtering (7d, 30d, 90d, 6m, all)
    # -------------------------------------------------------------
    for r in ["7d", "30d", "90d", "6m", "all"]:
        res_r = client.get(f"/api/analytics?range={r}", headers=headers_a)
        assert res_r.status_code == 200, f"Range {r} call failed: {res_r.text}"
        assert res_r.json()["range"] == r
    print("[OK] Date range filter query parameters (7d, 30d, 90d, 6m, all) work properly")

    # -------------------------------------------------------------
    # 7. MANDATORY SECURITY TEST: USER A -> USER B ISOLATION
    # -------------------------------------------------------------
    res_analytics_b = client.get("/api/analytics?range=30d", headers=headers_b)
    assert res_analytics_b.status_code == 200
    data_b = res_analytics_b.json()
    assert data_b["has_enough_data"] is False, "User B must NOT see User A's data! (User B has 0 evaluations)"
    assert len(data_b["scoreTrend"]) == 0, "User B score trend must be empty"
    print("[OK] USER ISOLATION VERIFIED: User B analytics is completely isolated from User A data")

    # Parameter Manipulation / Unauthenticated Access Checks
    res_no_auth = client.get("/api/analytics?range=30d")
    assert res_no_auth.status_code == 401, "Unauthenticated analytics request must be rejected with 401"
    print("[OK] Unauthenticated request rejected with 401 Unauthorized")

    # Parameter injection attempt: /api/analytics?userId=1
    res_inject = client.get(f"/api/analytics?userId={user_a_id}", headers=headers_b)
    assert res_inject.status_code == 200
    assert res_inject.json()["has_enough_data"] is False, "Backend must ignore query parameter userId overrides and strictly use JWT identity!"
    print("[OK] Parameter injection attempt (userId parameter override) safely ignored by JWT auth middleware")

    print("\n==================================================")
    print("ALL PHASE 12 ANALYTICS & USER ISOLATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_phase12_analytics_tests()
