from typing import Optional

from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources.providers import secrets


class Settings(BaseSettings):
    """Конфигурация из env"""

    # ========== Бот ==========
    BOT_TOKEN: str
    BOT_WEBHOOK_URL: Optional[str] = None

    # ========== База данных ==========
    DATABASE_URL: str = "sqlite:///./bot.db"
    ASYNC_DATABASE_URL: Optional[str] = None

    @validator("ASYNC_DATABASE_URL", pre=True)
    def assemble_async_db_url(cls, v: Optional[str], values: dict) -> str:
        """Автоматически создаем async URL если не задан"""
        if isinstance(v, str):
            return v

        sync_url = values.get("DATABASE_URL", "")
        if sync_url.startswith("postgresql://"):
            return sync_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            return sync_url.replace("sqlite://", "sqlite+aiosqlite://")

    # ========== Битрикс24 ==========
    BITRIX24_WEBHOOK_URL: Optional[str] = None

    # ========== Веб-приложение ==========
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8000
    WEBAPP_URL: Optional[str] = None


    # ========== Настройки логирования ==========
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False


    # ========== Настройки приложения ==========
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, production

    GOOGLE_SERVICE_ACCOUNT: str = './service_account.json'
    SHEET_DOC_ID: str = None
    CHROMA_PERSIST_DIR: str = None
    CACHE_TTL: int = 300

    OLLAMA_HOST: str = "http://ollama:11434"

    # Настройки для pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()
config = settings