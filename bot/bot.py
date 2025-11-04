import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import config

# Handlers existentes
from bot.handlers.start_handler import start_handler
from bot.handlers.help_handler import help_handler
from bot.handlers.summary_handler import summary_handler
from bot.handlers.message_handler import message_handler

# Novos handlers adicionados
from bot.handlers.list_handler import list_transactions_handler
from bot.handlers.edit_handler import (
    edit_init_handler,
    edit_process_handler
)
from bot.handlers.delete_handler import (
    delete_confirm_handler,
    delete_execute_handler,
    delete_cancel_handler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)


class FinanceBot:
    def __init__(self):
        self.application = None
        self.setup_bot()
    
    def setup_bot(self):
        """Configura o bot do Telegram com token e handlers"""
        try:
            config.validate()

            if not config.TELEGRAM_BOT_TOKEN:
                raise ValueError("Token do bot Telegram não configurado nas variáveis de ambiente")
            
            self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
            self._setup_handlers()

            logger.info("✅ Bot configurado com sucesso!")

        except Exception as e:
            logger.error(f"❌ Erro ao configurar bot: {e}")
            raise
    
    def _setup_handlers(self):
        """Registra handlers no bot"""

        # Comandos principais
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("ajuda", help_handler))
        self.application.add_handler(CommandHandler("resumo", summary_handler))

        # ✅ Novo comando de listagem
        self.application.add_handler(CommandHandler("listar", list_transactions_handler))

        # ✅ Callbacks de edição
        self.application.add_handler(CallbackQueryHandler(edit_init_handler, pattern="^edit_"))
        self.application.add_handler(CallbackQueryHandler(edit_process_handler, pattern="^save_edit$"))

        # ✅ Callbacks de exclusão
        self.application.add_handler(CallbackQueryHandler(delete_confirm_handler, pattern="^delete_"))
        self.application.add_handler(CallbackQueryHandler(delete_execute_handler, pattern="^confirm_delete$"))
        self.application.add_handler(CallbackQueryHandler(delete_cancel_handler, pattern="^cancel_delete$"))

        # Handler de mensagens (registro automático)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        logger.info("✅ Todos os handlers foram registrados com sucesso.")
    
    def run(self):
        logger.info("🤖 Bot iniciado e aguardando mensagens...")
        self.application.run_polling()


# Instância global
bot = FinanceBot()
