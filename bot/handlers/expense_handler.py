# bot/handlers/expense_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from services.expense_service import ExpenseService
import logging

logger = logging.getLogger(__name__)

expense_service = ExpenseService()

async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = (update.message.text or "").strip()  # remove espaços extras

    if not message_text:
        await update.message.reply_text("❌ Por favor, envie um valor e uma descrição do gasto.")
        return

    logger.info(f"[Handler] Mensagem recebida de user_id={user_id}: '{message_text}'")

    result = expense_service.register_expense(user_id, message_text)

    if not result.get("success") or result["data"]["amount"] <= 0:
        await update.message.reply_text(
            "❌ Não foi possível registrar o gasto. "
            "Verifique se você informou o valor corretamente."
        )
        logger.warning(f"[Handler] Gasto inválido: {result}")
        return

    data = result["data"]

    category = data.get("category") or "Desconhecida"
    if category == "Desconhecida":
        category += " ⚠️ Categoria não identificada"

    response = (
        f"✅ Gasto registrado!\n"
        f"💰 Valor: R$ {data['amount']:.2f}\n"
        f"📂 Categoria: {category}\n"
        f"📝 Descrição: {data['description']}\n"
    )

    logger.info(f"[Handler] Respondendo usuário {user_id}: {response.replace(chr(10), ' | ')}")

    await update.message.reply_text(response)
