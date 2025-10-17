from telegram import Update
from telegram.ext import ContextTypes

CATEGORIES = [
"🙏 Dízimos/Contribuição", 
"🏠 Moradia", 
"🍽️ Alimentação", 
"🚗 Transporte",
"💳 Dívidas", 
"🎮 Lazer", 
"👕 Vestuário", 
"💊 Saúde", 
"📚 Educação",
"📦 Diversos", 
"💰 Seguros/Poupanças/Investimento"
]

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    categorias = "\n".join(f"- {c}" for c in CATEGORIES)
    await update.effective_message.reply_text(
        "/start - iniciar conversa\n"
        "/ajuda - ajuda e exemplos\n"
        "/resumo - resumo do mês atual\n\n"
        "Categorias disponíveis:\n"
        f"{categorias}\n\n"
        "Exemplos:\n"
        "• 50 almoco\n"
        "• 100 uber\n"
        "• 30,50 café"
    )
