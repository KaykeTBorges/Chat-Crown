from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import config
import time

class DatabaseManager:
    def __init__(self):
        self.database_url = config.DATABASE_URL
        self._setup_engine()
        self._create_tables()

    def _setup_engine(self):
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            future=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, future=True
        )


    def get_session(self):
        return self.SessionLocal()

    def _create_tables(self):
        """Cria todas as tabelas registradas no Base"""
        try:
            from models.base import Base
            Base.metadata.create_all(bind=self.engine)
            print("🗃️ Tabelas verificadas/criadas")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")

    def test_connection(self):
        with self.get_session() as session:
            session.execute(text("SELECT 1"))
        print("✅ Conexão OK")


db_manager = DatabaseManager()
