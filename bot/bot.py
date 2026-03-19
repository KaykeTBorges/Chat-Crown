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
        # Use specific regex patterns to avoid collisions between edit_init and edit_choice/edit_cancel.
        self.application.add_handler(CallbackQueryHandler(edit_choice_handler, pattern=r"^edit_choice_"))
        self.application.add_handler(CallbackQueryHandler(edit_cancel_handler, pattern=r"^edit_cancel$"))
        self.application.add_handler(CallbackQueryHandler(edit_init_handler, pattern=r"^edit_\d+$"))

        # --- Delete handlers (confirm / cancel delete) ---
        self.application.add_handler(CallbackQueryHandler(delete_execute_handler, pattern=r"^confirm_delete$"))
        self.application.add_handler(CallbackQueryHandler(delete_cancel_handler, pattern=r"^cancel_delete$"))
        self.application.add_handler(CallbackQueryHandler(delete_confirm_handler, pattern=r"^delete_\d+$"))

        # --- Text message handlers ---
        # edit_process_handler is in group 0 (default), message_handler in group 1.
        # edit_process_handler checks if an edit is in progress; if not, it does nothing
        # and the message falls through to group 1 where message_handler picks it up.
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_process_handler),
            group=0,
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler),
            group=1,
        )

    def run(self):
        """Start polling for Telegram updates."""
        self.application.run_polling()


bot = FinanceBot()