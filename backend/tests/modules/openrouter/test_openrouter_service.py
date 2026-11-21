import asyncio
from typing import Any

import pytest

from app.core.errors import ServiceUnavailableError, UpstreamError
from app.modules.openrouter.openrouter_helper import ProviderCallError
from app.modules.openrouter.openrouter_schema import ImageGenerationRequest
from app.modules.openrouter.openrouter_service import OpenRouterService


class FakeHelper:
    def __init__(
        self,
        *,
        configured: bool = True,
        response: Any = None,
        error: Exception | None = None,
    ) -> None:
        self.is_configured = configured
        self._response = response
        self._error = error
        self.payloads: list[dict] = []

    async def generate_image(self, payload: dict) -> dict:
        self.payloads.append(payload)
        if self._error is not None:
            raise self._error
        return self._response


def _request(**overrides: Any) -> ImageGenerationRequest:
    return ImageGenerationRequest(prompt="A dashboard", **overrides)


def test_defaults_match_documented_example() -> None:
    request = _request()
    assert request.model == "openai/gpt-image-2"
    assert request.quality == "low"
    assert request.aspect_ratio == "16:9"
    assert request.n == 1
    assert request.output_format == "webp"


def test_generate_builds_payload_and_maps_response() -> None:
    helper = FakeHelper(
        response={
            "created": 42,
            "data": [{"b64_json": "AAA="}],
            "usage": {"cost": 0.04},
        }
    )

    result = asyncio.run(OpenRouterService(helper).generate_image(_request()))

    assert helper.payloads[0]["prompt"] == "A dashboard"
    assert helper.payloads[0]["output_format"] == "webp"
    assert result == {
        "created": 42,
        "data": [{"b64_json": "AAA=", "media_type": "image/webp"}],
        "cost": 0.04,
    }


def test_generate_uses_upstream_media_type_when_present() -> None:
    helper = FakeHelper(
        response={
            "created": 1,
            "data": [{"b64_json": "AAA=", "media_type": "image/png"}],
        }
    )

    result = asyncio.run(
        OpenRouterService(helper).generate_image(_request(output_format="png"))
    )

    assert result["data"][0]["media_type"] == "image/png"
    assert result["cost"] is None


def test_generate_requires_configuration() -> None:
    helper = FakeHelper(configured=False)

    with pytest.raises(ServiceUnavailableError, match="OPENROUTER_API_KEY"):
        asyncio.run(OpenRouterService(helper).generate_image(_request()))
    assert helper.payloads == []


def test_generate_maps_provider_failure_to_upstream_error() -> None:
    helper = FakeHelper(error=ProviderCallError("OpenRouter returned HTTP 502: bad"))

    with pytest.raises(UpstreamError, match="HTTP 502"):
        asyncio.run(OpenRouterService(helper).generate_image(_request()))


def test_generate_rejects_malformed_upstream_response() -> None:
    helper = FakeHelper(response={"unexpected": True})

    with pytest.raises(UpstreamError, match="unexpected response"):
        asyncio.run(OpenRouterService(helper).generate_image(_request()))


def test_generate_rejects_response_without_images() -> None:
    helper = FakeHelper(response={"created": 1, "data": [{"url": "https://x"}]})

    with pytest.raises(UpstreamError, match="no image data"):
        asyncio.run(OpenRouterService(helper).generate_image(_request()))
