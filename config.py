import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
    
    # Database (we'll set this up later with Supabase)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Groq AI API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # App Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    STREAMLIT_URL = os.getenv("STREAMLIT_URL")
    
    # Method Breno Nogueira Defaults
    DEFAULT_SAVINGS_PERCENTAGE = 0.25  # 25%
    
    def validate(self):
        """Validate that required environment variables are set"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # For now, database is optional until we set up Supabase
        if not self.DATABASE_URL:
            print("⚠️  DATABASE_URL not set - running in memory mode")
        
        if not self.GROQ_API_KEY:
            print("⚠️  GROQ_API_KEY not set - AI features will be limited")

# Global config instance
config = Config()

# Validate config on import
try:
    config.validate()
    print("✅ Configuration loaded successfully!")
except Exception as e:
    print(f"❌ Configuration error: {e}")