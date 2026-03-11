# bot/handlers/login_handler.py
import requests
from telegram import Update
from telegram.ext import ContextTypes
from config.config import config

# Auth API base URL (FastAPI).
API_URL = config.API_URL
# Streamlit app public URL (where the user enters the code).
STREAMLIT_URL = config.STREAMLIT_URL

async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a one-time login code and send it back to the Telegram user."""
    telegram_id = update.effective_user.id
    
    try:
        # Ask the auth API to generate a one-time code for this Telegram ID.
        response = requests.post(f"{API_URL}/auth/generate_code", data={"telegram_id": telegram_id})
        response.raise_for_status()  # Raise if the HTTP request failed.
        
        data = response.json()
        login_code = data.get("code")
        
        if login_code:
            text = (
                f"🔐 Seu código de acesso único é:\n\n"
                f"`{login_code}`\n\n"
                f"Acesse o painel pelo link abaixo e digite o código:\n"
                f"{STREAMLIT_URL}\n\n"
                f"⏰ Este código expira em 5 minutos."
            )
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Não foi possível gerar seu código. Tente novamente.")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")
        await update.message.reply_text("❌ O serviço de autenticação está indisponível. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Erro inesperado no login: {e}")
        await update.message.reply_text("❌ Ocorreu um erro inesperado.")