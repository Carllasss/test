from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.router import router as api_router
from app.db.asyncSession import init_db
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Test API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)


def main():
    uvicorn.run(
        "main:app",
        host=settings.WEBAPP_HOST,
        port=settings.WEBAPP_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
