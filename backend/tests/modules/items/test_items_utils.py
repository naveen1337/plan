from app.modules.items.items_utils import merge_changes


def test_merge_changes_overrides_and_keeps_other_keys() -> None:
    current = {"id": 1, "title": "a", "completed": False}
    assert merge_changes(current, {"completed": True}) == {
        "id": 1,
        "title": "a",
        "completed": True,
    }


def test_merge_changes_does_not_mutate_inputs() -> None:
    current = {"id": 1, "title": "a"}
    merge_changes(current, {"title": "b"})
    assert current == {"id": 1, "title": "a"}
