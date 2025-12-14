from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, RESTRICTED

from bot.api_client import APIClient

router = Router()
api_client = APIClient()

# KICKED >> MEMBER - пользователь был заблокирован (KICKED), теперь стал активным (MEMBER)
# LEFT >> MEMBER   - пользователь покинул чат (LEFT), теперь вернулся (MEMBER)
# RESTRICTED >> MEMBER - пользователь был ограничен, теперь снова активен

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED >> MEMBER))
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT >> MEMBER))
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=RESTRICTED >> MEMBER))
async def user_unblocked(event: ChatMemberUpdated):
    """
    Пользователь разблокировал бота или вернулся в чат.
    """
    telegram_id = event.from_user.id
    await api_client.update_user_active(telegram_id, is_active=True)

# MEMBER >> KICKED   - пользователь был активен (MEMBER), теперь заблокировал бота (KICKED)
# MEMBER >> LEFT     - пользователь был активен, теперь покинул чат (LEFT)
# MEMBER >> RESTRICTED - пользователь был активен, теперь ограничен

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> KICKED))
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> LEFT))
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> RESTRICTED))
async def user_blocked(event: ChatMemberUpdated):
    """
    Пользователь заблокировал бота или покинул чат.
    """
    telegram_id = event.from_user.id
    await api_client.update_user_active(telegram_id, is_active=False)
