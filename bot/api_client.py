import logging

import httpx
from typing import Optional, Dict, Any

from bot.config import BotConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class APIClient:
    """Клиент для работы с API"""

    def __init__(self, base_url: str = BotConfig.API_URL):
        self.base_url = base_url.rstrip("/")

    async def create_user(self, telegram_id: int, username: str) -> Optional[Dict[str, Any]]:
        """Создать пользователя"""
        url = f"{self.base_url}/users/new"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(url, json={
                    "telegram_id": telegram_id,
                    "username": username or str(telegram_id)
                })
                if response.status_code == 201:
                    return response.json()
                elif response.status_code == 409:
                    return await self.get_user(telegram_id)
                return None
            except Exception:
                return None

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя"""
        url = f"{self.base_url}/users/{telegram_id}"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None

    async def is_admin(self, telegram_id: int) -> bool:
        """Проверить админ"""
        url = f"{self.base_url}/users/{telegram_id}/is_admin"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("is_admin", False)
                return False
            except Exception:
                return False

    async def get_user_form(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить форму пользователя"""
        url = f"{self.base_url}/users/{telegram_id}/form"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None

    async def update_user_form(self, telegram_id: int, name: str, phone: str, via_bot: bool) -> Optional[Dict[str, Any]]:
        """Обновить форму пользователя"""
        url = f"{self.base_url}/users/{telegram_id}/form"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(url, json={
                    "name": name,
                    "phone": phone,
                    "via_bot": via_bot
                })
                if response.status_code in [200, 201]:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error updating form: {e}")
                return None


    async def update_user_active(self, telegram_id: int, is_active: bool) -> Optional[Dict[str, Any]]:
        """Обновить статус активности пользователя"""
        url = f"{self.base_url}/users/{telegram_id}/active"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.patch(url, params={"is_active": is_active})
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error updating user: {e}")
                return None

    async def get_users_statistics(self) -> Dict[str, int]:
        """Получить статистику пользователей"""
        url = f"{self.base_url}/users/statistics"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "total": data.get("total", 0),
                        "active": data.get("active", 0),
                        "bitrix_leads": data.get("bitrix_leads", 0)
                    }
                logger.error(f"Error getting statistics: {response.status_code} - {response.text}")
                return {"total": 0, "active": 0}
            except Exception as e:
                logger.error(f"Exception getting statistics: {e}")
                return {"total": 0, "active": 0}

    async def get_ai_answer(self, text: str) -> Optional[str]:
        """Получить ответ от AI"""
        url = f"{self.base_url}/answer"
        async with httpx.AsyncClient(timeout=300) as client:
            try:
                response = await client.post(url, json={"text": text})
                logger.debug(response)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("answer")
                return None
            except Exception:
                return None

