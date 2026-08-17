import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from app.database import SessionLocal
from app.models import Curriculum, Topic

def check_db():
    print(f"Connecting to: {os.getenv('DATABASE_URL')}")
    try:
        db = SessionLocal()
        curr_count = db.query(Curriculum).count()
        topic_count = db.query(Topic).count()
        print(f"SUCCESS! Connection established.")
        print(f"Found {curr_count} Curriculums in Supabase.")
        print(f"Found {topic_count} Topics in Supabase.")
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
