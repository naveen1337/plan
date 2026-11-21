from pathlib import Path
from typing import Any

import httpx

from app.core.config import Settings


class ProviderCallError(Exception):
    """OpenRouter could not be reached or returned a non-success response."""


class OpenRouterHelper:
    """Owns all outbound I/O to the OpenRouter API and local file writes for this module."""

    def __init__(
        self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._api_key = settings.openrouter_api_key
        self._base_url = settings.openrouter_base_url.rstrip("/")
        self._timeout = settings.openrouter_timeout_seconds
        self._downloads_dir = settings.openrouter_downloads_dir
        self._transport = transport

    @property
    def is_configured(self) -> bool:
        return self._api_key is not None and bool(self._api_key.get_secret_value())

    def save_image(self, filename: str, content: bytes) -> Path:
        """Write image bytes into the downloads directory and return the file path."""
        self._downloads_dir.mkdir(parents=True, exist_ok=True)
        path = self._downloads_dir / filename
        path.write_bytes(content)
        return path

    async def generate_image(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._api_key is None:
            raise ProviderCallError("OpenRouter API key is not configured")
        headers = {
            "Authorization": f"Bearer {self._api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post("/images", json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ProviderCallError(f"OpenRouter request failed: {exc}") from exc

        if response.status_code >= 400:
            raise ProviderCallError(
                f"OpenRouter returned HTTP {response.status_code}: "
                f"{_error_message(response)}"
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderCallError("OpenRouter returned a non-JSON body") from exc
        if not isinstance(body, dict):
            raise ProviderCallError("OpenRouter returned an unexpected body")
        return body


def _error_message(response: httpx.Response) -> str:
    try:
        error = response.json().get("error", {})
        message = error.get("message") if isinstance(error, dict) else None
    except (ValueError, AttributeError):
        message = None
    return str(message or response.reason_phrase)
