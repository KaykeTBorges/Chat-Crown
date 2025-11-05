# services/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import config

class DatabaseManager:
    def __init__(self):
        self.database_url = config.DATABASE_URL
        self._setup_engine()
        self._create_tables()

    def _setup_engine(self):
        """Conecta exclusivamente ao banco Supabase (sem fallback para SQLite)."""
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            future=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True
        )

        print("✅ Conexão com o Supabase configurada")

    def get_session(self):
        return self.SessionLocal()

    def _create_tables(self):
        """Cria as tabelas no banco remoto."""
        try:
            from models.base import Base
            Base.metadata.create_all(bind=self.engine)
            print("🗃️ Tabelas verificadas/criadas no Supabase")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")

    def test_connection(self):
        """Testa conexão simples com o Supabase."""
        with self.get_session() as session:
            session.execute(text("SELECT 1"))
        print("✅ Conexão OK com o Supabase")

db_manager = DatabaseManager()
