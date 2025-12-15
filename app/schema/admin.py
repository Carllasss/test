from datetime import datetime

from pydantic import BaseModel


class AdminDto(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True
