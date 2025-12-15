from __future__ import annotations

from datetime import datetime
from typing import Optional
from unittest import mock

import pytest

from app.schema import BitrixLeadDTO, FormDTO, UserCreate, UserDTO
from app.schema.form import FormUpdate
from app.service.errors import UserAlreadyExists
from app.service.service import Service


def _user_dto(id_: int, user: UserCreate, is_active: bool = True) -> UserDTO:
    return UserDTO(
        id=id_,
        telegram_id=user.telegram_id,
        username=user.username,
        is_active=is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_activity=datetime.utcnow(),
    )


def _form_dto(id_: int, user_id: int, update: FormUpdate) -> FormDTO:
    return FormDTO(
        id=id_,
        user_id=user_id,
        name=update.name,
        phone=update.phone,
        via_bot=update.via_bot,
    )


@pytest.fixture()
def uow() -> mock.MagicMock:
    users_store: dict[int, UserDTO] = {}
    bitrix_store: dict[int, BitrixLeadDTO] = {}
    forms_store: list[FormDTO] = []

    users_repo = mock.MagicMock()
    bitrix_repo = mock.MagicMock()
    forms_repo = mock.MagicMock()
    admins_repo = mock.MagicMock()

    async def users_create(user: UserCreate) -> UserDTO:
        if user.telegram_id in users_store:
            return users_store[user.telegram_id]
        dto = _user_dto(len(users_store) + 1, user)
        users_store[user.telegram_id] = dto
        return dto

    async def users_get_by_telegram_id(telegram_id: int) -> Optional[UserDTO]:
        return users_store.get(telegram_id)

    async def users_update_active(telegram_id: int, is_active: bool) -> Optional[UserDTO]:
        dto = users_store.get(telegram_id)
        if not dto:
            return None
        updated = dto.copy(update={"is_active": is_active, "last_activity": datetime.utcnow()})
        users_store[telegram_id] = updated
        return updated

    async def users_count_all() -> int:
        return len(users_store)

    async def users_count_active() -> int:
        return len([u for u in users_store.values() if u.is_active])

    users_repo.create = mock.AsyncMock(side_effect=users_create)
    users_repo.get_by_telegram_id = mock.AsyncMock(side_effect=users_get_by_telegram_id)
    users_repo.set_user_admin = mock.AsyncMock(side_effect=users_get_by_telegram_id)
    users_repo.update_active_status = mock.AsyncMock(side_effect=users_update_active)
    users_repo.count_all = mock.AsyncMock(side_effect=users_count_all)
    users_repo.count_active = mock.AsyncMock(side_effect=users_count_active)

    async def bitrix_create(data) -> BitrixLeadDTO:
        dto = BitrixLeadDTO(
            id=len(bitrix_store) + 1,
            user_id=data.user_id,
            lead_id=data.lead_id,
            created_at=datetime.utcnow(),
        )
        bitrix_store[data.user_id] = dto
        return dto

    async def bitrix_get_by_user_id(user_id: int) -> Optional[BitrixLeadDTO]:
        return bitrix_store.get(user_id)

    async def bitrix_count_all() -> int:
        return len(bitrix_store)

    bitrix_repo.create = mock.AsyncMock(side_effect=bitrix_create)
    bitrix_repo.get_by_user_id = mock.AsyncMock(side_effect=bitrix_get_by_user_id)
    bitrix_repo.count_all = mock.AsyncMock(side_effect=bitrix_count_all)

    async def forms_create(form) -> FormDTO:
        dto = _form_dto(len(forms_store) + 1, form.user_id, form)
        forms_store.append(dto)
        return dto

    async def forms_get_last_by_user_id(user_id: int) -> Optional[FormDTO]:
        for f in reversed(forms_store):
            if f.user_id == user_id:
                return f
        return None

    forms_repo.create = mock.AsyncMock(side_effect=forms_create)
    forms_repo.get_last_by_user_id = mock.AsyncMock(side_effect=forms_get_last_by_user_id)

    admins_repo.get_by_user_id = mock.AsyncMock(return_value=None)

    uow_mock = mock.MagicMock()
    uow_mock.users = users_repo
    uow_mock.bitrix = bitrix_repo
    uow_mock.forms = forms_repo
    uow_mock.admins = admins_repo
    uow_mock.commit = mock.AsyncMock()
    uow_mock.rollback = mock.AsyncMock()

    uow_mock._stores = {
        "users": users_store,
        "bitrix": bitrix_store,
        "forms": forms_store,
    }
    return uow_mock


@pytest.fixture()
def service(uow: mock.MagicMock) -> Service:
    svc = Service(uow)
    bitrix_client = mock.MagicMock()

    async def create_lead(payload: dict) -> int:
        return len(uow._stores["bitrix"]) + 100

    async def update_lead(lead_id: int, payload: dict) -> None:
        return None

    bitrix_client.create_lead = mock.AsyncMock(side_effect=create_lead)
    bitrix_client.update_lead = mock.AsyncMock(side_effect=update_lead)
    svc.bitrix_client = bitrix_client
    return svc


# ======= Tests =======
@pytest.mark.asyncio
async def test_create_user_raises_when_exists(service: Service):
    first = UserCreate(telegram_id=1, username="user1")
    await service.create_user(first)

    with pytest.raises(UserAlreadyExists):
        await service.create_user(first)


@pytest.mark.asyncio
async def test_get_or_create_returns_existing(service: Service):
    user = UserCreate(telegram_id=2, username="existing")
    created = await service.create_user(user)

    result = await service.get_or_create_user(telegram_id=2, username="other")

    assert result.id == created.id
    assert result.username == created.username


@pytest.mark.asyncio
async def test_get_or_create_creates_new_user(service: Service):
    result = await service.get_or_create_user(telegram_id=3, username="new_user")

    assert result.telegram_id == 3
    assert result.username == "new_user"


@pytest.mark.asyncio
async def test_change_user_form_creates_form_and_syncs_bitrix(service: Service, uow: mock.MagicMock):
    user = await service.create_user(UserCreate(telegram_id=10, username="user10"))

    update = FormUpdate(name="Name", phone="+123", via_bot=True)
    created_form = await service.change_user_form(telegram_id=user.telegram_id, form=update)

    assert created_form is not None
    assert created_form.user_id == user.id
    assert len(uow._stores["bitrix"]) == 1
    service.bitrix_client.create_lead.assert_awaited()


@pytest.mark.asyncio
async def test_create_lead_on_start_skips_when_no_user(service: Service):
    lead_id = await service.create_lead_on_start(telegram_id=999)

    assert lead_id is None


@pytest.mark.asyncio
async def test_create_lead_on_start_creates_bitrix_lead(service: Service, uow: mock.MagicMock):
    user = await service.create_user(UserCreate(telegram_id=42, username="tg42"))

    lead_id = await service.create_lead_on_start(telegram_id=user.telegram_id)

    assert lead_id is not None
    assert uow._stores["bitrix"].get(user.id) is not None


@pytest.mark.asyncio
async def test_statistics(service: Service):
    await service.create_user(UserCreate(telegram_id=201, username="u1"))
    await service.create_user(UserCreate(telegram_id=202, username="u2"))
    await service.create_lead_on_start(telegram_id=201)

    stats = await service.get_users_statistics()

    assert stats["total"] == 2
    assert stats["active"] == 2
    assert stats["bitrix_leads"] == 1
