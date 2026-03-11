from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service

async def delete_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a confirmation message before deleting a transaction."""
    query = update.callback_query
    await query.answer()

    transaction_id = int(query.data.replace("delete_", ""))
    context.user_data["delete_id"] = transaction_id

    # Load the transaction so we can show what will be deleted.
    t = transactions_service.get_by_id(transaction_id)
    if not t:
        await query.edit_message_text("⚠️ Could not find that transaction to delete.")
        return

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
    """Delete the transaction after the user confirms."""
    query = update.callback_query
    await query.answer()

    transaction_id = context.user_data.get("delete_id")

    if transaction_id is None:
        await query.edit_message_text("⚠️ No transaction selected for deletion.")
        return

    deleted = transactions_service.delete(transaction_id)

    if deleted:
        await query.edit_message_text("✅ *Transaction deleted successfully!*", parse_mode="Markdown")
    else:
        await query.edit_message_text("❌ Failed to delete the transaction.")


async def delete_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the delete flow."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Operation cancelled.")
