from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Admin
from app.schema import AdminDto


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Optional[AdminDto]:
        stmt = (
            select(Admin)
            .where(Admin.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            return None
        return AdminDto.from_orm(admin)
