from pydantic import BaseModel, Field

class FormUpdate(BaseModel):
    name: str
    phone: str
    via_bot: bool


class FormCreate(FormUpdate):
    user_id: int = Field(..., gt=0)

class FormDTO(FormCreate):
    id: int

    class Config:
        from_attributes = True
