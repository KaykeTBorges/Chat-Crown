from telegram import Update
from telegram.ext import ContextTypes
from services.transactions_service import transactions_service
from services.users_service import UsersService
from services.ai_processor import ai_processor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = UsersService.get_or_create_user(update.effective_user)
    user_message = update.message.text

    try:
        data = ai_processor.detect_expense(user_message)
        if data['amount'] is None:
            await update.message.reply_text("❌ Não consegui identificar o valor. Ex: 'almoço 45,50'")
            return

        transaction = transactions_service.create(
            user_id=user.id,
            description=data['description'],
            amount=data['amount'],
            category=data['category'],
            type=data['type'],
            date=datetime.now(),
            detected_by=data['detected_by']
        )

        await update.message.reply_text(f"✅ Transação registrada: {transaction.category} - R$ {transaction.amount:.2f}")

    except Exception as e:
        logger.error(f"Erro no message_handler: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao processar sua mensagem.")
