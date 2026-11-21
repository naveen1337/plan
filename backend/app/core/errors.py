from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for errors raised by services. Carries no HTTP meaning."""


class NotFoundError(DomainError):
    """Requested resource does not exist."""


class ServiceUnavailableError(DomainError):
    """A required server-side configuration or dependency is missing."""


class UpstreamError(DomainError):
    """An external provider failed or returned an unusable response."""


async def _not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _service_unavailable_handler(
    _: Request, exc: ServiceUnavailableError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


async def _upstream_handler(_: Request, exc: UpstreamError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, _not_found_handler)
    app.add_exception_handler(ServiceUnavailableError, _service_unavailable_handler)
    app.add_exception_handler(UpstreamError, _upstream_handler)
