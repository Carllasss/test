from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schema import FormCreate, FormDTO, UserCreate, UserDTO
from app.schema.form import FormUpdate
from app.schema.rag import Message
from app.service.errors import UserAlreadyExists
from app.service.ai import answer_user_message
from app.service.service import Service, get_service

router = APIRouter(prefix="/api", tags=["api"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/users/new", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: Service = Depends(get_service)) -> UserDTO:
    try:
        user = await service.create_user(payload)
        await service.create_lead_on_start(payload.telegram_id)
        return user
    except UserAlreadyExists as exc:
        user = await service.get_user(payload.telegram_id)
        if user:
            await service.create_lead_on_start(payload.telegram_id)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/users/{telegram_id}/make_admin", response_model=UserDTO)
async def make_admin(telegram_id: int, admin: bool, service: Service = Depends(get_service)) -> UserDTO:
    user = await service.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await service.set_admin(telegram_id, admin)
    return user


@router.get("/users/statistics")
async def get_users_statistics(service: Service = Depends(get_service)) -> dict[str, int]:
    """Получить статистику пользователей"""
    return await service.get_users_statistics()


@router.get("/users/{telegram_id}", response_model=UserDTO)
async def get_user(telegram_id: int, service: Service = Depends(get_service)) -> UserDTO:
    user = await service.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/users/{telegram_id}/is_admin")
async def is_admin(telegram_id: int, service: Service = Depends(get_service)) -> dict[str, bool]:
    return {"is_admin": await service.is_user_admin(telegram_id)}


@router.patch("/users/{telegram_id}/active", response_model=UserDTO)
async def update_user_active(
    telegram_id: int,
    is_active: bool = Query(True, description="Статус активности пользователя"),
    service: Service = Depends(get_service)
) -> UserDTO:
    """Обновить статус активности пользователя"""
    user = await service.update_user_active(telegram_id, is_active)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/users/{telegram_id}/form", response_model=FormDTO | None)
async def get_user_form(telegram_id: int, service: Service = Depends(get_service)) -> FormDTO | None:
    return await service.get_user_form(telegram_id)


@router.post("/users/{telegram_id}/form", response_model=FormDTO, status_code=status.HTTP_201_CREATED)
async def upsert_user_form(
    telegram_id: int,
    payload: FormUpdate,
    service: Service = Depends(get_service),
) -> FormDTO:
    form = await service.change_user_form(telegram_id, payload)
    if form is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return form


@router.get(
    "/web/users/{telegram_id}/form",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def web_form(
    telegram_id: int,
    request: Request,
    service: Service = Depends(get_service),
):
    existing = await service.get_user_form(telegram_id)
    name_val = existing.name if existing else ""
    phone_val = existing.phone if existing else ""
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "telegram_id": telegram_id,
            "name": name_val,
            "phone": phone_val,
            "message": None,
            "is_error": False,
        },
    )


@router.post(
    "/web/users/{telegram_id}/form",
    response_class=HTMLResponse,
)
async def web_form_submit(
    request: Request,
    telegram_id: int,
    name: str = Form(...),
    phone: str = Form(...),
    service: Service = Depends(get_service),
):
    form = await service.change_user_form(
        telegram_id,
        FormUpdate(name=name, phone=phone, via_bot=False),
    )
    if form is None:
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "telegram_id": telegram_id,
                "name": name,
                "phone": phone,
                "message": "User not found",
                "is_error": True,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "telegram_id": telegram_id,
            "name": form.name,
            "phone": form.phone,
            "message": "Saved successfully",
            "is_error": False,
        },
    )




@router.post("/answer")
async def rag_answer(msg: Message):
    reply = await answer_user_message(msg.text)
    return {"answer": reply}