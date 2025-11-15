# bot/handlers/edit_handler.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service

logger = logging.getLogger(__name__)

async def edit_init_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de edição, mostrando opções."""
    query = update.callback_query
    await query.answer()

    try:
        transaction_id = int(query.data.split("_")[1])
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Erro ao identificar a transação.")
        return

    # NOTA: Precisa de um método no service para buscar por ID
    t = transactions_service.get_transaction_by_id(transaction_id)
    if not t:
        await query.edit_message_text("❌ Transação não encontrada.")
        return

    # Armazena o ID da transação para os próximos passos
    context.user_data["edit_transaction_id"] = transaction_id

    text = (
        f"✏️ *Editar Transação ID: `{t.id}`*\n\n"
        f"• *Valor:* R$ {t.amount:.2f}\n"
        f"• *Descrição:* {t.description}\n"
        f"• *Categoria:* {t.category}\n"
        f"• *Tipo:* {t.type.replace('_', ' ').title()}\n"
        f"• *Data:* {t.date.strftime('%d/%m/%Y')}\n\n"
        f"O que você gostaria de editar?"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Valor", callback_data="edit_choice_amount")],
        [InlineKeyboardButton("📝 Descrição", callback_data="edit_choice_description")],
        [InlineKeyboardButton("📂 Categoria", callback_data="edit_choice_category")],
        [InlineKeyboardButton("🔖 Tipo", callback_data="edit_choice_type")],
        [InlineKeyboardButton("📅 Data", callback_data="edit_choice_date")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="edit_cancel")]
    ])

    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=keyboard)


async def edit_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do campo a ser editado."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data.replace("edit_choice_", "")
    context.user_data["edit_field"] = choice

    prompts = {
        "amount": "Digite o *novo valor* (ex: `45,90` ou `100`):",
        "description": "Digite a *nova descrição*:",
        "category": "Digite a *nova categoria*:",
        "type": "Digite o *novo tipo* (`renda`, `despesa_fixa`, `despesa_variavel`, `economia`):",
        "date": "Digite a *nova data* (formato `DD/MM/AAAA`):"
    }

    text = f"✏️ *Editar Campo: {choice.title()}*\n\n{prompts.get(choice, 'Valor inválido.')}"
    await query.edit_message_text(text, parse_mode='Markdown')


async def edit_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o novo valor e atualiza a transação."""
    user = update.effective_user
    new_value = update.message.text
    field = context.user_data.get("edit_field")
    transaction_id = context.user_data.get("edit_transaction_id")

    if not all([field, transaction_id]):
        await update.message.reply_text("❌ Nenhuma edição em andamento.")
        return

    # Prepara os dados para atualização
    update_data = {"user_id": user.id}
    
    if field == "amount":
        try:
            new_value = new_value.replace(",", ".")
            update_data["amount"] = float(new_value)
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Tente novamente.")
            return
    elif field == "date":
        try:
            from datetime import datetime
            update_data["date"] = datetime.strptime(new_value, "%d/%m/%Y").date()
        except ValueError:
            await update.message.reply_text("❌ Data inválida. Use o formato DD/MM/AAAA.")
            return
    else: # description, category, type
        update_data[field] = new_value

    # NOTA: O service precisa de um método de update flexível
    success = transactions_service.update_transaction(transaction_id, **update_data)

    if success:
        await update.message.reply_text(f"✅ Campo *{field}* atualizado com sucesso!", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Falha ao atualizar a transação.")

    # Limpa o estado
    context.user_data.pop("edit_transaction_id", None)
    context.user_data.pop("edit_field", None)


async def edit_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela o processo de edição."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Edição cancelada.")
    context.user_data.clear()

# Adicione estes handlers ao seu bot.py
# CallbackQueryHandler(edit_choice_handler, pattern="^edit_choice_")
# CallbackQueryHandler(edit_cancel_handler, pattern="^edit_cancel$")