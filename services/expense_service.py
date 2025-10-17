from datetime import datetime
from services.ai_processor import AIProcessor
from repositories.expense_repository import create_expense
import logging

logger = logging.getLogger(__name__)

class ExpenseService:
    def __init__(self):
        self.processor = AIProcessor()

    def register_expense(self, user_id: int, message: str):
        logger.info(f"[ExpenseService] Recebendo gasto de user_id={user_id}: '{message}'")

        try:
            parsed = self.processor.parse_message(message)
            logger.debug(f"[ExpenseService] Resultado do AIProcessor: {parsed}")

        except Exception as e:
            logger.error(f"[ExpenseService] Erro ao processar mensagem: {e}")
            parsed = {
                "amount": 0.0,
                "category": "Desconhecida",
                "description": message
            }

        expense_data = {
            "user_id": user_id,
            "amount": parsed["amount"],
            "category": parsed["category"],
            "description": parsed["description"],
            "date": datetime.utcnow(),
        }

        try:
            created = create_expense(**expense_data)
            logger.info(f"[ExpenseService] Gasto salvo no banco: {created}")

        except Exception as e:
            logger.error(f"[ExpenseService] Falha ao salvar no banco: {e}")
            created = expense_data  # fallback, apenas retorna os dados

        return {
            "success": True,
            "data": created,
            "message": "Gasto registrado com sucesso!"
        }