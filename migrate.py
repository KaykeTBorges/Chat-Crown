import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from config import config

# Handlers existentes
from bot.handlers.start_handler import start_handler
from bot.handlers.help_handler import help_handler
from bot.handlers.summary_handler import summary_handler
from bot.handlers.message_handler import message_handler

# 🔥 NOVO: Handler de edição guiada
from bot.handlers.edit_handler import (
    start_edit,
    ask_new_amount,
    ask_new_category,
    ask_new_description,
    CANCEL,
    AMOUNT,
    CATEGORY,
    DESCRIPTION
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
        """Configura comandos, edição guiada e mensagens"""
        
        # --- Comandos existentes ---
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("ajuda", help_handler))
        self.application.add_handler(CommandHandler("resumo", summary_handler))

        # --- 🔥 NOVO: Conversation Handler de edição guiada ---
        edit_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_edit, pattern="^edit_")],
            states={
                AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_amount)],
                CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_category)],
                DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_description)],
            },
            fallbacks=[CommandHandler("cancelar", CANCEL)],
        )

        self.application.add_handler(edit_conv)

        # --- Mensagens comuns (registrar despesas/renda) ---
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        logger.info("✅ Handlers carregados com sucesso!")
    
    def run(self):
        logger.info("🤖 Iniciando bot...")
        self.application.run_polling()


# Instância global do bot
bot = FinanceBot()
