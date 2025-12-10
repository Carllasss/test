from datetime import datetime
from typing import Optional

from fastapi import Depends

from app.repo.uow import UnitOfWork, get_uow
from app.schema import BitrixLeadCreate, FormCreate, FormDTO, UserCreate, UserDTO
from app.schema.form import FormUpdate
from app.service.errors import UserAlreadyExists


class Service:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_user(self, telegram_id: int) -> Optional[UserDTO]:
        return await self.uow.users.get_by_telegram_id(telegram_id)

    async def create_user(self, user: UserCreate) -> UserDTO:
        exists = await self.uow.users.get_by_telegram_id(user.telegram_id)
        if exists:
            raise UserAlreadyExists(user.telegram_id)

        created_user = await self.uow.users.create(user)
        await self._create_bitrix_lead(created_user.id)
        return created_user

    async def is_user_admin(self, telegram_id: int) -> bool:
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return False

        admin = await self.uow.admins.get_by_user_id(user_id=user.id)
        return admin is not None

    async def get_user_form(self, telegram_id: int) -> Optional[FormDTO]:
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return None
        form = await self.uow.forms.get_last_by_user_id(user_id=user.id)
        return form

    async def change_user_form(self, telegram_id: int, form: FormUpdate) -> Optional[FormDTO]:
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return None

        form_with_user = FormCreate(
            user_id=user.id,
            name=form.name,
            phone=form.phone,
            via_bot=form.via_bot,
        )
        return await self.uow.forms.create(form_with_user)

    async def _create_bitrix_lead(self, user_id: int) -> Optional[int]:
        """
        Создать лид в Битрикс24.
        Сейчас заглушка, сохраняем в БД псевдо-идентификатор.
        """
        lead_id = int(datetime.utcnow().timestamp())
        await self.uow.bitrix.create(
            BitrixLeadCreate(
                user_id=user_id,
                lead_id=lead_id,
            )
        )
        return lead_id


async def get_service(uow: UnitOfWork = Depends(get_uow)) -> Service:
    """
    FastAPI dependency для получения Service c активной транзакцией UnitOfWork.
    """
    return Service(uow)