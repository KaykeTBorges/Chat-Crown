"""
Entry point da aplicação Chat Crown.
"""
import logging
from config import settings

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.log_level)
)
logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    logger.info("🚀 Iniciando Chat Crown Bot...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # TODO: Inicializar o bot aqui (Dia 1 - Kayke)
    # from bot.bot import start_bot
    # start_bot()
    
    logger.info("✅ Chat Crown Bot iniciado com sucesso!")


if __name__ == "__main__":
    main()

