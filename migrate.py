# migrate.py
from services.database import db_manager
from models.base import Base

# IMPORTAÇÃO DE TODOS OS MODELS
from models.user import User
from models.transaction import Transaction
from models.magic_link import MagicLink

def run_migrations():
    print("🗃️ Criando tabelas...")
    Base.metadata.create_all(bind=db_manager.engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    run_migrations()
