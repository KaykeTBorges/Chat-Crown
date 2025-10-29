import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import config

# Importando os handlers
from bot.handlers import (
    start_handler,
    help_handler,
    summary_handler,
    message_handler
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
            # Validate config here instead of at import time
            from config import config
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
        """Configura os handlers de comandos e mensagens"""
        # Handlers de comandos
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("ajuda", help_handler))
        self.application.add_handler(CommandHandler("resumo", summary_handler))
        
        # Handler para mensagens de despesas
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        logger.info("✅ Handlers do bot configurados")
    
    def run(self):
        """Inicia o bot"""
        logger.info("🤖 Iniciando bot...")
        self.application.run_polling()

# Instância global do bot
bot = FinanceBot()