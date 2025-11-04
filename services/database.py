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
        """Configura engine com fallback automático para SQLite"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                future=True
            )
            print("✅ Conectado ao Supabase")
        except Exception as e:
            print(f"❌ Erro ao conectar ao Supabase: {e}")
            print("🔄 Alternando para SQLite local...")
            self.database_url = "sqlite:///./finance.db"
            self.engine = create_engine(self.database_url, future=True)

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
        """Testa conexão de forma simples"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            print("✅ Conexão OK")
        except Exception:
            print("⚠️ Conexão falhou, reconfigurando para SQLite...")
            self.database_url = "sqlite:///./finance.db"
            self._setup_engine()
            self._create_tables()

db_manager = DatabaseManager()
