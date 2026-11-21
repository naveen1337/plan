import base64
import binascii

from pydantic import ValidationError

from app.core.errors import ServiceUnavailableError, UpstreamError
from app.modules.openrouter import openrouter_utils
from app.modules.openrouter.openrouter_helper import OpenRouterHelper, ProviderCallError
from app.modules.openrouter.openrouter_schema import (
    GeneratedImage,
    ImageGenerationRequest,
    UpstreamImageResponse,
)


class OpenRouterService:
    """Business rules for OpenRouter image generation. Delegates I/O to the helper."""

    def __init__(self, helper: OpenRouterHelper) -> None:
        self._helper = helper

    async def generate_image(self, request: ImageGenerationRequest) -> dict:
        if not self._helper.is_configured:
            raise ServiceUnavailableError(
                "OpenRouter is not configured: set OPENROUTER_API_KEY"
            )

        payload = openrouter_utils.build_payload(request.model_dump())
        try:
            raw = await self._helper.generate_image(payload)
        except ProviderCallError as exc:
            raise UpstreamError(str(exc)) from exc

        try:
            upstream = UpstreamImageResponse.model_validate(raw)
        except ValidationError as exc:
            raise UpstreamError("OpenRouter returned an unexpected response") from exc

        images = [
            GeneratedImage(
                b64_json=item.b64_json,
                media_type=item.media_type
                or openrouter_utils.media_type_for(request.output_format),
            )
            for item in upstream.data
            if item.b64_json
        ]
        if not images:
            raise UpstreamError("OpenRouter returned no image data")

        saved: list[GeneratedImage] = []
        for index, image in enumerate(images):
            try:
                content = base64.b64decode(image.b64_json, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise UpstreamError("OpenRouter returned invalid image data") from exc
            filename = openrouter_utils.image_filename(
                upstream.created, index, image.media_type or ""
            )
            path = self._helper.save_image(filename, content)
            saved.append(image.model_copy(update={"saved_path": str(path)}))

        return {
            "created": upstream.created,
            "data": [image.model_dump() for image in saved],
            "cost": upstream.usage.cost if upstream.usage else None,
        }
