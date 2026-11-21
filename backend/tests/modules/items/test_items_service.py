import pytest

from app.core.errors import NotFoundError
from app.modules.items.items_schema import ItemCreate, ItemUpdate
from app.modules.items.items_service import ItemsService


def test_create_returns_item_with_id(items_service: ItemsService) -> None:
    item = items_service.create(ItemCreate(title="a"))
    assert item["id"] == 1
    assert item["title"] == "a"


def test_get_missing_raises_not_found(items_service: ItemsService) -> None:
    with pytest.raises(NotFoundError, match="Item 5 not found"):
        items_service.get(5)


def test_update_revalidates_merged_result(items_service: ItemsService) -> None:
    item = items_service.create(ItemCreate(title="a"))
    updated = items_service.update(item["id"], ItemUpdate(completed=True))
    assert updated["completed"] is True
    assert updated["title"] == "a"


def test_delete_missing_raises_not_found(items_service: ItemsService) -> None:
    with pytest.raises(NotFoundError):
        items_service.delete(1)
