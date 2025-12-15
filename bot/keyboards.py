from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.config import BotConfig


def get_main_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    """Главная клавиатура для обычных пользователей"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Анкета через бот",
                callback_data="form_bot"
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 Анкета через webapp",
                callback_data="form_webapp"
            )
        ]
    ])
    return keyboard


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админов"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👥 Посмотреть пользователей",
                callback_data="admin_stats"
            )
        ]
    ])
    return keyboard


def get_webapp_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой для перехода в webapp"""
    webapp_url = f"{BotConfig.WEBAPP_URL}/api/web/users/{telegram_id}/form"
    
    # Проверяем, что URL использует HTTPS (требование Telegram)
    if not webapp_url.startswith("https://"):
        # В режиме разработки можно использовать ngrok или другой туннель
        # В продакшене обязательно нужен HTTPS!
        raise ValueError(
            f"WebApp URL должен использовать HTTPS! Текущий URL: {webapp_url}\n"
            f"Установите переменную WEBAPP_URL в .env с публичным HTTPS URL"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📱 Открыть форму",
                web_app=WebAppInfo(url=webapp_url)
            )
        ]
    ])
    return keyboard

