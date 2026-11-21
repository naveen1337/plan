from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.modules.openrouter.openrouter_helper import OpenRouterHelper
from app.modules.openrouter.openrouter_schema import (
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.modules.openrouter.openrouter_service import OpenRouterService

router = APIRouter(prefix="/api/openrouter", tags=["openrouter"])


def get_openrouter_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OpenRouterService:
    return OpenRouterService(OpenRouterHelper(settings))


OpenRouterServiceDep = Annotated[OpenRouterService, Depends(get_openrouter_service)]


@router.post(
    "/images/generations",
    response_model=ImageGenerationResponse,
)
async def generate_image(
    data: ImageGenerationRequest, service: OpenRouterServiceDep
) -> dict:
    return await service.generate_image(data)
