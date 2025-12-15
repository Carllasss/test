# Test API

## Старт (Docker)
1. Создать `.env` по образцу `env.example`. (подменить в docker-compose) либо дополнить существующий `env.example`.
2. Поднять докер: `docker-compose up --build`.
3. Выполнить миграции: `docker-compose exec api alembic upgrade head`.
4. Открыть swagger: http://localhost:8000/docs#.

## Требования

- Запущенный API сервер (из папки `app`) или через Docker
- Настроенный `BOT_TOKEN` в env
- Настроенный `BITRIX24_WEBHOOK_URL` (опционально)
- В корне проекта должен лежать файл 'service_account.json' из Google Cloud API
- Расширить доступную оперативную память под докер до 4 гб (из-за модели)

## Тесты
- Для тестов `uv sync`, затем `uv run pytest -W "ignore::DeprecationWarning"`.