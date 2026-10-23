from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Next Claw Personal Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "temporary-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database
    DATABASE_URL: Optional[str] = "postgresql://postgres:password@localhost:5432/nextserve"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Gmail Live Integration
    GMAIL_USER: Optional[str] = "chigbookpalaugo@gmail.com"
    GMAIL_APP_PASSWORD: Optional[str] = None
    GMAIL_IMAP_SERVER: str = "imap.gmail.com"
    GMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    GMAIL_SMTP_PORT: int = 587

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
