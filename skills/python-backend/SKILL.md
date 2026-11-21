---
name: python-backend
description: Build Python 3.13 FastAPI backends with uv and ruff, organized as app/modules/<name>/ with <name>_ctrl.py (routes, validation, auth, responses), <name>_service.py (business logic), <name>_helper.py (DB, cache, external I/O, parsing) and <name>_utils.py (pure validation/cleaning). Uses Postgres (psycopg2 + pypika, no ORM), Redis cache, SQLite local cache, DuckDB analytics, httpx, Pydantic v2, pydantic-settings, PyJWT, tenacity, orjson, PyYAML, structlog, APScheduler. Use when creating or changing backend routes, modules, services, database access, config, auth, background jobs, external API calls, or backend tests in this repo.
license: MIT
compatibility: opencode, claude-code
metadata:
  stack: python fastapi uv ruff postgres redis
  audience: backend-developers
  workflow: module-layered-fastapi
---

# Python Backend (FastAPI)

Opinionated skill for FastAPI backends managed with `uv`, linted and formatted with `ruff`.

## When to use

Use this skill when the task involves, in a Python/FastAPI backend:

- Adding or changing a module, route, request/response model, or auth rule
- Writing business logic, database queries, cache access, or external API calls
- Configuring settings, secrets, logging, JWT, scheduled jobs, or retries
- Adding tests or reviewing backend code for layering violations

If the project explicitly uses a different stack, follow the project and ignore conflicting defaults here.

## Core stack (defaults)

- Python 3.13, dependencies and virtualenv managed by **uv** (`uv add`, `uv run`, `uv.lock` committed)
- **FastAPI** (latest stable release) + Uvicorn
- **ruff** for both lint (`ruff check`) and format (`ruff format`); no black/isort/flake8
- **PostgreSQL** is the default database; driver **psycopg2**; SQL built with **pypika**; **no ORM** (no SQLAlchemy, no SQLModel, no Django ORM, no Tortoise)
- **Redis** (`redis` package, `redis.asyncio`) as cache
- **SQLite** (stdlib `sqlite3`) for local cache only
- **DuckDB** for analytical queries (aggregations, scans over files/exports), never for OLTP writes
- **httpx** for all outbound HTTP (async client)
- **Pydantic v2** for every request, response, and validation boundary
- **pydantic-settings** with `SecretStr` for env vars and config
- **PyJWT** for auth tokens and signatures
- **tenacity** for retries on external calls
- **orjson** for large JSON encode/decode (and `ORJSONResponse` for big responses)
- **PyYAML** for YAML config/input (`yaml.safe_load` only)
- **structlog** for structured local logging
- **APScheduler** for in-process scheduled jobs

Details: [references/01-stack.md](references/01-stack.md)

## Mandatory project structure

```text
backend/
├── pyproject.toml
├── uv.lock
├── app/
│   ├── main.py              # app factory, lifespan, router registration
│   ├── core/                # shared infrastructure (config, db, cache, security, logging, scheduler, errors)
│   └── modules/
│       └── <name>/          # e.g. user, orders, products
│           ├── __init__.py
│           ├── <name>_ctrl.py     # routes, request validation, auth, response
│           ├── <name>_service.py  # business logic
│           ├── <name>_helper.py   # I/O: DB (pypika+psycopg2), cache, external API, parsing
│           ├── <name>_utils.py    # pure functions: validation, cleaning, normalization
│           └── <name>_schema.py   # Pydantic request/response models for the module
└── tests/
    ├── modules/<name>/      # mirrors app/modules
    └── conftest.py
```

Rules: one folder per business module under `app/modules/`. Never put business code in `core/`. Never put a second module's code inside another module folder.

Details: [references/02-project-structure.md](references/02-project-structure.md)

## Layer rules (enforce strictly)

```text
ctrl → service → helper → utils
  ↘________↗ (ctrl may call utils for validation; utils imports nothing internal)
```

