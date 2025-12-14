from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_client import APIClient
from bot.keyboards import get_main_keyboard, get_admin_keyboard
from bot.handlers.form import FormStates

router = Router()
api_client = APIClient()


class StartStates(StatesGroup):
    waiting = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    telegram_id = message.from_user.id
    username = message.from_user.username or ""

    user = await api_client.create_user(telegram_id, username)

    is_admin = await api_client.is_admin(telegram_id)

    if is_admin:
        await message.answer(
            "👋 Добро пожаловать, администратор!",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать! Выберите способ заполнения анкеты:",
            reply_markup=get_main_keyboard(telegram_id)
        )

