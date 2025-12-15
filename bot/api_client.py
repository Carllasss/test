import asyncio
import logging
from typing import Optional, Dict, Any

import httpx

from bot.config import BotConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class APIClient:
    """Клиент для работы с API"""

    def __init__(self, base_url: str = BotConfig.API_URL, retries: int = 3, backoff: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.retries = max(1, retries)
        self.backoff = max(0.0, backoff)

    async def _request(self, method: str, path: str, **kwargs) -> Optional[httpx.Response]:
        url = f"{self.base_url}{path}"
        delay = self.backoff
        last_exc: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=kwargs.pop("timeout", 10)) as client:
                    response = await client.request(method, url, **kwargs)
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"Server error {response.status_code}", request=response.request, response=response
                    )
                return response
            except Exception as exc:
                last_exc = exc
                if attempt == self.retries:
                    break
                logger.warning(
                    "API request failed (attempt %s/%s): %s",
                    attempt,
                    self.retries,
                    exc,
                )
                await asyncio.sleep(delay)
                delay *= 2

        logger.error("API request failed after %s attempts: %s", self.retries, last_exc)
        return None

    async def create_user(self, telegram_id: int, username: str) -> Optional[Dict[str, Any]]:
        """Создать пользователя"""
        response = await self._request(
            "post",
            "/users/new",
            json={"telegram_id": telegram_id, "username": username or str(telegram_id)},
        )
        if response is None:
            return None
        if response.status_code == 201:
            return response.json()
        if response.status_code == 409:
            return await self.get_user(telegram_id)
        return None

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя"""
        response = await self._request("get", f"/users/{telegram_id}")
        if response and response.status_code == 200:
            return response.json()
        return None

    async def is_admin(self, telegram_id: int) -> bool:
        """Проверить админ"""
        response = await self._request("get", f"/users/{telegram_id}/is_admin")
        if response and response.status_code == 200:
            data = response.json()
            return data.get("is_admin", False)
        return False

    async def get_user_form(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить форму пользователя"""
        response = await self._request("get", f"/users/{telegram_id}/form")
        if response and response.status_code == 200:
            return response.json()
        return None

    async def update_user_form(self, telegram_id: int, name: str, phone: str, via_bot: bool) -> Optional[Dict[str, Any]]:
        """Обновить форму пользователя"""
        response = await self._request(
            "post",
            f"/users/{telegram_id}/form",
            json={"name": name, "phone": phone, "via_bot": via_bot},
        )
        if response and response.status_code in (200, 201):
            return response.json()
        return None


    async def update_user_active(self, telegram_id: int, is_active: bool) -> Optional[Dict[str, Any]]:
        """Обновить статус активности пользователя"""
        response = await self._request(
            "patch",
            f"/users/{telegram_id}/active",
            params={"is_active": is_active},
        )
        if response and response.status_code == 200:
            return response.json()
        return None

    async def get_users_statistics(self) -> Dict[str, int]:
        """Получить статистику пользователей"""
        response = await self._request("get", "/users/statistics")
        if response and response.status_code == 200:
            data = response.json()
            return {
                "total": data.get("total", 0),
                "active": data.get("active", 0),
                "bitrix_leads": data.get("bitrix_leads", 0),
            }
        if response:
            logger.error("Error getting statistics: %s - %s", response.status_code, response.text)
        return {"total": 0, "active": 0}

    async def get_ai_answer(self, text: str) -> Optional[str]:
        """Получить ответ от AI"""
        response = await self._request("post", "/answer", json={"text": text}, timeout=300)
        if response and response.status_code == 200:
            data = response.json()
            return data.get("answer")
        return None

