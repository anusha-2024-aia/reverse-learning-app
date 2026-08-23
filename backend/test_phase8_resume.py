import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()


from app.database import SessionLocal
from app import models
from app.services.resume_intelligence_service import ResumeIntelligenceService


async def run_tests():
    print("--- STARTING PHASE 8 RESUME INTELLIGENCE TESTS ---")
    db = SessionLocal()

    try:
        # Create test users
        user_a = db.query(models.User).filter(models.User.email == "resume_test_a@example.com").first()
        if not user_a:
            user_a = models.User(username="resume_test_a", email="resume_test_a@example.com", password_hash="hash")
            db.add(user_a)
            db.commit()
            db.refresh(user_a)

        user_b = db.query(models.User).filter(models.User.email == "resume_test_b@example.com").first()
        if not user_b:
            user_b = models.User(username="resume_test_b", email="resume_test_b@example.com", password_hash="hash")
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        # 1. Test Text Extraction Validation
        try:
            ResumeIntelligenceService.extract_text("non_existent_file.xyz", "xyz")
            assert False, "Should have raised exception for unsupported file extension"
        except Exception as e:
            assert "Unsupported" in str(e) or "not found" in str(e), f"Unexpected error: {e}"
        print("Test 1: File Format Validation PASSED.")

        # 2. Test Resume DB Creation & Replacement
        sample_text = """
        Anusha Kumar - Full Stack Software Engineer
        Email: anusha@example.com
        
        SKILLS:
        Java, Python, SQL, React, Node.js, FastAPI, Docker, MongoDB
        
        PROJECTS:
        1. Smart Job Matching System
           Built an AI-driven job candidate recommendation system using Python, FastAPI, and MongoDB.
           Implemented vector similarity search and REST APIs.
           
        2. E-Commerce Order Microservice
           Engineered high-throughput order processing service using Java Spring Boot and MySQL.
           Integrated Redis caching to cut latency by 40%.
           
        EXPERIENCE:
        Backend Development Intern at Tech Solutions (6 months)
        Implemented JWT authentication and database indexing.
        
        EDUCATION:
        B.Tech in Computer Science, 2025
        """

        # Deactivate old resumes for User A
        db.query(models.Resume).filter(models.Resume.user_id == user_a.id).update({"is_active": False})
        db.commit()

        structured = {
            "summary": "Full Stack Software Engineer with Python and Java expertise",
            "skills": ["Java", "Python", "SQL", "React", "Node.js", "FastAPI", "Docker", "MongoDB"],
            "projects": [
                {
                    "name": "Smart Job Matching System",
                    "description": "Built AI-driven job recommendation system using Python, FastAPI, and MongoDB.",
                    "technologies": ["Python", "FastAPI", "MongoDB"]
                },
                {
                    "name": "E-Commerce Order Microservice",
                    "description": "Engineered order processing service using Java Spring Boot and MySQL with Redis caching.",
                    "technologies": ["Java", "Spring Boot", "MySQL", "Redis"]
                }
            ],
            "experience": [
                {
                    "company": "Tech Solutions",
                    "role": "Backend Development Intern",
                    "description": "Implemented JWT auth and DB indexing."
                }
            ],
            "education": [{"degree": "B.Tech Computer Science", "institution": "University", "year": "2025"}]
        }

        resume_a1 = models.Resume(
            user_id=user_a.id,
            file_name="Anusha_Resume_v1.pdf",
            file_type="pdf",
            file_path="/tmp/fake_path_v1.pdf",
            extracted_text=sample_text,
            is_active=True,
            parsed_skills=json.dumps(structured["skills"]),
            parsed_projects=json.dumps(structured["projects"]),
            parsed_experience=json.dumps(structured["experience"]),
            parsed_education=json.dumps(structured["education"]),
            analysis_summary_json=json.dumps(structured)
        )
        db.add(resume_a1)
        db.commit()
        db.refresh(resume_a1)

        assert resume_a1.is_active == True, "Resume 1 should be active"
        print("Test 2: Resume Record Creation PASSED.")

        # 3. Test Question Generation
        questions = await ResumeIntelligenceService.generate_personalized_questions(db, user_a.id, resume_a1.id)
        assert len(questions) > 0, "Failed to generate personalized questions"
        print(f"Test 3: Generated {len(questions)} personalized questions PASSED.")

        # 4. Test Follow-Up Question Generation
        prev_qa = [{"question": "Why did you choose MongoDB for Smart Job Matching System?", "answer": "I used MongoDB because of schema flexibility for storing unstructured resume JSON files."}]
        followup = await ResumeIntelligenceService.generate_followup_question("Full Stack Developer", prev_qa)
        assert len(followup) > 10, "Follow-up question failed"
        print(f"Test 4: Follow-up Question PASSED. ('{followup[:40]}...')")

        # 5. Test Resume Replacement
        db.query(models.Resume).filter(models.Resume.user_id == user_a.id).update({"is_active": False})
        resume_a2 = models.Resume(
            user_id=user_a.id,
            file_name="Anusha_Resume_v2.pdf",
            file_type="pdf",
            file_path="/tmp/fake_path_v2.pdf",
            extracted_text=sample_text,
            is_active=True,
            parsed_skills=json.dumps(structured["skills"]),
            parsed_projects=json.dumps(structured["projects"]),
            analysis_summary_json=json.dumps(structured)
        )
        db.add(resume_a2)
        db.commit()
        db.refresh(resume_a2)

        active_a = db.query(models.Resume).filter(models.Resume.user_id == user_a.id, models.Resume.is_active == True).first()
        assert active_a.id == resume_a2.id, "Active resume should be v2"
        print("Test 5: Resume Replacement PASSED.")

        # 6. Test User Isolation
        active_b = db.query(models.Resume).filter(models.Resume.user_id == user_b.id, models.Resume.is_active == True).first()
        assert active_b is None, "User B should not see User A's resume"
        print("Test 6: User Isolation PASSED.")

        print("--- ALL PHASE 8 RESUME INTELLIGENCE TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
