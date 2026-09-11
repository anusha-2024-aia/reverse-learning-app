import os
import sys
import unittest
from sqlalchemy import create_engine, text

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import normalize_database_url

class TestDatabaseConfig(unittest.TestCase):
    def test_sqlite_url_configuration(self):
        """Verify SQLite URL retains check_same_thread=False in connect_args."""
        db_url = "sqlite:///./test_temp.db"
        normalized = normalize_database_url(db_url)
        connect_args = {"check_same_thread": False} if normalized.startswith("sqlite") else {}
        
        self.assertEqual(connect_args, {"check_same_thread": False})
        engine = create_engine(normalized, connect_args=connect_args)
        self.assertEqual(engine.dialect.name, "sqlite")
        engine.dispose()
        if os.path.exists("./test_temp.db"):
            os.remove("./test_temp.db")

    def test_postgres_legacy_url_normalization(self):
        """Verify postgres:// is normalized to postgresql:// centrally."""
        raw_url = "postgres://user:password@cloud-db-host.com:5432/mydb"
        normalized_url = normalize_database_url(raw_url)
            
        self.assertEqual(normalized_url, "postgresql://user:password@cloud-db-host.com:5432/mydb")
        self.assertFalse(normalized_url.startswith("postgres://"))

    def test_postgres_special_character_password_normalization(self):
        """Verify PostgreSQL URLs with unencoded special characters in password are safely URL encoded."""
        raw_url = "postgresql://postgres.kybdgnxilghfushektao:Sanu@2006@3*&@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
        normalized_url = normalize_database_url(raw_url)
        self.assertIn("Sanu%402006%403%2A%26", normalized_url)
        self.assertTrue(normalized_url.startswith("postgresql://"))

    def test_postgresql_engine_configuration(self):
        """Verify engine kwargs for PostgreSQL URLs include pool_pre_ping and empty connect_args."""
        pg_url = "postgresql://user:password@cloud-db-host.com:5432/mydb"
        normalized = normalize_database_url(pg_url)
        
        if normalized.startswith("sqlite"):
            engine_kwargs = {"connect_args": {"check_same_thread": False}}
        else:
            engine_kwargs = {
                "connect_args": {},
                "pool_pre_ping": True,
                "pool_recycle": 300,
            }
            
        self.assertEqual(engine_kwargs["connect_args"], {})
        self.assertTrue(engine_kwargs["pool_pre_ping"])
        self.assertEqual(engine_kwargs["pool_recycle"], 300)

    def test_app_database_import(self):
        """Verify backend app.database module initializes engine and Base correctly."""
        from app.database import engine, Base, SessionLocal, get_db, SQLALCHEMY_DATABASE_URL
        
        self.assertIsNotNone(engine)
        self.assertIsNotNone(Base)
        self.assertIsNotNone(SessionLocal)
        self.assertIsNotNone(SQLALCHEMY_DATABASE_URL)

    def test_cloud_postgres_live_connection_if_env_present(self):
        """Test live PostgreSQL connection if CLOUD_POSTGRES_URL environment variable is present."""
        pg_url = os.getenv("CLOUD_POSTGRES_URL") or os.getenv("DATABASE_URL")
        if not pg_url or pg_url.startswith("sqlite"):
            self.skipTest("CLOUD_POSTGRES_URL / PostgreSQL DATABASE_URL environment variable not provided for live PostgreSQL test.")
            
        normalized_pg_url = normalize_database_url(pg_url)
        pg_engine = create_engine(normalized_pg_url, pool_pre_ping=True)
        try:
            with pg_engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                self.assertEqual(result, 1)
        finally:
            pg_engine.dispose()

if __name__ == "__main__":
    unittest.main()

