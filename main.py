#!/usr/bin/env python3
"""
Sistema Financeiro Pessoal do Kayke
Chat Crown + Método Breno Nogueira
"""

import logging
from services.database import db_manager
from bot.bot import bot
from config import config

logger = logging.getLogger(__name__)

def setup():
    print("🚀 Iniciando Sistema Financeiro Pessoal...")
    
    db_success = db_manager.test_connection()
    
    if db_success:
        try:
            db_manager.create_tables()
            print("✅ Tabelas do banco criadas/verificadas!")
        except Exception as e:
            print(f"⚠️  Erro ao criar tabelas: {e}")
    else:
        print("⚠️  Continuando sem banco de dados...")

def main():
    try:
        setup()
        
        print("\n🎯 Sistema pronto!")
        print("📱 Telegram Bot: Aguardando mensagens...")
        print("💻 Streamlit: Execute 'streamlit run streamlit_app/app.py'")
        print("\n⏹️  Pressione Ctrl+C para parar\n")
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        raise

if __name__ == "__main__":
    main()