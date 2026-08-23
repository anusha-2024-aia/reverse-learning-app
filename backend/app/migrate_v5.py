import sqlite3
import os
from sqlalchemy import inspect
from app.database import engine
from app import models

def migrate_db():
    print("Checking database tables & columns for Phase 5 migration...")
    
    # 1. Ensure SQLAlchemy metadata creates all tables including roadmap_changes
    models.Base.metadata.create_all(bind=engine)

    # 2. Add columns to existing SQLite tables if missing
    db_path = "./study.db"
    if not os.path.exists(db_path):
        db_path = "./sql_app.db"
        
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure roadmap_changes table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            change_type VARCHAR NOT NULL,
            topic_name VARCHAR,
            old_position INTEGER,
            new_position INTEGER,
            reason TEXT,
            created_at DATETIME,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        conn.commit()

        # Ensure revision_schedules table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS revision_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            last_mastery_score REAL DEFAULT 0.0,
            current_mastery_score REAL DEFAULT 0.0,
            last_reviewed_at DATETIME,
            next_review_at DATETIME,
            review_count INTEGER DEFAULT 0,
            status VARCHAR DEFAULT 'UPCOMING',
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
        """)
        conn.commit()


        # Helper to add column safely

        def add_column_if_missing(table, col_name, col_type):
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [info[1] for info in cursor.fetchall()]
                if col_name not in cols:
                    print(f"Adding column '{col_name}' to '{table}'...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    conn.commit()
            except Exception as e:
                print(f"Column migration warning for {table}.{col_name}: {e}")
                
        # Users table
        add_column_if_missing("users", "hours_per_day", "REAL DEFAULT 2.0")
        add_column_if_missing("users", "days_per_week", "INTEGER DEFAULT 6")
        add_column_if_missing("users", "experience_level", "VARCHAR DEFAULT 'BEGINNER'")
        add_column_if_missing("users", "current_skills", "TEXT")
        add_column_if_missing("users", "preferred_areas", "TEXT")
        add_column_if_missing("users", "onboarding_completed", "BOOLEAN DEFAULT 0")

        # Roadmaps table
        add_column_if_missing("roadmaps", "career_goal", "TEXT")
        add_column_if_missing("roadmaps", "experience_level", "VARCHAR")
        add_column_if_missing("roadmaps", "hours_per_day", "REAL DEFAULT 2.0")
        add_column_if_missing("roadmaps", "days_per_week", "INTEGER DEFAULT 6")
        add_column_if_missing("roadmaps", "preferred_areas", "TEXT")
        add_column_if_missing("roadmaps", "version", "INTEGER DEFAULT 1")
        add_column_if_missing("roadmaps", "progress", "REAL DEFAULT 0.0")
        add_column_if_missing("roadmaps", "estimated_hours", "INTEGER DEFAULT 0")

        # RoadmapItems table
        add_column_if_missing("roadmap_items", "user_id", "INTEGER")
        add_column_if_missing("roadmap_items", "category", "VARCHAR")
        add_column_if_missing("roadmap_items", "description", "TEXT")
        add_column_if_missing("roadmap_items", "importance", "VARCHAR DEFAULT 'HIGH'")
        add_column_if_missing("roadmap_items", "prerequisites", "TEXT")
        add_column_if_missing("roadmap_items", "estimated_hours", "INTEGER DEFAULT 10")
        add_column_if_missing("roadmap_items", "mastery_score", "REAL DEFAULT 0.0")
        add_column_if_missing("roadmap_items", "priority_score", "REAL DEFAULT 0.0")
        add_column_if_missing("roadmap_items", "reason", "TEXT")
        add_column_if_missing("roadmap_items", "skills_gained", "TEXT")
        add_column_if_missing("roadmap_items", "topic_id", "INTEGER")
        add_column_if_missing("roadmap_items", "last_evaluated_at", "DATETIME")
        add_column_if_missing("roadmap_items", "started_at", "DATETIME")
        add_column_if_missing("roadmap_items", "completed_at", "DATETIME")
        add_column_if_missing("roadmap_items", "created_at", "DATETIME")
        add_column_if_missing("roadmap_items", "updated_at", "DATETIME")

        # Resumes table columns
        add_column_if_missing("resumes", "file_name", "VARCHAR")
        add_column_if_missing("resumes", "file_type", "VARCHAR")
        add_column_if_missing("resumes", "extracted_text", "TEXT")
        add_column_if_missing("resumes", "is_active", "BOOLEAN DEFAULT 1")
        add_column_if_missing("resumes", "parsed_education", "TEXT")
        add_column_if_missing("resumes", "parsed_certifications", "TEXT")
        add_column_if_missing("resumes", "analysis_summary_json", "TEXT")
        add_column_if_missing("resumes", "updated_at", "DATETIME")

        # Ensure resume_questions table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            category VARCHAR NOT NULL,
            question_text TEXT NOT NULL,
            difficulty VARCHAR DEFAULT 'Medium',
            target_project_or_skill VARCHAR,
            created_at DATETIME,
            FOREIGN KEY (resume_id) REFERENCES resumes (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        conn.commit()

        # Ensure resume_interviews table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            overall_score INTEGER,
            technical_score INTEGER,
            project_knowledge_score INTEGER,
            communication_score INTEGER,
            problem_solving_score INTEGER,
            resume_understanding_score INTEGER,
            feedback_json TEXT,
            status VARCHAR DEFAULT 'IN_PROGRESS',
            created_at DATETIME,
            completed_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (resume_id) REFERENCES resumes (id)
        )
        """)
        conn.commit()

        # Phase 9: Interviews Table Columns
        add_column_if_missing("interviews", "resume_id", "INTEGER")
        add_column_if_missing("interviews", "starting_difficulty", "VARCHAR DEFAULT 'MEDIUM'")
        add_column_if_missing("interviews", "current_difficulty", "VARCHAR DEFAULT 'MEDIUM'")
        add_column_if_missing("interviews", "question_count", "INTEGER DEFAULT 10")
        add_column_if_missing("interviews", "current_question_number", "INTEGER DEFAULT 1")
        add_column_if_missing("interviews", "status", "VARCHAR DEFAULT 'IN_PROGRESS'")
        add_column_if_missing("interviews", "project_knowledge_score", "INTEGER")
        add_column_if_missing("interviews", "problem_solving_score", "INTEGER")
        add_column_if_missing("interviews", "started_at", "DATETIME")
        add_column_if_missing("interviews", "completed_at", "DATETIME")

        # Phase 9: InterviewQuestions Table Columns
        add_column_if_missing("interview_questions", "question_number", "INTEGER DEFAULT 1")
        add_column_if_missing("interview_questions", "difficulty", "VARCHAR DEFAULT 'MEDIUM'")
        add_column_if_missing("interview_questions", "is_followup", "BOOLEAN DEFAULT 0")
        add_column_if_missing("interview_questions", "topic", "VARCHAR")
        add_column_if_missing("interview_questions", "source", "VARCHAR")
        add_column_if_missing("interview_questions", "created_at", "DATETIME")

        # Phase 9: InterviewAnswers Table Columns
        add_column_if_missing("interview_answers", "technical_score", "INTEGER")
        add_column_if_missing("interview_answers", "communication_score", "INTEGER")
        add_column_if_missing("interview_answers", "completeness_score", "INTEGER")
        add_column_if_missing("interview_answers", "relevance_score", "INTEGER")
        add_column_if_missing("interview_answers", "overall_score", "INTEGER")
        add_column_if_missing("interview_answers", "created_at", "DATETIME")

        # Phase 10: Communication Analyses Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS communication_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interview_id INTEGER,
            answer_id INTEGER,
            communication_score INTEGER NOT NULL DEFAULT 70,
            clarity_score INTEGER NOT NULL DEFAULT 70,
            grammar_score INTEGER NOT NULL DEFAULT 70,
            vocabulary_score INTEGER NOT NULL DEFAULT 70,
            structure_score INTEGER NOT NULL DEFAULT 70,
            speaking_pace VARCHAR DEFAULT 'Good',
            words_per_minute INTEGER,
            pause_count INTEGER,
            filler_word_count INTEGER DEFAULT 0,
            filler_words_json TEXT,
            grammar_feedback TEXT,
            grammar_improvements_json TEXT,
            vocabulary_feedback TEXT,
            clarity_feedback TEXT,
            structure_feedback TEXT,
            ai_coach_recommendation TEXT,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (interview_id) REFERENCES interviews (id),
            FOREIGN KEY (answer_id) REFERENCES interview_answers (id)
        )
        """)
        conn.commit()

        conn.close()
        print("Phase 10 database migration completed successfully.")

if __name__ == "__main__":
    migrate_db()

