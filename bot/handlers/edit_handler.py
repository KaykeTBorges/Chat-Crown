import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service

logger = logging.getLogger(__name__)

"""
Fluxo:
1) Bot recebe callback: edit_<ID>  → edit_init_handler
2) Bot pergunta ao usuário o novo valor
3) user_data guarda o ID da transação
4) Usuário responde → edit_process_handler finaliza atualização
"""

async def edit_init_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de edição (pergunta novo valor)."""
    query = update.callback_query
    await query.answer()

    try:
        transaction_id = int(query.data.split("_")[1])
    except:
        await query.edit_message_text("❌ Erro ao identificar a transação.")
        return

    # Guardamos no estado até o usuário responder
    context.user_data["edit_transaction_id"] = transaction_id

    await query.edit_message_text(
        f"✏️ *Editar Transação*\n\n"
        f"Digite o *novo valor* para a transação ID `{transaction_id}` (ex: `45,90` ou `100`):",
        parse_mode="Markdown"
    )


async def edit_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o novo valor digitado e atualiza no banco."""
    user = update.effective_user
    text = update.message.text

    if "edit_transaction_id" not in context.user_data:
        await update.message.reply_text("❌ Nenhuma edição em andamento.")
        return
    
    transaction_id = context.user_data["edit_transaction_id"]

    # Converter valor
    try:
        text = text.replace(",", ".")
        new_value = float(text)
    except:
        await update.message.reply_text("❌ Valor inválido. Tente novamente, ex: `32,50`.")
        return

    # Atualiza no banco
    success = transactions_service.update_transaction(
        transaction_id=transaction_id,
        user_id=user.id,
        amount=new_value
    )

    if not success:
        await update.message.reply_text("❌ Não foi possível atualizar a transação.")
        return

    # Limpa o state
    context.user_data.pop("edit_transaction_id", None)

    await update.message.reply_text(
        f"✅ Valor atualizado com sucesso!\n\n"
        f"Novo valor: *R$ {new_value:.2f}*",
        parse_mode="Markdown"
    )

__all__ = ["edit_init_handler", "edit_process_handler"]
