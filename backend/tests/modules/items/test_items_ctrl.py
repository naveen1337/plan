from fastapi.testclient import TestClient


def _create(client: TestClient, title: str = "Buy milk", **extra: object) -> dict:
    response = client.post("/api/items", json={"title": title, **extra})
    assert response.status_code == 201
    return response.json()


def test_create_item(client: TestClient) -> None:
    response = client.post(
        "/api/items",
        json={"title": "Write tests", "description": "pytest", "completed": False},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Write tests",
        "description": "pytest",
        "completed": False,
    }


def test_create_item_defaults(client: TestClient) -> None:
    item = _create(client)
    assert item["description"] is None
    assert item["completed"] is False


def test_create_item_rejects_empty_title(client: TestClient) -> None:
    response = client.post("/api/items", json={"title": ""})
    assert response.status_code == 422


def test_create_item_rejects_unknown_fields(client: TestClient) -> None:
    response = client.post("/api/items", json={"title": "x", "unknown": 1})
    assert response.status_code == 422


def test_list_items_empty(client: TestClient) -> None:
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items(client: TestClient) -> None:
    _create(client, "first")
    _create(client, "second")

    titles = [item["title"] for item in client.get("/api/items").json()]
    assert titles == ["first", "second"]


def test_get_item(client: TestClient) -> None:
    created = _create(client)

    response = client.get(f"/api/items/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_item_not_found(client: TestClient) -> None:
    response = client.get("/api/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item 999 not found"


def test_update_item_partial(client: TestClient) -> None:
    created = _create(client, "Buy milk", description="2 liters")

    response = client.patch(f"/api/items/{created['id']}", json={"completed": True})

    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["title"] == "Buy milk"
    assert body["description"] == "2 liters"


def test_update_item_can_clear_description(client: TestClient) -> None:
    created = _create(client, description="temp")

    response = client.patch(f"/api/items/{created['id']}", json={"description": None})

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_item_rejects_empty_title(client: TestClient) -> None:
    created = _create(client)

    response = client.patch(f"/api/items/{created['id']}", json={"title": ""})

    assert response.status_code == 422
    assert client.get(f"/api/items/{created['id']}").json()["title"] == "Buy milk"


def test_update_item_rejects_null_title_and_completed(client: TestClient) -> None:
    created = _create(client)

    assert (
        client.patch(f"/api/items/{created['id']}", json={"title": None}).status_code
        == 422
    )
    assert (
        client.patch(
            f"/api/items/{created['id']}", json={"completed": None}
        ).status_code
        == 422
    )


def test_update_item_not_found(client: TestClient) -> None:
    response = client.patch("/api/items/999", json={"completed": True})
    assert response.status_code == 404


def test_delete_item(client: TestClient) -> None:
    created = _create(client)

    response = client.delete(f"/api/items/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""

    assert client.get(f"/api/items/{created['id']}").status_code == 404
    assert client.get("/api/items").json() == []


def test_delete_item_not_found(client: TestClient) -> None:
    response = client.delete("/api/items/999")
    assert response.status_code == 404


def test_ids_are_not_reused_after_delete(client: TestClient) -> None:
    first = _create(client, "first")
    client.delete(f"/api/items/{first['id']}")

    second = _create(client, "second")
    assert second["id"] == first["id"] + 1
