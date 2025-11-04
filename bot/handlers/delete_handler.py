from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service

async def delete_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra mensagem de confirmação antes de excluir."""
    query = update.callback_query
    await query.answer()

    transaction_id = int(query.data.replace("delete_", ""))
    context.user_data["delete_id"] = transaction_id

    t = transactions_service.get_transaction_by_id(transaction_id)

    text = (
        f"🗑️ *Deseja realmente excluir esta transação?*\n\n"
        f"• Categoria: *{t.category}*\n"
        f"• Valor: *R$ {t.amount:.2f}*\n"
        f"• Descrição: _{t.description}_\n\n"
        f"*Essa ação não pode ser desfeita.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Sim, excluir", callback_data="confirm_delete")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete")]
    ])

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def delete_execute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a exclusão após confirmação."""
    query = update.callback_query
    await query.answer()

    transaction_id = context.user_data.get("delete_id")

    if transaction_id is None:
        await query.edit_message_text("⚠️ Erro: Nenhuma transação para excluir.")
        return

    deleted = transactions_service.delete_transaction(transaction_id)

    if deleted:
        await query.edit_message_text("✅ *Transação excluída com sucesso!*", parse_mode="Markdown")
    else:
        await query.edit_message_text("❌ Erro ao excluir a transação.")


async def delete_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a exclusão."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Operação cancelada.")
