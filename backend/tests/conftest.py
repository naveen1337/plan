from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.modules.items.items_ctrl import get_items_service
from app.modules.items.items_helper import ItemsHelper
from app.modules.items.items_service import ItemsService


@pytest.fixture
def items_service() -> ItemsService:
    return ItemsService(ItemsHelper())


@pytest.fixture
def client(items_service: ItemsService) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_items_service] = lambda: items_service
    with TestClient(app) as test_client:
        yield test_client
