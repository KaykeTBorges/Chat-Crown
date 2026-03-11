# bot/bot.py
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import config

from bot.handlers.start_handler import start_handler
from bot.handlers.help_handler import help_handler
from bot.handlers.login_handler import login_handler
from bot.handlers.summary_handler import summary_handler
from bot.handlers.message_handler import message_handler
from bot.handlers.list_handler import list_transactions_handler
from bot.handlers.edit_handler import (
    edit_init_handler,
    edit_choice_handler,
    edit_process_handler,
    edit_cancel_handler,
)
from bot.handlers.delete_handler import (
    delete_confirm_handler,
    delete_execute_handler,
    delete_cancel_handler,
)

# Configure logging according to the configured log level.
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class FinanceBot:
    """Wrapper around the Telegram Application to register all handlers."""

    def __init__(self):
        # Build the Telegram application using the bot token from config.
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Register all command, callback and message handlers."""
        # Simple command handlers.
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("ajuda", help_handler))
        self.application.add_handler(CommandHandler("login", login_handler))
        self.application.add_handler(CommandHandler("resumo", summary_handler))
        self.application.add_handler(CommandHandler("listar", list_transactions_handler))

        # --- Edit handlers (edit an existing transaction) ---
        self.application.add_handler(CallbackQueryHandler(edit_init_handler, pattern="^edit_"))
        self.application.add_handler(CallbackQueryHandler(edit_choice_handler, pattern="^edit_choice_"))
        self.application.add_handler(CallbackQueryHandler(edit_cancel_handler, pattern="^edit_cancel$"))

        # Handler that receives the new text value for the edit flow.
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, edit_process_handler))

        # --- Delete handlers (confirm / cancel delete) ---
        self.application.add_handler(CallbackQueryHandler(delete_confirm_handler, pattern="^delete_"))
        self.application.add_handler(CallbackQueryHandler(delete_execute_handler, pattern="^confirm_delete$"))
        self.application.add_handler(CallbackQueryHandler(delete_cancel_handler, pattern="^cancel_delete$"))

        # --- General message handler (register new transactions) ---
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    def run(self):
        """Start polling for Telegram updates."""
        self.application.run_polling()


bot = FinanceBot()