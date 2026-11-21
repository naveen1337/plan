# Config, Security, External I/O, Logging, Jobs

## Settings and secrets (pydantic-settings)

```python
# app/core/config.py
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="forbid")

    env: str = "dev"
    database_url: SecretStr
    db_pool_max: int = 10
    redis_url: SecretStr
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_ttl_seconds: int = 3600
    sqlite_path: str = "local_cache.db"
    log_json: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
```

Rules:
- Every secret is `SecretStr`. Call `.get_secret_value()` only at the point of use (pool, client, signer).
- `.env` is never committed. Commit `.env.example` with keys and empty placeholders.
- Tests override settings via environment variables or a `Settings` fixture, never by editing files.
- YAML config (if needed) is loaded with `yaml.safe_load` in `core/config.py` only.

## Auth (PyJWT)

```python
# app/core/security.py
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings


class TokenClaims(BaseModel):
    sub: str
    exp: int


def create_access_token(subject: str) -> str:
    s = get_settings()
    now = datetime.now(UTC)
    payload = {"sub": subject, "iat": now, "exp": now + timedelta(seconds=s.jwt_ttl_seconds)}
    return jwt.encode(payload, s.jwt_secret.get_secret_value(), algorithm=s.jwt_algorithm)


def decode_access_token(authorization: str = Header(...)) -> TokenClaims:
    s = get_settings()
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid authorization header")
    try:
        data = jwt.decode(token, s.jwt_secret.get_secret_value(), algorithms=[s.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from exc
    return TokenClaims(**data)
```

Rules:
- Always pass `algorithms=[...]` explicitly on decode. Never accept `none`.
- The HTTP-facing dependency may live in `core/security.py` only if it raises HTTP errors; otherwise move the HTTP mapping into the ctrl. Keep services free of HTTP.
- Token creation/verification is the only JWT code path. Services receive decoded claims, not raw tokens.

## Outbound HTTP (httpx + tenacity)

```python
# app/modules/products/products_helper.py
import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.http import get_http_client


@retry(
    retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
async def fetch_product_feed(url: str) -> dict:
    response = await get_http_client().get(url, timeout=10.0)
    response.raise_for_status()
    return response.json()
```

Rules:
- One shared `httpx.AsyncClient` created in lifespan (`core/http.py`); never create a client per request.
- Explicit timeouts on every call.
- Retry only idempotent calls, and only on transport errors or 5xx/429. Do not retry 4xx.
- For large JSON bodies, parse with `orjson.loads(response.content)` instead of `response.json()`.

## JSON (orjson)

- `orjson.dumps(obj)` returns bytes; `orjson.loads(bytes_or_str)` accepts both.
- Use `ORJSONResponse` as default response class for large payloads (`FastAPI(default_response_class=ORJSONResponse)`).
- Do not serialize non-JSON types ad hoc; convert to Pydantic models or plain dicts first.

## YAML (PyYAML)

- Only `yaml.safe_load` / `yaml.safe_load_all`. Never `yaml.load` without a safe loader.
- Parse YAML in helpers; validate the parsed structure with a Pydantic model before use.

## Logging (structlog)

```python
# app/core/logging.py
import structlog


def configure_logging(json_output: bool) -> None:
    renderer = structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
    )
```

Rules:
- Log structured events: `log.info("user_created", user_id=user.id)`, never f-strings.
- Bind request-scoped context (request id) with `structlog.contextvars`.
- Never log passwords, tokens, `SecretStr` values, or full request bodies.
- Business logging happens in services; transport logging (access logs) in ctrl/middleware.

## Scheduling (APScheduler)

```python
# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def register_jobs() -> None:
    from app.modules.orders import orders_service

    scheduler.add_job(
        orders_service.close_stale_carts,
        trigger="interval",
        minutes=15,
        id="orders.close_stale_carts",
        replace_existing=True,
    )
```

Rules:
- Start/stop the scheduler in lifespan.
- Job functions call a service; they do not contain SQL or HTTP.
- Job functions are idempotent: a rerun must not duplicate effects.
- Verify the APScheduler API against the installed version's docs before use; the 3.x and 4.x lines differ.
