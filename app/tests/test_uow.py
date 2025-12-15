from __future__ import annotations

from unittest import mock

import pytest

from app.repo.uow import UnitOfWork


@pytest.fixture()
def session() -> mock.MagicMock:
    sess = mock.MagicMock()
    sess.commit = mock.AsyncMock()
    sess.rollback = mock.AsyncMock()
    return sess


@pytest.mark.asyncio
async def test_commit_calls_session_commit(session: mock.MagicMock):
    uow = UnitOfWork(session)

    await uow.commit()

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rollback_calls_session_rollback(session: mock.MagicMock):
    uow = UnitOfWork(session)

    await uow.rollback()

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_context_manager_commits_on_success(session: mock.MagicMock):
    async with UnitOfWork(session):
        pass

    session.commit.assert_awaited_once()
    session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_context_manager_rolls_back_on_error(session: mock.MagicMock):
    with pytest.raises(RuntimeError):
        async with UnitOfWork(session):
            raise RuntimeError("boom")

    session.rollback.assert_awaited_once()
    session.commit.assert_not_called()


def test_repositories_are_singletons_per_uow(session: mock.MagicMock):
    uow = UnitOfWork(session)

    assert uow.users is uow.users
    assert uow.forms is uow.forms
    assert uow.bitrix is uow.bitrix
    assert uow.admins is uow.admins

    assert uow.users.db is session
    assert uow.forms.db is session
    assert uow.bitrix.db is session
    assert uow.admins.db is session
