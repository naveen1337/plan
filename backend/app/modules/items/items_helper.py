class ItemsHelper:
    """In-memory storage for items. Owns all I/O for the items module.

    Data lives only for the lifetime of the process. Replace this class with a
    persistent implementation (e.g. Postgres via pypika + psycopg2) without
    changing the service or the controller.
    """

    def __init__(self) -> None:
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def insert(self, data: dict) -> dict:
        item = {"id": self._next_id, **data}
        self._items[self._next_id] = item
        self._next_id += 1
        return dict(item)

    def list_all(self) -> list[dict]:
        return [dict(item) for item in self._items.values()]

    def find_by_id(self, item_id: int) -> dict | None:
        item = self._items.get(item_id)
        return None if item is None else dict(item)

    def replace(self, item_id: int, data: dict) -> dict:
        item = {"id": item_id, **data}
        self._items[item_id] = item
        return dict(item)

    def remove(self, item_id: int) -> None:
        del self._items[item_id]
