# Project Structure

```text
backend/
├── pyproject.toml           # uv-managed deps, [tool.ruff], [tool.pytest.ini_options]
├── uv.lock
├── .env.example             # documented keys, no real values
├── app/
│   ├── __init__.py
│   ├── main.py              # create_app(): lifespan, middleware, routers, error handlers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings (pydantic-settings), get_settings()
│   │   ├── db.py            # psycopg2 connection pool, get_conn() context manager
│   │   ├── cache.py         # redis.asyncio client factory
│   │   ├── local_cache.py   # sqlite3 local cache
│   │   ├── analytics.py     # duckdb connection factory
│   │   ├── http.py          # shared httpx.AsyncClient lifecycle
│   │   ├── security.py      # PyJWT encode/decode, password hashing hooks
│   │   ├── logging.py       # structlog configuration
│   │   ├── errors.py        # domain exception base classes + handlers
│   │   └── scheduler.py     # APScheduler instance + job registration
│   └── modules/
│       ├── user/
│       │   ├── __init__.py
│       │   ├── user_ctrl.py
│       │   ├── user_service.py
│       │   ├── user_helper.py
│       │   ├── user_utils.py
│       │   └── user_schema.py
│       ├── orders/
│       │   └── ...same five files...
│       └── products/
│           └── ...
└── tests/
    ├── conftest.py          # app fixture, test settings, db fixtures
    ├── core/
    └── modules/
        ├── user/
        │   ├── test_user_ctrl.py
        │   ├── test_user_service.py
        │   ├── test_user_helper.py
        │   └── test_user_utils.py
        └── ...
```

## Naming

- Module folder: singular or plural noun, lowercase, no hyphens (`user`, `orders`, `products`). Python package name must be importable.
- Files: `<module>_<layer>.py` exactly: `_ctrl`, `_service`, `_helper`, `_utils`, `_schema`.
- Classes: `UserCreate`, `UserResponse`, `UserError`. Functions: `create_user`, `get_user_by_id`.
- Router variable: `router` in `<name>_ctrl.py`; mounted in `main.py` with prefix `/api/<name>`.

## Placement table

| What | Where |
|---|---|
| HTTP route | `modules/<name>/<name>_ctrl.py` |
| Request/response Pydantic model | `modules/<name>/<name>_schema.py` |
| Business rule, orchestration | `modules/<name>/<name>_service.py` |
| SQL query, cache get/set, HTTP call, file read | `modules/<name>/<name>_helper.py` |
| Parse raw payload into domain dict | `modules/<name>/<name>_helper.py` |
| Normalize email, trim strings, validate ranges | `modules/<name>/<name>_utils.py` |
| Settings, secret, DB pool | `core/` |
| JWT encode/decode | `core/security.py` |
| Shared exception base | `core/errors.py` |
| Scheduled job | `core/scheduler.py` registers; job body calls a service |
| Cross-module shared pure helper | Only if used by ≥2 modules: `core/` (pure) — otherwise duplicate small logic |

## Entry point (`app/main.py`)

- Build the app in `create_app()`; expose `app = create_app()` for Uvicorn.
- Lifespan opens/closes: DB pool, Redis client, httpx client, DuckDB connection, scheduler.
- Register routers from each module's `router`.
- Register error handlers from `core/errors.py` so services never return HTTP responses.
- Use `ORJSONResponse` as `default_response_class` when payloads are large.
