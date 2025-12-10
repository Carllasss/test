from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import User
from app.schema import UserCreate, UserDTO


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: UserCreate) -> UserDTO:
        db_user = User(
            telegram_id=user.telegram_id,
            username=user.username,
        )

        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        userDto = UserDTO.from_orm(db_user)
        return userDto

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[UserDTO]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        userDto = UserDTO.from_orm(user)
        return userDto

    async def get_by_id(self, user_id: int) -> Optional[UserDTO]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        userDto = UserDTO.from_orm(user)
        return userDto
