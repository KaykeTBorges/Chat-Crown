# bot.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand

# Handlers dos comandos
from bot.handlers.start import start
from bot.handlers.help import ajuda
from bot.handlers.summary_handler import resumo
from bot.handlers.expense_handler import handle_expense  # handler de gastos

# Configurações
from config import settings

# =====================
# 🔹 Configuração de logging
# =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================
# 🔹 Função para criar a aplicação do bot
# =====================
def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()
    # ---------------------
    # Handlers de comandos
    # ---------------------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("resumo", resumo))
    # ---------------------
    # Handler para mensagens de texto que não são comandos
    # Todas essas mensagens serão tratadas como possíveis gastos
    # ---------------------
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense))

    return app

# =====================
# 🔹 Define os comandos do bot (BotFather)
# =====================
async def set_bot_commands(app: Application) -> None:
    """
    Define os comandos que aparecem no menu do Telegram.
    """
    commands = [
        BotCommand("start", "Iniciar conversa"),
        BotCommand("ajuda", "Ver ajuda e exemplos"),
        BotCommand("resumo", "Resumo do mês atual")
        # Futuramente: /relatorio, /categoria, /editar
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Comandos do bot definidos com sucesso.")

# =====================
# 🔹 Inicia o bot
# =====================
def start_bot() -> None:
    """
    Inicializa a aplicação, define comandos e inicia long polling.
    """
    app = build_application()

    async def _post_init(_: Application) -> None:
        await set_bot_commands(app)

    app.post_init = _post_init

    logger.info("Iniciando long polling do bot...")
    app.run_polling(close_loop=False)

# =====================
# 🔹 Ponto de entrada
# =====================
if __name__ == "__main__":
    start_bot()
