import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine

def migrate():
    print("Migrating evaluations table for Multi-Dimensional Evaluation 2.0...")
    new_columns = [
        ("overall_score", "INTEGER"),
        ("technical_score", "INTEGER"),
        ("concept_score", "INTEGER"),
        ("completeness_score", "INTEGER"),
        ("examples_score", "INTEGER"),
        ("relevance_score", "INTEGER"),
        ("communication_score", "INTEGER"),
        ("grammar_score", "INTEGER"),
        ("vocabulary_score", "INTEGER"),
        ("attempt_number", "INTEGER DEFAULT 1"),
        ("ai_insight", "TEXT")
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            try:
                conn.execute(text(f"ALTER TABLE evaluations ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Added column: {col_name}")
            except Exception as e:
                print(f"Column {col_name} already exists or error: {e}")
                
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
