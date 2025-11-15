# bot/handlers/list_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service
from datetime import datetime

async def list_transactions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista transações do mês atual com botões de editar e excluir."""
    telegram_id = update.effective_user.id # Pega o telegram_id
    now = datetime.now()

    transactions, _ = transactions_service.get_transactions(
        telegram_id=telegram_id,
        filters={"date_range": "current_month"}
    )

    # Se não houver transações ainda
    if not transactions:
        await update.message.reply_text(
            "📭 Você ainda não tem transações registradas neste mês.\n"
            "💡 Envie uma mensagem como:\n\n"
            "`+ 25 almoço`\n"
            "`- 120 mercado`\n",
            parse_mode='Markdown'
        )
        return

    text = f"📋 *Suas transações de {now.strftime('%B/%Y')}*\n\n"
    keyboard_rows = []

    for t in transactions:
        # Usando um emoji para identificar o tipo
        emoji = "💰" if t.type == 'renda' else "💸" if 'despesa' in t.type else "🚀"
        text += f"{emoji} *{t.category}* — `R$ {t.amount:.2f}` (ID: `{t.id}`)\n"

        keyboard_rows.append([
            InlineKeyboardButton("✏️ Editar", callback_data=f"edit_{t.id}"),
            InlineKeyboardButton("🗑️ Excluir", callback_data=f"delete_{t.id}")
        ])

    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard_rows)
    )

__all__ = ["list_transactions_handler"]