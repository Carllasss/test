from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from bot.api_client import APIClient
from bot.keyboards import get_admin_keyboard

router = Router()
api_client = APIClient()


@router.callback_query(F.data == "admin_stats")
async def show_users_stats(callback: CallbackQuery):
    """Показать статистику пользователей"""
    stats = await api_client.get_users_statistics()
    
    text = (
        f"📊 Статистика пользователей:\n\n"
        f"👥 Всего пользователей в БД: {stats.get('total', 0)}\n"
        f"✅ Активных пользователей (не заблокировали бота): {stats.get('active', 0)}\n"
        f"📋 Лидов в Bitrix24: {stats.get('bitrix_leads', 0)}"
    )
    
    try:
        # Пытаемся отредактировать сообщение
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
        await callback.answer()
    except TelegramBadRequest as e:
        # Если сообщение не изменилось
        if "message is not modified" in str(e).lower():
            await callback.answer("Статистика актуальна", show_alert=False)
        else:
            # Другая ошибка BadRequest
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    except Exception as e:
        # Другая ошибка - отправляем новое сообщение
        await callback.message.answer(text, reply_markup=get_admin_keyboard())
        await callback.answer()

