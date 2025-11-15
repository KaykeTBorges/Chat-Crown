# config/config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Config:
    """
    Classe de configuração central para o aplicativo Chat Crown.
    Todas as variáveis de ambiente são carregadas e validadas aqui.
    """

    # --- Configurações do Telegram Bot ---
    # Token secreto do bot, obtido no @BotFather
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    # Nome de usuário do bot (sem o @), usado no widget de login
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

    # --- Configurações dos Serviços (API e Streamlit) ---
    # URL onde a API de autenticação (FastAPI) está rodando
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    # URL pública onde o aplicativo Streamlit está acessível
    STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")

    # --- Configurações do Banco de Dados ---
    # URL de conexão com o banco de dados (Ex: Supabase, PostgreSQL, SQLite)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # --- Configurações de IA ---
    # Chave da API do Groq para processamento de linguagem natural
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # --- Configurações Gerais do Aplicativo ---
    # Ambiente: 'development', 'staging', 'production'
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    # Nível de log: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # --- Configurações de Lógica de Negócio ---
    # Porcentagem padrão de economia para o Método Breno
    DEFAULT_SAVINGS_PERCENTAGE = 0.25  # 25%

    def validate(self):
        """
        Valida se todas as variáveis de ambiente obrigatórias foram definidas.
        Lança um ValueError se alguma crítica estiver faltando.
        """
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("A variável de ambiente 'TELEGRAM_BOT_TOKEN' é obrigatória.")
        if not self.TELEGRAM_BOT_USERNAME:
            raise ValueError("A variável de ambiente 'TELEGRAM_BOT_USERNAME' é obrigatória.")
        
        # A validação do DATABASE_URL é importante, mas pode ser opcional em dev
        if not self.DATABASE_URL:
            print("⚠️  AVISO: 'DATABASE_URL' não está definida. O app pode não funcionar corretamente.")
        
        if not self.GROQ_API_KEY:
            print("⚠️  AVISO: 'GROQ_API_KEY' não está definida. Recursos de IA estarão desabilitados.")
        
        if not self.API_URL:
            raise ValueError("A variável de ambiente 'API_URL' é obrigatória para a autenticação.")
        
        if not self.STREAMLIT_URL:
            raise ValueError("A variável de ambiente 'STREAMLIT_URL' é obrigatória para os redirecionamentos.")

# Instância global de configuração para ser usada em todo o aplicativo
config = Config()

# Valida a configuração assim que o módulo é importado
try:
    config.validate()
    print("✅ Configuração carregada e validada com sucesso!")
except Exception as e:
    print(f"❌ Erro de configuração: {e}")