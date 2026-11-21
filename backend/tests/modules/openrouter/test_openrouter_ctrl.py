from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Settings, get_settings
from app.main import create_app
from app.modules.openrouter.openrouter_ctrl import get_openrouter_service
from app.modules.openrouter.openrouter_helper import OpenRouterHelper
from app.modules.openrouter.openrouter_service import OpenRouterService
from tests.modules.openrouter.test_openrouter_service import FakeHelper

URL = "/api/openrouter/images/generations"


def _client(settings: Settings, helper: FakeHelper | None = None) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    if helper is not None:
        app.dependency_overrides[get_openrouter_service] = lambda: OpenRouterService(
            helper
        )
    return TestClient(app)


@pytest.fixture
def client() -> Iterator[TestClient]:
    helper = FakeHelper(
        response={
            "created": 7,
            "data": [{"b64_json": "AAA=", "media_type": "image/webp"}],
        }
    )
    with _client(
        Settings(_env_file=None, openrouter_api_key=SecretStr("sk")), helper
    ) as c:
        yield c


def test_generate_image_returns_images(client: TestClient) -> None:
    response = client.post(URL, json={"prompt": "A modern SaaS dashboard UI design"})

    assert response.status_code == 200
    assert response.json() == {
        "created": 7,
        "data": [{"b64_json": "AAA=", "media_type": "image/webp"}],
        "cost": None,
    }


def test_generate_image_requires_prompt(client: TestClient) -> None:
    assert client.post(URL, json={}).status_code == 422


def test_generate_image_rejects_unknown_fields(client: TestClient) -> None:
    response = client.post(URL, json={"prompt": "x", "bogus": 1})
    assert response.status_code == 422


def test_generate_image_rejects_invalid_enums(client: TestClient) -> None:
    response = client.post(URL, json={"prompt": "x", "output_format": "gif"})
    assert response.status_code == 422


def test_generate_image_rejects_out_of_range_n(client: TestClient) -> None:
    assert client.post(URL, json={"prompt": "x", "n": 0}).status_code == 422
    assert client.post(URL, json={"prompt": "x", "n": 11}).status_code == 422


def test_generate_image_without_api_key_returns_503() -> None:
    with _client(Settings(_env_file=None, openrouter_api_key=None)) as client:
        response = client.post(URL, json={"prompt": "x"})

    assert response.status_code == 503
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


def test_generate_image_provider_failure_returns_502() -> None:
    from app.modules.openrouter.openrouter_helper import ProviderCallError

    helper = FakeHelper(
        error=ProviderCallError("OpenRouter returned HTTP 402: No credits")
    )
    with _client(
        Settings(_env_file=None, openrouter_api_key=SecretStr("sk")), helper
    ) as client:
        response = client.post(URL, json={"prompt": "x"})

    assert response.status_code == 502
    assert "No credits" in response.json()["detail"]


def test_default_dependency_builds_helper_from_settings() -> None:
    settings = Settings(_env_file=None, openrouter_api_key=SecretStr("sk"))
    service = get_openrouter_service(settings)

    assert isinstance(service, OpenRouterService)
    assert isinstance(service._helper, OpenRouterHelper)
    assert service._helper.is_configured is True
