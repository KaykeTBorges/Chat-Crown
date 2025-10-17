from telegram import Update
from telegram.ext import ContextTypes

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    await update.effective_message.reply_text(
        "✅ Registrado!\n"
        f"📝 Mensagem: {text}\n"
        "Obs.: Integração com parser/DB entra no Dia 2."
    )
# aqui precisa estar conectado com o processador de IA das mensagens, ou em regex ou no groq
# por enquanto apenas fingimos registrar



    
    