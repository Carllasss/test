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

    async def set_user_admin(self, telegram_id: int, admin: bool) -> Optional[UserDTO]:
        """Установить или снять админские права пользователя"""
        from app.model.models import Admin
        from datetime import datetime
        
        # Находим пользователя
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Проверяем, есть ли уже запись админа
        admin_stmt = select(Admin).where(Admin.user_id == user.id)
        admin_result = await self.db.execute(admin_stmt)
        existing_admin = admin_result.scalar_one_or_none()
        
        if admin:
            # Нужно сделать админом
            if not existing_admin:
                # Создаем запись админа
                new_admin = Admin(
                    user_id=user.id,
                    created_at=datetime.utcnow(),
                    last_activity=datetime.utcnow()
                )
                self.db.add(new_admin)
                await self.db.flush()
        else:
            # Нужно убрать админские права
            if existing_admin:
                # Удаляем запись админа
                await self.db.delete(existing_admin)
                await self.db.flush()
        
        if admin and existing_admin:
            existing_admin.last_activity = datetime.utcnow()
            await self.db.flush()

        await self.db.refresh(user)
        return UserDTO.from_orm(user)


    async def get_by_id(self, user_id: int) -> Optional[UserDTO]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        userDto = UserDTO.from_orm(user)
        return userDto

    async def count_all(self) -> int:
        """Подсчет всех пользователей в БД"""
        from sqlalchemy import func
        stmt = select(func.count(User.id))
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def count_active(self) -> int:
        """Подсчет активных пользователей (не заблокировавших бота)"""
        from sqlalchemy import func
        stmt = select(func.count(User.id)).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def update_active_status(self, telegram_id: int, is_active: bool) -> Optional[UserDTO]:
        """Обновить статус активности пользователя"""
        from datetime import datetime
        
        # Находим пользователя
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Обновляем статус напрямую в объекте
        user.is_active = is_active
        user.last_activity = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(user)
        
        return UserDTO.from_orm(user)