from pydantic import BaseModel, Field


class FormCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    name: str
    phone: str
    via_bot: bool

class FormDTO(FormCreate):
    id: int

    class Config:
        from_attributes = True
