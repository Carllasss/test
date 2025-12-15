from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, RESTRICTED

from bot.api_client import APIClient

router = Router()
api_client = APIClient()


# KICKED >> MEMBER - пользователь был ограничен, теперь снова активен

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked(event: ChatMemberUpdated):
    """
    Пользователь разблокировал бота или вернулся в чат.
    """
    telegram_id = event.from_user.id
    await api_client.update_user_active(telegram_id, is_active=True)

# MEMBER >> KICKED   - пользователь был активен (MEMBER), теперь заблокировал бота (KICKED)

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked(event: ChatMemberUpdated):
    """
    Пользователь заблокировал бота или покинул чат.
    """
    telegram_id = event.from_user.id
    await api_client.update_user_active(telegram_id, is_active=False)
