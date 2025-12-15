from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import BitrixLead
from app.schema import BitrixLeadCreate, BitrixLeadDTO


class BitrixRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: BitrixLeadCreate) -> BitrixLeadDTO:
        db_bitrix = BitrixLead(
            user_id=data.user_id,
            lead_id=data.lead_id,
        )
        self.db.add(db_bitrix)
        await self.db.flush()
        await self.db.refresh(db_bitrix)
        bitrixDto = BitrixLeadDTO.from_orm(db_bitrix)
        return bitrixDto

    async def get_by_user_id(self, user_id: int) -> Optional[BitrixLeadDTO]:
        stmt = (
            select(BitrixLead)
            .where(BitrixLead.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        bitrixLead = result.scalar_one_or_none()
        if not bitrixLead:
            return None
        return BitrixLeadDTO.from_orm(bitrixLead)

    async def count_all(self) -> int:
        """Подсчет всех лидов в Bitrix24"""
        from sqlalchemy import func
        stmt = select(func.count(BitrixLead.id))
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0