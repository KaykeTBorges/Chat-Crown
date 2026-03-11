# services/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.config import config


class DatabaseManager:
    """Central place to manage the SQLAlchemy engine and sessions."""

    def __init__(self):
        # Use the URL from config, which falls back to a local SQLite file.
        self.database_url = config.DATABASE_URL
        self._setup_engine()
        self._create_tables()

    def _setup_engine(self):
        """Create the SQLAlchemy engine and session factory."""
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            future=True,
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True,
        )

        print(f"✅ Database engine created for URL: {self.database_url}")

    def get_session(self):
        """Return a new database session. Caller is responsible for closing it."""
        return self.SessionLocal()

    def _create_tables(self):
        """Create all tables defined in SQLAlchemy models, if they do not exist."""
        try:
            from models.base import Base

            Base.metadata.create_all(bind=self.engine)
            print("🗃️ Database tables checked/created successfully")
        except Exception as e:
            print(f"❌ Error while creating tables: {e}")

    def test_connection(self):
        """Run a very small query just to confirm the database is reachable."""
        with self.get_session() as session:
            session.execute(text("SELECT 1"))
        print("✅ Database connection test passed")


db_manager = DatabaseManager()
