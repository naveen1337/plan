from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImageGenerationRequest(BaseModel):
    """Request body for generating an image through OpenRouter."""

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=4000)
    model: str = Field(default="openai/gpt-image-2", min_length=1, max_length=200)
    quality: Literal["auto", "low", "medium", "high", "xhigh", "max"] = "low"
    aspect_ratio: Literal[
        "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"
    ] = "16:9"
    n: int = Field(default=1, ge=1, le=10)
    output_format: Literal["png", "jpeg", "webp"] = "webp"


class GeneratedImage(BaseModel):
    b64_json: str
    media_type: str | None = None
    saved_path: str | None = None


class ImageGenerationResponse(BaseModel):
    """Response returned to our clients."""

    created: int
    data: list[GeneratedImage]
    cost: float | None = None


class UpstreamImageItem(BaseModel):
    """One image as returned by OpenRouter. Unknown fields are ignored."""

    b64_json: str | None = None
    media_type: str | None = None


class UpstreamUsage(BaseModel):
    cost: float | None = None


class UpstreamImageResponse(BaseModel):
    """OpenRouter `/images` response. Unknown fields are ignored."""

    created: int
    data: list[UpstreamImageItem]
    usage: UpstreamUsage | None = None
