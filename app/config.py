import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mahardika Hub"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://mahardika:mahardika@postgres:5432/mahardika_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # WhatsApp Official API
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

    # Chatwoot
    CHATWOOT_API_URL: str = os.getenv("CHATWOOT_API_URL", "")
    CHATWOOT_API_TOKEN: str = os.getenv("CHATWOOT_API_TOKEN", "")

settings = Settings()
