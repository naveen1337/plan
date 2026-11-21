from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.modules.items.items_ctrl import router as items_router
from app.modules.openrouter.openrouter_ctrl import router as openrouter_router


def create_app() -> FastAPI:
    app = FastAPI(title="Plan and Execution API", version="0.1.0")
    app.include_router(items_router)
    app.include_router(openrouter_router)
    register_error_handlers(app)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
