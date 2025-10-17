from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await user.send_message(text="👋 Olá! Sou o Chat Crown, seu assistente financeiro. 💰")
    await user.send_message(text="💡 Para começar, envie uma mensagem com o valor e categoria do seu gasto. 💡")
    await user.send_message(text="💡 Para ver os comandos disponíveis, envie /ajuda. 💡")
    

