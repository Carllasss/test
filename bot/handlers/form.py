from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from bot.api_client import APIClient
from bot.keyboards import get_main_keyboard, get_webapp_keyboard

router = Router()
api_client = APIClient()


class FormStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


@router.callback_query(F.data == "form_bot")
async def start_form_bot(callback: CallbackQuery, state: FSMContext):
    """Начало заполнения анкеты через бот"""
    telegram_id = callback.from_user.id
    
    existing_form = await api_client.get_user_form(telegram_id)
    
    if existing_form:
        text = (
            f"📝 Заполнение анкеты через бот\n\n"
            f"Текущие данные:\n"
            f"Имя: {existing_form.get('name', 'не указано')}\n"
            f"Телефон: {existing_form.get('phone', 'не указан')}\n\n"
            f"Введите ваше имя:"
        )
    else:
        text = "📝 Заполнение анкеты через бот\n\nВведите ваше имя:"
    
    await callback.message.edit_text(text)
    await state.set_state(FormStates.waiting_name)
    await callback.answer()


@router.message(FormStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка введенного имени"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Пожалуйста, введите имя еще раз:")
        return
    
    await state.update_data(name=name)
    await message.answer("📞 Теперь введите ваш номер телефона:")
    await state.set_state(FormStates.waiting_phone)


@router.message(FormStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка введенного телефона"""
    phone = message.text.strip()
    
    # Простая валидация
    phone_clean = re.sub(r'[^\d+]', '', phone)
    if len(phone_clean) < 10:
        await message.answer("❌ Номер телефона некорректный. Пожалуйста, введите номер еще раз:")
        return
    
    data = await state.get_data()
    name = data.get("name")
    
    telegram_id = message.from_user.id

    result = await api_client.update_user_form(telegram_id, name, phone, via_bot=True)
    
    if result:
        await message.answer(
            f"✅ Данные успешно сохранены!\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n\n"
            f"Ваш лид в Битрикс24 обновлен.",
            reply_markup=get_main_keyboard(telegram_id)
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при сохранении данных. Попробуйте позже.",
            reply_markup=get_main_keyboard(telegram_id)
        )
    
    await state.clear()


# Не будет работать потому что нужно захостить сервис, у меня такой возможности нет
@router.callback_query(F.data == "form_webapp")
async def start_form_webapp(callback: CallbackQuery):
    """Открытие формы через webapp"""
    telegram_id = callback.from_user.id
    
    try:
        keyboard = get_webapp_keyboard(telegram_id)
        text = (
            "🌐 Заполнение анкеты через webapp\n\n"
            "Нажмите на кнопку ниже, чтобы открыть форму в браузере."
        )
        await callback.message.edit_text(
            text,
            reply_markup=keyboard
        )
    except ValueError as e:
        await callback.message.edit_text(
            "❌ Ошибка: WebApp недоступен.\n\n"
            "Для работы WebApp требуется публичный HTTPS URL.\n"
            "Пожалуйста, используйте анкету через бот или обратитесь к администратору."
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Произошла ошибка при открытии формы: {str(e)}"
        )
    
    await callback.answer()

