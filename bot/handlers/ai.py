from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.api_client import APIClient

router = Router()
api_client = APIClient()


@router.message(F.text)
async def handle_text_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений вне контекста бота.
    Если пользователь не находится в состоянии FSM  отправляем в ии.
    """
    # Проверяем находится ли пользователь в состоянии FSM
    current_state = await state.get_state()
    
    # Если пользователь заполняет форму не лезем
    if current_state is not None:
        return
    
    if message.text.startswith('/'):
        return
    
    answer = await api_client.get_ai_answer(message.text)
    
    if answer:
        await message.answer(answer)
    else:
        await message.answer("Извините, сервис временно недоступен. Попробуйте позже.")

