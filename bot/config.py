import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Настройки бота из переменных окружения"""
    
    # ========== Бот ==========
    BOT_TOKEN: str
    
    # ========== API ==========
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_URL: Optional[str] = None
    WEBAPP_URL: Optional[str] = None
    
    # ========== Docker ==========
    DOCKER_ENV: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Определяем, запущены ли мы в Docker
        if os.getenv("DOCKER_ENV") or os.getenv("API_HOST"):
            self.DOCKER_ENV = True
            self.API_HOST = os.getenv("API_HOST", "api")
        
        # Формируем URL для API (внутренний, может быть HTTP)
        if not self.API_URL:
            self.API_URL = f"http://{self.API_HOST}:{self.API_PORT}/api"
        
        if not self.WEBAPP_URL:
            # Пытаемся получить из переменной окружения (может быть установлена в docker-compose)
            webapp_url_env = os.getenv("WEBAPP_URL")
            if webapp_url_env:
                self.WEBAPP_URL = webapp_url_env
            else:
                # Если не указано, формируем из API_HOST (но это будет HTTP, что не подходит для Telegram)
                # В продакшене обязательно нужно указать WEBAPP_URL с HTTPS!
                self.WEBAPP_URL = f"http://{self.API_HOST}:{self.API_PORT}"


# Создаем глобальный экземпляр настроек
settings = BotSettings()


class BotConfig:
    """Конфигурация бота"""
    TOKEN: str = settings.BOT_TOKEN
    API_URL: str = settings.API_URL
    WEBAPP_URL: str = settings.WEBAPP_URL
