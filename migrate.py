# setup_db.py
from services.database import db_manager
from models.base import Base

print("⚠️ ATENÇÃO: Isso vai APAGAR todos os dados do banco de dados.")
input("Pressione Enter para continuar ou Ctrl+C para cancelar...")

print("Dropping all tables...")
Base.metadata.drop_all(bind=db_manager.engine)

print("Creating all tables...")
Base.metadata.create_all(bind=db_manager.engine)

print("✅ Banco de dados recriado com sucesso com a nova estrutura (telegram_id)!")