import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from app.core.config import Settings
from app.modules.openrouter.openrouter_helper import OpenRouterHelper, ProviderCallError

OK_BODY = {"created": 1, "data": [{"b64_json": "AAA="}]}


def _settings(key: str | None = "sk-test") -> Settings:
    return Settings(
        _env_file=None,
        openrouter_api_key=SecretStr(key) if key is not None else None,
        openrouter_base_url="https://example.test/api/v1/",
    )


def _helper(handler: httpx.MockTransport | None, key: str | None = "sk-test"):
    return OpenRouterHelper(_settings(key), transport=handler)


def test_is_configured_reflects_key() -> None:
    assert _helper(None).is_configured is True
    assert _helper(None, key=None).is_configured is False
    assert _helper(None, key="").is_configured is False


def test_generate_image_posts_to_images_with_bearer_auth() -> None:
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=OK_BODY)

    result = asyncio.run(
        _helper(httpx.MockTransport(handler)).generate_image({"prompt": "cat"})
    )

    assert result == OK_BODY
    assert seen["url"] == "https://example.test/api/v1/images"
    assert seen["auth"] == "Bearer sk-test"
    assert seen["body"] == {"prompt": "cat"}


def test_generate_image_raises_on_http_error_with_upstream_message() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            402, json={"error": {"code": 402, "message": "No credits"}}
        )

    with pytest.raises(ProviderCallError, match="HTTP 402: No credits"):
        asyncio.run(_helper(httpx.MockTransport(handler)).generate_image({}))


def test_generate_image_raises_on_transport_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    with pytest.raises(ProviderCallError, match="request failed"):
        asyncio.run(_helper(httpx.MockTransport(handler)).generate_image({}))


def test_generate_image_raises_on_non_json_body() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>")

    with pytest.raises(ProviderCallError, match="non-JSON"):
        asyncio.run(_helper(httpx.MockTransport(handler)).generate_image({}))


def test_generate_image_without_key_raises() -> None:
    with pytest.raises(ProviderCallError, match="not configured"):
        asyncio.run(_helper(None, key=None).generate_image({}))
