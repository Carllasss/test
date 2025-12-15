from datetime import datetime

from pydantic import BaseModel, Field


class BitrixLeadCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    lead_id: int


class BitrixLeadDTO(BitrixLeadCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
