import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url

load_dotenv(override=True)

def normalize_database_url(url_str: str) -> str:
    if not url_str:
        return url_str
    url_str = url_str.strip()
    
    # 1. Normalize legacy postgres:// connection URLs to postgresql:// for SQLAlchemy compatibility
    if url_str.startswith("postgres://"):
        url_str = "postgresql://" + url_str[len("postgres://"):]
        
    # 2. Normalize PostgreSQL credentials if special characters (like '@') in password are unencoded
    if url_str.startswith("postgresql://"):
        prefix = "postgresql://"
        rest = url_str[len(prefix):]
        if "@" in rest:
            last_at = rest.rfind("@")
            user_pass = rest[:last_at]
            host_db = rest[last_at + 1:]
            if ":" in user_pass:
                user, password = user_pass.split(":", 1)
                decoded_password = urllib.parse.unquote(password)
                encoded_pass = urllib.parse.quote(decoded_password, safe="")
                return f"{prefix}{user}:{encoded_pass}@{host_db}"
    return url_str

raw_database_url = os.getenv("DATABASE_URL", "sqlite:///./study.db").strip()
SQLALCHEMY_DATABASE_URL = normalize_database_url(raw_database_url)

# Configure database options conditionally based on database engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }
else:
    engine_kwargs = {
        "connect_args": {},
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


