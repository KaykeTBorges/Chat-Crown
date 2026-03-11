#!/usr/bin/env python3

from dotenv import load_dotenv

# Load environment variables before anything else so config and services can see them.
load_dotenv()

"""
Entry point for running the Telegram bot + database initialization.
This script prepares the database and then starts listening for bot updates.
"""

import logging
from services.database import db_manager
import models  # Import all models to ensure mappings are registered before creating tables.
from bot.bot import bot

# Basic logging configuration for the whole application.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def setup_database():
    """Create all tables (if needed) and verify the database connection."""
    try:
        db_manager.test_connection()
        logger.info("✅ Conexão com o banco de dados OK!")
        
        models.Base.metadata.create_all(bind=db_manager.engine)
        logger.info("✅ Todas as tabelas foram verificadas/criadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Falha ao inicializar banco de dados: {e}")
        raise

def setup():
    """High-level setup hook before actually starting the bot."""
    print("🚀 Inicializando Sistema Financeiro Pessoal...")
    setup_database()


def main():
    """Run the setup and then start the Telegram bot loop."""
    setup()

    print("\n🎯 Sistema pronto!")
    print("📱 Telegram Bot ouvindo mensagens...")
    print("💻 Para abrir o painel:    streamlit run streamlit_app/app.py")
    print("\n⏹️  Pressione Ctrl+C para encerrar.\n")

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao rodar o bot: {e}")

if __name__ == "__main__":
    main()
