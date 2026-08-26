import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

TEST_DB_PATH = os.path.join(backend_dir, "test_study.db")
test_db_url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{TEST_DB_PATH}").strip()
if test_db_url.startswith("postgres://"):
    test_db_url = test_db_url.replace("postgres://", "postgresql://", 1)

TEST_SQLALCHEMY_DATABASE_URL = test_db_url

test_connect_args = {"check_same_thread": False} if TEST_SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args=test_connect_args
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def init_test_db():
    from app.models import Base
    from app.main import app
    from app.database import get_db
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = get_test_db

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def cleanup_test_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception as e:
            print(f"Test DB cleanup note: {e}")
