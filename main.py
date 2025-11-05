#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()  # ✅ Carrega .env antes de tudo!

"""
Sistema Financeiro Pessoal do Kayke
Chat Crown + Método Breno Nogueira
"""

import logging
from services.database import db_manager
import models  # importa todos os models para garantir mapeamento
from bot.bot import bot

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def setup_database():
    """
    Cria todas as tabelas definidas nos models se não existirem
    e testa a conexão com o banco.
    """
    try:
        db_manager.test_connection()
        logger.info("✅ Conexão com o banco de dados OK!")
        
        models.Base.metadata.create_all(bind=db_manager.engine)
        logger.info("✅ Todas as tabelas foram verificadas/criadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Falha ao inicializar banco de dados: {e}")
        raise

def setup():
    print("🚀 Inicializando Sistema Financeiro Pessoal...")
    setup_database()

def main():
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
