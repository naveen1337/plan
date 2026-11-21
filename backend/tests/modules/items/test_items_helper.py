from app.modules.items.items_helper import ItemsHelper


def test_insert_assigns_increasing_ids() -> None:
    helper = ItemsHelper()
    first = helper.insert({"title": "a", "description": None, "completed": False})
    second = helper.insert({"title": "b", "description": None, "completed": False})
    assert (first["id"], second["id"]) == (1, 2)


def test_find_missing_returns_none() -> None:
    assert ItemsHelper().find_by_id(1) is None


def test_remove_then_find_returns_none() -> None:
    helper = ItemsHelper()
    item = helper.insert({"title": "a", "description": None, "completed": False})
    helper.remove(item["id"])
    assert helper.find_by_id(item["id"]) is None
