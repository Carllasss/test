from typing import Type, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from contextlib import AbstractContextManager, contextmanager

from app.db.asyncSession import get_async_db
from app.repo.user import UserRepository
from app.repo.form import FormRepository
from app.repo.bitrix import BitrixRepository
from app.repo.admin import AdminRepository


class UnitOfWork:
    """Управление всеми репозиториями в одной транзакции"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._repositories = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    @property
    def users(self) -> UserRepository:
        if 'users' not in self._repositories:
            self._repositories['users'] = UserRepository(self.db)
        return self._repositories['users']

    @property
    def forms(self) -> FormRepository:
        if 'forms' not in self._repositories:
            self._repositories['forms'] = FormRepository(self.db)
        return self._repositories['forms']

    @property
    def bitrix(self) -> BitrixRepository:
        if 'bitrix' not in self._repositories:
            self._repositories['bitrix'] = BitrixRepository(self.db)
        return self._repositories['bitrix']

    @property
    def admins(self) -> AdminRepository:
        if 'admins' not in self._repositories:
            self._repositories['admins'] = AdminRepository(self.db)
        return self._repositories['admins']


class UnitOfWorkFactory:
    """Фабрика для создания UnitOfWork"""

    @staticmethod
    @contextmanager
    def create() -> AbstractContextManager[UnitOfWork]:
        """Создать UnitOfWork с контекстным менеджером"""
        db = get_async_db()
        try:
            uow = UnitOfWork(db)
            yield uow
            uow.commit()
        except Exception:
            uow.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def get_uow(db: Session) -> UnitOfWork:
        """Получить UnitOfWork для существующей сессии"""
        return UnitOfWork(db)