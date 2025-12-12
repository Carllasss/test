from typing import Optional

from fastapi import Depends

from app.repo.uow import UnitOfWork, get_uow
from app.schema import BitrixLeadCreate, FormCreate, FormDTO, UserCreate, UserDTO
from app.schema.form import FormUpdate
from app.service.errors import UserAlreadyExists
from app.utils.bitrix import Bitrix24Client, BitrixClientError
from app.config.settings import settings


class Service:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.bitrix_client = Bitrix24Client.from_settings(settings)

    async def get_user(self, telegram_id: int) -> Optional[UserDTO]:
        return await self.uow.users.get_by_telegram_id(telegram_id)

    async def create_user(self, user: UserCreate) -> UserDTO:
        exists = await self.uow.users.get_by_telegram_id(user.telegram_id)
        if exists:
            raise UserAlreadyExists(user.telegram_id)

        created_user = await self.uow.users.create(user)
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
        created_form = await self.uow.forms.create(form_with_user)
        await self._sync_bitrix_lead(form_with_user)
        return created_form

    async def _sync_bitrix_lead(self, form: FormCreate) -> Optional[int]:
        """
        Создает или обновляет лид в Bitrix24 на основе последних данных формы.
        Если клиент не сконфигурирован, просто пропускаем синхронизацию.
        """
        if not self.bitrix_client:
            return None

        payload = {
            "TITLE": f"Лид: {form.name}",
            "NAME": form.name,
            "PHONE": [{"VALUE": form.phone, "VALUE_TYPE": "WORK"}],
            "COMMENTS": f"Получено через бота: {form.via_bot}",
        }

        existing_lead = await self.uow.bitrix.get_by_user_id(form.user_id)

        try:
            if existing_lead:
                await self.bitrix_client.update_lead(existing_lead.lead_id, payload)
                return existing_lead.lead_id

            lead_id = await self.bitrix_client.create_lead(payload)
            await self.uow.bitrix.create(
                BitrixLeadCreate(
                    user_id=form.user_id,
                    lead_id=lead_id,
                )
            )
            return lead_id
        except BitrixClientError:
            return None


async def get_service(uow: UnitOfWork = Depends(get_uow)) -> Service:
    """
    FastAPI dependency для получения Service c активной транзакцией UnitOfWork.
    """
    return Service(uow)