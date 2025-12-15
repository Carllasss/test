from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.asyncSession import AsyncSessionLocal, get_async_db
from app.repo.admin import AdminRepository
from app.repo.bitrix import BitrixRepository
from app.repo.form import FormRepository
from app.repo.user import UserRepository


class UnitOfWork:
    """Единая точка управления репозиториями в рамках одной транзакции."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._repositories: dict[str, object] = {}

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    @property
    def users(self) -> UserRepository:
        if "users" not in self._repositories:
            self._repositories["users"] = UserRepository(self.db)
        return self._repositories["users"]

    @property
    def forms(self) -> FormRepository:
        if "forms" not in self._repositories:
            self._repositories["forms"] = FormRepository(self.db)
        return self._repositories["forms"]

    @property
    def bitrix(self) -> BitrixRepository:
        if "bitrix" not in self._repositories:
            self._repositories["bitrix"] = BitrixRepository(self.db)
        return self._repositories["bitrix"]

    @property
    def admins(self) -> AdminRepository:
        if "admins" not in self._repositories:
            self._repositories["admins"] = AdminRepository(self.db)
        return self._repositories["admins"]


@asynccontextmanager
async def create_uow(session_factory: async_sessionmaker[AsyncSession] = AsyncSessionLocal) -> AsyncIterator[UnitOfWork]:
    """
    Вспомогательная фабрика для создания UoW вне FastAPI DI.
    """
    async with session_factory() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise


async def get_uow(db: AsyncSession = Depends(get_async_db)) -> AsyncIterator[UnitOfWork]:
    """
    Dependency
    """
    uow = UnitOfWork(db)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise