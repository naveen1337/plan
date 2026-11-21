from app.core.errors import NotFoundError
from app.modules.items import items_utils
from app.modules.items.items_helper import ItemsHelper
from app.modules.items.items_schema import Item, ItemCreate, ItemUpdate


class ItemsService:
    """Business rules for items. Delegates all I/O to ItemsHelper."""

    def __init__(self, helper: ItemsHelper) -> None:
        self._helper = helper

    def create(self, data: ItemCreate) -> dict:
        return self._helper.insert(data.model_dump())

    def list(self) -> list[dict]:
        return self._helper.list_all()

    def get(self, item_id: int) -> dict:
        item = self._helper.find_by_id(item_id)
        if item is None:
            raise NotFoundError(f"Item {item_id} not found")
        return item

    def update(self, item_id: int, data: ItemUpdate) -> dict:
        current = self.get(item_id)
        merged = items_utils.merge_changes(current, data.model_dump(exclude_unset=True))
        # Re-validate so partial updates obey the same rules as creation.
        validated = Item.model_validate(merged).model_dump()
        return self._helper.replace(item_id, validated)

    def delete(self, item_id: int) -> None:
        self.get(item_id)
        self._helper.remove(item_id)
