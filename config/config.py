# config/config.py
import os

class Config:
    """Central configuration for the Chat Crown application."""

    # --- Telegram bot configuration ---
    # Bot token created via @BotFather.
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    # Bot username (without "@"). Used by the login widget/link.
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

    # --- Service URLs (API and Streamlit) ---
    # URL where the authentication API (FastAPI) is running.
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    # Public URL where the Streamlit app is accessible.
    STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")

    # --- Database configuration ---
    # If DATABASE_URL is not set, use a local SQLite file for personal use.
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///chat_crown.db")

    # --- External processing configuration ---
    # Optional key for external text processing features
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # --- General configuration ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    # Logging level used across the project (e.g., INFO, DEBUG).
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # --- Business rules configuration ---
    # Default savings percentage used by the monthly summary calculations.
    DEFAULT_SAVINGS_PERCENTAGE = 0.25  # 25%

    def validate(self):
        """Validate that all required environment variables are present."""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("A variável de ambiente 'TELEGRAM_BOT_TOKEN' é obrigatória.")
        if not self.TELEGRAM_BOT_USERNAME:
            raise ValueError("A variável de ambiente 'TELEGRAM_BOT_USERNAME' é obrigatória.")
        
        if not self.GROQ_API_KEY:
            print("⚠️  WARNING: 'GROQ_API_KEY' is not set. Optional text processing features will be disabled.")
        
        if not self.API_URL:
            raise ValueError("A variável de ambiente 'API_URL' é obrigatória para a autenticação.")
        
        if not self.STREAMLIT_URL:
            raise ValueError("A variável de ambiente 'STREAMLIT_URL' é obrigatória para os redirecionamentos.")

# Global config instance used throughout the application.
config = Config()

# Validate config as soon as this module is imported.
try:
    config.validate()
    print("✅ Configuration loaded and validated successfully!")
except Exception as e:
    print(f"❌ Configuration error: {e}")