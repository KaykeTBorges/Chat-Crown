from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service
from datetime import datetime

async def list_transactions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista transações do mês atual com botões de editar e excluir."""
    user = update.effective_user
    now = datetime.now()

    transactions = transactions_service.get_transactions_by_month(
        user_id=user.id,
        month=now.month,
        year=now.year
    )

    # Se não houver transações ainda
    if not transactions:
        await update.message.reply_text(
            "📭 Você ainda não tem transações registradas neste mês.\n"
            "💡 Envie uma mensagem como:\n\n"
            "`+ 25 almoço`\n"
            "`- 120 mercado`\n",
            parse_mode="Markdown"
        )
        return

    text = "📋 *Suas transações deste mês:*\n\n"
    keyboard_rows = []

    for t in transactions:
        text += f"• *{t.category}* — `R$ {t.amount:.2f}` (ID: `{t.id}`)\n"

        keyboard_rows.append([
            InlineKeyboardButton("✏️ Editar", callback_data=f"edit_{t.id}"),
            InlineKeyboardButton("🗑️ Excluir", callback_data=f"delete_{t.id}")
        ])

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_rows)
    )

__all__ = ["list_transactions_handler"]
