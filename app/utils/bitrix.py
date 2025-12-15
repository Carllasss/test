import asyncio
import logging
from typing import Any, Dict, Optional

import httpx


class BitrixClientError(Exception):
    """Ошибки при работе с Bitrix24."""


logger = logging.getLogger(__name__)


class Bitrix24Client:
    """Клиент для работы по входящему вебхуку Bitrix24."""

    def __init__(self, base_url: str, retries: int = 3, backoff: float = 0.5):
        if not base_url:
            raise ValueError("Bitrix24 base_url is required")
        self.base_url = base_url.rstrip("/")
        self.retries = max(1, retries)
        self.backoff = max(0.0, backoff)

    @classmethod
    def from_settings(cls, settings: Any) -> Optional["Bitrix24Client"]:
        """
        Создает клиент из настроек.
        """
        if settings.BITRIX24_WEBHOOK_URL:
            return cls(settings.BITRIX24_WEBHOOK_URL)

        return None

    async def create_lead(self, fields: Dict[str, Any]) -> int:
        response = await self._post("crm.lead.add", {"fields": fields})
        result = response.get("result")
        if not isinstance(result, int):
            raise BitrixClientError("Unexpected response for lead creation")
        return result

    async def update_lead(self, lead_id: int, fields: Dict[str, Any]) -> None:
        await self._post("crm.lead.update", {"ID": lead_id, "fields": fields})

    async def _post(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST with simple retry/backoff on transport and HTTP errors."""
        url = f"{self.base_url}/{method}.json"
        delay = self.backoff
        last_exc: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and data.get("error"):
                    raise BitrixClientError(
                        f"{data.get('error')}: {data.get('error_description')}"
                    )
                if not isinstance(data, dict):
                    raise BitrixClientError("Unexpected response format from Bitrix24")
                return data
            except (httpx.HTTPError, BitrixClientError) as exc:
                last_exc = exc
                if attempt == self.retries:
                    break
                logger.warning(
                    "Bitrix request failed (attempt %s/%s): %s",
                    attempt,
                    self.retries,
                    exc,
                )
                await asyncio.sleep(delay)
                delay *= 2

        raise BitrixClientError(f"Bitrix request failed after {self.retries} attempts") from last_exc

