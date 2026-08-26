import os
import json
import asyncio
import time
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models, auth

client = TestClient(app)

def run_security_tests():
    print("==================================================")
    print("STARTING PHASE 11 SECURITY & USER ISOLATION TESTS")
    print("==================================================")

    db = SessionLocal()

    # Clean up existing test users if present
    db.query(models.User).filter(
        models.User.email.in_(["sec_user_a@example.com", "sec_user_b@example.com"])
    ).delete(synchronize_session=False)
    db.commit()

    try:
        # -------------------------------------------------------------
        # 1. USER REGISTRATION TESTS
        # -------------------------------------------------------------
        print("\n--- 1. Testing User Registration ---")
        
        # Valid Register User A
        res_reg_a = client.post("/api/auth/register", json={
            "name": "User A",
            "email": "sec_user_a@example.com",
            "password": "PasswordA123!",
            "confirm_password": "PasswordA123!"
        })
        assert res_reg_a.status_code == 200, f"User A registration failed: {res_reg_a.text}"
        data_a = res_reg_a.json()
        assert "access_token" in data_a, "Registration must return access_token"
        assert "password_hash" not in data_a, "Registration must never leak password_hash"
        user_a_id = data_a["user_id"]
        token_a = data_a["access_token"]
        print("[OK] User A registered successfully")

        # Valid Register User B
        res_reg_b = client.post("/api/auth/register", json={
            "name": "User B",
            "email": "sec_user_b@example.com",
            "password": "PasswordB123!",
            "confirm_password": "PasswordB123!"
        })
        assert res_reg_b.status_code == 200, f"User B registration failed: {res_reg_b.text}"
        data_b = res_reg_b.json()
        user_b_id = data_b["user_id"]
        token_b = data_b["access_token"]
        print("[OK] User B registered successfully")

        # Duplicate Email Rejection
        res_dup = client.post("/api/auth/register", json={
            "name": "User A Duplicate",
            "email": "sec_user_a@example.com",
            "password": "PasswordA123!",
            "confirm_password": "PasswordA123!"
        })
        assert res_dup.status_code == 400, "Duplicate email registration must be rejected"
        print("[OK] Duplicate email registration rejected properly")

        # Password Mismatch Rejection
        res_mismatch = client.post("/api/auth/register", json={
            "name": "User Bad",
            "email": "sec_bad@example.com",
            "password": "Password123!",
            "confirm_password": "WrongPassword!"
        })
        assert res_mismatch.status_code == 400, "Password mismatch registration must be rejected"
        print("[OK] Password mismatch registration rejected properly")

        # Short Password Rejection
        res_short = client.post("/api/auth/register", json={
            "name": "User Short",
            "email": "sec_short@example.com",
            "password": "123",
            "confirm_password": "123"
        })
        assert res_short.status_code == 400, "Short password registration must be rejected"
        print("[OK] Short password registration rejected properly")

        # -------------------------------------------------------------
        # 2. LOGIN & JWT SECURITY TESTS
        # -------------------------------------------------------------
        print("\n--- 2. Testing Login & Account Enumeration Protection ---")

        # Valid Login User A
        res_login_a = client.post("/api/auth/login", json={
            "email": "sec_user_a@example.com",
            "password": "PasswordA123!"
        })
        assert res_login_a.status_code == 200, f"Valid login failed: {res_login_a.text}"
        assert "access_token" in res_login_a.json()
        print("[OK] Login User A successful")

        # Invalid Password Login (Account Enumeration Check)
        res_bad_pass = client.post("/api/auth/login", json={
            "email": "sec_user_a@example.com",
            "password": "WrongPassword123!"
        })
        assert res_bad_pass.status_code == 401, "Invalid password login must return 401"
        assert res_bad_pass.json().get("detail") == "Invalid email or password.", f"Unexpected error detail: {res_bad_pass.json()}"
        print("[OK] Invalid password returns generic message ('Invalid email or password.')")

        # Non-existent Email Login (Account Enumeration Check)
        res_bad_email = client.post("/api/auth/login", json={
            "email": "nonexistent_sec_user@example.com",
            "password": "PasswordA123!"
        })
        assert res_bad_email.status_code == 401, "Non-existent email login must return 401"
        assert res_bad_email.json().get("detail") == "Invalid email or password."
        print("[OK] Non-existent email returns identical generic error message")

        # -------------------------------------------------------------
        # 3. AUTHENTICATION MIDDLEWARE & TOKEN VALIDATION TESTS
        # -------------------------------------------------------------
        print("\n--- 3. Testing Authentication Middleware ---")

        # Missing Token
        res_no_auth = client.get("/api/dashboard-data")
        assert res_no_auth.status_code == 401, f"Expected 401 for unauthenticated request, got {res_no_auth.status_code}"
        print("[OK] Request without token rejected with 401 Unauthorized")

        # Invalid Token
        res_bad_token = client.get("/api/dashboard-data", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert res_bad_token.status_code == 401, "Invalid token must be rejected with 401"
        print("[OK] Request with invalid token rejected with 401 Unauthorized")

        # Expired Token
        expired_token = auth.create_access_token(
            data={"sub": str(user_a_id)},
            expires_delta=timedelta(seconds=-10)
        )
        res_exp = client.get("/api/dashboard-data", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_exp.status_code == 401, "Expired token must be rejected with 401"
        print("[OK] Request with expired token rejected with 401 Unauthorized")

        # -------------------------------------------------------------
        # 4. MOST IMPORTANT SECURITY TEST: USER A -> USER B ISOLATION
        # -------------------------------------------------------------
        print("\n--- 4. Mandatory User A -> User B Isolation Test ---")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Step 4a: User B creates an Interview
        res_int_b = client.post("/api/interview/start", headers=headers_b, json={
            "target_role": "Backend Security Engineer",
            "interview_type": "technical",
            "difficulty": "MEDIUM",
            "question_count": 5
        })
        assert res_int_b.status_code == 200, f"User B interview creation failed: {res_int_b.text}"
        int_b_id = res_int_b.json()["interview_id"]
        q_b_id = res_int_b.json()["question_id"]
        print(f"[OK] User B created Interview ID {int_b_id}")

        # Step 4b: User B creates an Evaluation
        topic = db.query(models.Topic).first()
        topic_id = topic.id if topic else 1
        res_eval_b = client.post("/api/evaluate", headers=headers_b, json={
            "topic_id": topic_id,
            "explanation": "Binary search divides the search space in half at each step with O(log N) time complexity.",
            "learning_mode": "EXPLAIN"
        })
        assert res_eval_b.status_code == 200, f"User B evaluation failed: {res_eval_b.text}"
        eval_b_id = res_eval_b.json()["evaluation_id"]
        print(f"[OK] User B created Evaluation ID {eval_b_id}")

        # Step 4c: User B creates a Communication Analysis record
        res_comm_b = client.post("/api/communication/analyze", headers=headers_b, json={
            "transcript": "Um, basically we used PostgreSQL for ACID transactions and like reliability.",
            "question_text": "Why choose PostgreSQL?",
            "duration_seconds": 5.0
        })
        assert res_comm_b.status_code == 200, f"User B communication analysis failed: {res_comm_b.text}"
        comm_b_id = res_comm_b.json()["analysis_id"]
        print(f"[OK] User B created Communication Analysis ID {comm_b_id}")

        # Step 4d: USER A ATTEMPTS TO ACCESS USER B'S DATA (MUST ALL FAIL!)
        print("\nAttempting User A access to User B resources...")

        # User A -> GET User B's Interview Report
        res_cross_int = client.get(f"/api/interview/{int_b_id}/report", headers=headers_a)
        assert res_cross_int.status_code in [403, 404], f"User A accessed User B interview report! Status: {res_cross_int.status_code}"
        print(f"[OK] User A -> GET User B Interview {int_b_id} rejected with {res_cross_int.status_code}")

        # User A -> Answer User B's Interview Question
        res_cross_ans = client.post("/api/interview/answer", headers=headers_a, json={
            "interview_id": int_b_id,
            "current_question_id": q_b_id,
            "answer": "Unauthorized answer attempt by User A"
        })
        assert res_cross_ans.status_code in [403, 404], f"User A answered User B interview! Status: {res_cross_ans.status_code}"
        print(f"[OK] User A -> POST Answer on User B Interview rejected with {res_cross_ans.status_code}")

        # User A -> GET User B's Evaluation
        res_cross_eval = client.get(f"/api/evaluations/{eval_b_id}", headers=headers_a)
        assert res_cross_eval.status_code in [403, 404], f"User A accessed User B evaluation! Status: {res_cross_eval.status_code}"
        print(f"[OK] User A -> GET User B Evaluation {eval_b_id} rejected with {res_cross_eval.status_code}")

        # User A -> GET User B's Communication Analysis
        res_cross_comm = client.get(f"/api/communication/analysis/{comm_b_id}", headers=headers_a)
        assert res_cross_comm.status_code in [403, 404], f"User A accessed User B communication analysis! Status: {res_cross_comm.status_code}"
        print(f"[OK] User A -> GET User B Communication Analysis {comm_b_id} rejected with {res_cross_comm.status_code}")

        # Step 4e: Verify Dashboard Data Separation
        res_dash_a = client.get("/api/dashboard-data", headers=headers_a)
        assert res_dash_a.status_code == 200
        dash_a = res_dash_a.json()
        assert dash_a["user"]["name"] == "User A"
        assert len(dash_a["recentActivity"]) == 0, "User A must not see User B's recent activity"
        print("[OK] User A Dashboard contains ONLY User A data")

        res_dash_b = client.get("/api/dashboard-data", headers=headers_b)
        assert res_dash_b.status_code == 200
        dash_b = res_dash_b.json()
        assert dash_b["user"]["name"] == "User B"
        assert len(dash_b["recentActivity"]) > 0, "User B should see their own activity"
        print("[OK] User B Dashboard contains User B data")

        # -------------------------------------------------------------
        # 5. FILE UPLOAD SECURITY TESTS
        # -------------------------------------------------------------
        print("\n--- 5. Testing File Upload Security ---")

        # Valid PDF Upload
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
            b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj\n"
            b"4 0 obj <</Length 55>> stream\n"
            b"BT /F1 12 Tf 100 700 Td (Software Engineer Resume Content) Tj ET\n"
            b"endstream\n"
            b"endobj\n"
            b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \n0000000212 00000 n \n"
            b"trailer <</Size 5 /Root 1 0 R>>\n"
            b"startxref\n318\n%%EOF\n"
        )
        res_pdf = client.post("/api/resume/upload", headers=headers_a, files={"file": ("resume.pdf", pdf_content, "application/pdf")})
        assert res_pdf.status_code == 200, f"Valid PDF upload failed: {res_pdf.text}"
        res_id_a = res_pdf.json()["resume_id"]
        print(f"[OK] Valid PDF uploaded successfully (Resume ID {res_id_a})")

        # User B tries to access User A's Resume by ID
        res_cross_res = client.get(f"/api/resume/{res_id_a}", headers=headers_b)
        assert res_cross_res.status_code in [403, 404], f"User B accessed User A resume! Status: {res_cross_res.status_code}"
        print(f"[OK] User B -> GET User A Resume {res_id_a} rejected with {res_cross_res.status_code}")

        # Invalid Executable (.exe) Upload Rejection
        exe_content = b"MZ\x90\x00\x03\x00\x00\x00Fake Windows Executable Payload"
        res_exe = client.post("/api/resume/upload", headers=headers_a, files={"file": ("malicious.exe", exe_content, "application/x-msdownload")})
        assert res_exe.status_code == 400, "Executable file upload must be rejected"
        print("[OK] Malicious .exe file upload rejected with 400")

        # Invalid JS Upload Rejection
        js_content = b"console.log('malicious script');"
        res_js = client.post("/api/resume/upload", headers=headers_a, files={"file": ("script.js", js_content, "application/javascript")})
        assert res_js.status_code == 400, "JS file upload must be rejected"
        print("[OK] Malicious .js file upload rejected with 400")

        # Oversized File (>10MB) Rejection
        big_content = b"0" * (11 * 1024 * 1024) # 11 MB
        res_big = client.post("/api/resume/upload", headers=headers_a, files={"file": ("huge.pdf", big_content, "application/pdf")})
        assert res_big.status_code == 400, "Oversized file upload (>10MB) must be rejected"
        print("[OK] Oversized file (>10MB) upload rejected with 400")

        # Path Traversal Filename Test
        trav_content = pdf_content
        res_trav = client.post("/api/resume/upload", headers=headers_a, files={"file": ("../../etc/passwd.pdf", trav_content, "application/pdf")})
        assert res_trav.status_code == 200, f"Path traversal filename should be sanitized safely: {res_trav.text}"
        assert "../../" not in res_trav.json().get("file_name", ""), "Path traversal characters must be stripped"
        print("[OK] Path traversal filename safely sanitized")

        # -------------------------------------------------------------
        # 6. SECURITY HEADERS & SECRET EXPOSURE AUDIT
        # -------------------------------------------------------------
        print("\n--- 6. Security Headers & Secret Exposure Audit ---")

        res_me = client.get("/api/auth/me", headers=headers_a)
        headers_resp = res_me.headers
        assert headers_resp.get("X-Content-Type-Options") == "nosniff", "Missing X-Content-Type-Options header"
        assert headers_resp.get("X-Frame-Options") == "DENY", "Missing X-Frame-Options header"
        assert "password_hash" not in res_me.text, "password_hash must never be present in user response"
        assert "JWT_SECRET" not in res_me.text and "GEMINI_API_KEY" not in res_me.text, "Backend secrets must never be present in responses"
        print("[OK] Security headers present & backend secrets completely omitted from API outputs")

        print("\n==================================================")
        print("ALL PHASE 11 SECURITY & USER ISOLATION TESTS PASSED!")
        print("==================================================")

    finally:
        # Cleanup test users
        db.query(models.User).filter(
            models.User.email.in_(["sec_user_a@example.com", "sec_user_b@example.com"])
        ).delete(synchronize_session=False)
        db.commit()
        db.close()

if __name__ == "__main__":
    run_security_tests()
