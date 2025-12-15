import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BotConfig
from bot.handlers import start, admin, form, chat_member, ai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    bot = Bot(token=BotConfig.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    # AI обработчик должен быть последним, чтобы не перехватывать другие команды
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(form.router)
    dp.include_router(chat_member.router)
    dp.include_router(ai.router)  # AI обработчик в конце

    logger.info("Бот запущен")
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

