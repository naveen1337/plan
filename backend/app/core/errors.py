from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for errors raised by services. Carries no HTTP meaning."""


class NotFoundError(DomainError):
    """Requested resource does not exist."""


async def _not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, _not_found_handler)
