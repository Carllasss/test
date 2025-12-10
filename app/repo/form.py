from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import FormHistory
from app.schema import FormDTO, FormCreate


class FormRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, form: FormCreate) -> FormDTO:
        db_form = FormHistory(
            user_id=form.user_id,
            name=form.name,
            phone=form.phone,
            via_bot=form.via_bot,
        )

        self.db.add(db_form)
        await self.db.commit()
        await self.db.refresh(db_form)
        formDto = FormDTO.from_orm(db_form)
        return formDto

    async def get_last_by_user_id(self, user_id: int) -> Optional[FormDTO]:
        stmt = (
            select(FormHistory)
            .where(FormHistory.user_id == user_id)
            .order_by(desc(FormHistory.created_at))
            .limit(1)
        )

        result = await self.db.execute(stmt)
        form = result.scalar_one_or_none()

        return FormDTO.from_orm(form) if form else None

