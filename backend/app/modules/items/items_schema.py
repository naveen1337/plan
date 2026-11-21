from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class ItemCreate(ItemBase):
    """Request body for creating an item."""


class ItemUpdate(BaseModel):
    """Request body for partially updating an item (PATCH semantics)."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None

    @field_validator("title", "completed", mode="before")
    @classmethod
    def _reject_explicit_null(cls, value: Any) -> Any:
        # Fields are optional for PATCH, but when provided they cannot be null.
        if value is None:
            raise ValueError("must not be null")
        return value


class Item(ItemBase):
    """Item as returned by the API."""

    id: int
