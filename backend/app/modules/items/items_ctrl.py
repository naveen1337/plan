from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.modules.items.items_helper import ItemsHelper
from app.modules.items.items_schema import Item, ItemCreate, ItemUpdate
from app.modules.items.items_service import ItemsService

router = APIRouter(prefix="/api/items", tags=["items"])

_service = ItemsService(ItemsHelper())


def get_items_service() -> ItemsService:
    return _service


ItemsServiceDep = Annotated[ItemsService, Depends(get_items_service)]


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, service: ItemsServiceDep) -> dict:
    return service.create(data)


@router.get("", response_model=list[Item])
def list_items(service: ItemsServiceDep) -> list[dict]:
    return service.list()


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, service: ItemsServiceDep) -> dict:
    return service.get(item_id)


@router.patch("/{item_id}", response_model=Item)
def update_item(item_id: int, data: ItemUpdate, service: ItemsServiceDep) -> dict:
    return service.update(item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, service: ItemsServiceDep) -> Response:
    service.delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
