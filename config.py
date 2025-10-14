# config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Telegram
    telegram_bot_token: str
    
    # Database
    database_url: str
    
    # Groq API
    groq_api_key: str
    
    # Application
    environment: str = "development"
    log_level: str = "INFO" 
    debug: bool = True
    
    # Optional: Webhook (para produção)
    webhook_url: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
