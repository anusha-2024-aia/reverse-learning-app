import sys
import os

# Add backend directory to sys.path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def migrate():
    print("Creating adaptive_recommendations table...")
    # This will create tables that don't exist yet
    Base.metadata.create_all(bind=engine)
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
