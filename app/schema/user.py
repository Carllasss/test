from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: int = Field(..., gt=0)
    username: str = Field(..., max_length=255)


class UserUpdate(BaseModel):
    telegram_id: int
    is_active: bool | None = True
    last_activity: datetime | None = datetime.utcnow()

class UserDTO(BaseModel):
    id: int
    telegram_id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True