# bot/handlers/painel_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from config import config

async def painel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Link que ativa o login OAuth
    link = (
        "https://oauth.telegram.org/auth?"
        f"bot_id={config.TELEGRAM_BOT_USERNAME}&"
        f"origin={config.STREAMLIT_URL}&"
        f"return_to={config.STREAMLIT_URL}"
    )

    mensagem = f"""
💻 Para acessar seu painel financeiro:

👉 *Clique abaixo* para logar automaticamente usando o Telegram:
{link}

⚡ Não precisa senha. Login seguro.
"""

    await update.message.reply_text(mensagem, parse_mode="Markdown")
