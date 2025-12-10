# Test API

## старт (локально)
1. Создать `.env` по образцу `env.example`.
2. Поднять докер: `docker-compose up --build`.
3. Выполнить миграции: `docker-compose exec api alembic upgrade head`.
4. Открыть swagger: http://localhost:8000/docs#.