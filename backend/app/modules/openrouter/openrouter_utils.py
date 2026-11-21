from typing import Any


def build_payload(request: dict[str, Any]) -> dict[str, Any]:
    """Return the OpenRouter request body, dropping unset (None) fields. Pure."""
    return {key: value for key, value in request.items() if value is not None}


def media_type_for(output_format: str) -> str:
    """Map an output format name to its MIME type. Pure."""
    return {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp"}[
        output_format
    ]


def image_filename(created: int, index: int, media_type: str) -> str:
    """Build a unique file name for a generated image. Pure."""
    extension = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
    }.get(media_type, "bin")
    return f"openrouter_{created}_{index}.{extension}"