- **`<name>_ctrl.py`** — `APIRouter`, route decorators, Pydantic validation via `_schema.py`, auth dependencies, mapping domain errors to HTTP status, building the response. Calls **only** its own `<name>_service`. No business logic, no SQL, no `httpx`.
- **`<name>_service.py`** — business rules and orchestration. Calls its own `<name>_helper` and `<name>_utils`, and other modules' **services** (never their helpers). No `fastapi`/`starlette` imports, no `HTTPException`; raise domain exceptions from `core/errors.py`.
- **`<name>_helper.py`** — supports the service: parsing, DB access (pypika + psycopg2), Redis, SQLite, DuckDB, `httpx` calls, file I/O, retries. Owns all I/O for the module. Returns plain data (dicts, dataclasses, Pydantic models), not HTTP objects.
- **`<name>_utils.py`** — pure functions only: validation, cleaning, normalization, computation. Deterministic, no I/O, no logging, no env access, no imports from `helper`/`service`/`ctrl`.
- **`core/`** — shared infrastructure only (settings, connection pools, JWT encode/decode, logging setup, scheduler, error types). Modules depend on `core`; `core` never imports from `modules`.
- Sync-only libraries (psycopg2, duckdb, stdlib sqlite3) are called from helpers through `run_in_threadpool` or from sync `def` routes. Never block the event loop.

Details: [references/03-layers.md](references/03-layers.md)

## Data access

- SQL is built with **pypika** (`PostgreSQLQuery`, `Table`) and executed with **psycopg2** using parameter tuples. Never build SQL with f-strings or `%` formatting from user input.
- Connections come from a shared pool in `core/db.py`. Helpers open a cursor per unit of work and close it.
- Migrations and schema DDL are plain `.sql` files; no ORM metadata.
- Redis is a cache, never the source of truth. Every cached value has a TTL.
- SQLite is for local, single-process cache/state only.
- DuckDB is for read-heavy analytics. Writes to Postgres go through the Postgres helper.

Details: [references/04-data-access.md](references/04-data-access.md)

## Config, security, external calls, logging

- Settings in `core/config.py` via `pydantic-settings`. Secrets typed as `SecretStr`. Never log or serialize `SecretStr` values; call `.get_secret_value()` only inside helpers that need the raw value.
- Auth: JWT via **PyJWT** (`jwt.encode` / `jwt.decode` with an explicit `algorithms=[...]`). Token verification is a dependency in `<name>_ctrl.py`; token creation lives in `core/security.py`.
- Outbound HTTP: shared `httpx.AsyncClient` created in lifespan, used only in helpers, with timeouts set explicitly. Retries via **tenacity** on transport/5xx errors only.
- JSON: `orjson` for large payloads; `ORJSONResponse` for big responses.
- Logging: **structlog** with JSON or console renderer chosen by config. Log events, not f-strings; never log secrets or raw tokens.
- Scheduling: **APScheduler** jobs registered in `core/scheduler.py`; each job calls a service function, never SQL directly.

Details: [references/05-config-security-io.md](references/05-config-security-io.md)

## Testing and quality

Tests, fixtures, ruff configuration, and layer-violation review checklist: [references/06-testing-quality.md](references/06-testing-quality.md)

## Pre-completion checklist

1. Every module lives in `app/modules/<name>/` with the five files (`ctrl`, `service`, `helper`, `utils`, `schema`).
2. `ctrl` has no SQL, no `httpx`, no business rules; it only validates, authorizes, delegates, and responds.
3. `service` does not import `fastapi`/`starlette` and does not import another module's helper.
4. `helper` holds all I/O; `utils` has no I/O and no imports from helper/service/ctrl.
5. All request and response bodies are Pydantic v2 models.
6. No ORM imports; all SQL built with pypika and executed with parameters.
7. Secrets are `SecretStr` from `core/config.py`; no hardcoded keys, no `.env` committed.
8. Blocking libraries are not called directly inside `async def` code.
9. Every feature has pytest tests under `tests/modules/<name>/`.
10. `uv run ruff format --check .`, `uv run ruff check .`, and `uv run pytest` all pass.
