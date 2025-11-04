#!/usr/bin/env python3

"""
Sistema Financeiro Pessoal do Kayke
Chat Crown + Método Breno Nogueira
"""

from services.database import db_manager
from bot.bot import bot

def setup():
    print("🚀 Inicializando Sistema Financeiro Pessoal...")
    db_manager.test_connection()

def main():
    setup()

    print("\n🎯 Sistema pronto!")
    print("📱 Telegram Bot ouvindo mensagens...")
    print("💻 Para abrir o painel:    streamlit run streamlit_app/app.py")
    print("\n⏹️  Pressione Ctrl+C para encerrar.\n")

    bot.run()

if __name__ == "__main__":
    main()
