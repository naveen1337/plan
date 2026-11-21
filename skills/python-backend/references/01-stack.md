# Stack and Tooling

## Package manager: uv

```bash
uv init --package backend        # only when bootstrapping
uv add fastapi uvicorn[standard] pydantic pydantic-settings
uv add psycopg2-binary pypika redis duckdb httpx orjson pyjwt tenacity pyyaml structlog apscheduler
uv add --dev pytest ruff
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format .
```

- Always use `uv add` / `uv remove`; never edit dependency lists by hand without re-locking.
- Commit `uv.lock`.
- Use `uv run` for every tool invocation so the project venv is used.
- Target Python `>=3.13` in `pyproject.toml`.
- Use the latest stable FastAPI release. Do not pin to an old version without a reason written in the plan.

## Dependency map

| Concern | Package | Import | Notes |
|---|---|---|---|
| Web framework | `fastapi` | `fastapi` | Latest stable |
| ASGI server | `uvicorn` | — | `uvicorn[standard]` |
| Validation | `pydantic` v2 | `pydantic` | Only validation layer |
| Settings/secrets | `pydantic-settings` | `pydantic_settings` | `SecretStr` for secrets |
| Postgres driver | `psycopg2-binary` (dev) / `psycopg2` (prod build) | `psycopg2` | Sync; wrap with threadpool |
| SQL builder | `pypika` | `pypika` | Use `PostgreSQLQuery` dialect |
| Cache | `redis` | `redis.asyncio` | Async client |
| Local cache | stdlib | `sqlite3` | Local only |
| Analytics | `duckdb` | `duckdb` | Read-heavy queries |
| HTTP client | `httpx` | `httpx` | `AsyncClient` |
| Fast JSON | `orjson` | `orjson` | Large payloads |
| JWT | `pyjwt` | `jwt` | Explicit algorithms |
| Retries | `tenacity` | `tenacity` | Async-compatible |
| YAML | `pyyaml` | `yaml` | `safe_load` only |
| Logging | `structlog` | `structlog` | Structured events |
| Scheduler | `apscheduler` | `apscheduler` | Use latest stable line |
| Tests | `pytest` | `pytest` | `httpx` test client |
| Lint/format | `ruff` | — | Replaces black/isort/flake8 |

## Forbidden / avoid

- ORMs: SQLAlchemy, SQLModel, Django ORM, Tortoise, Peewee.
- Other formatters/linters alongside ruff (black, isort, flake8, pylint).
- Other web frameworks in the same service (Flask, Starlette-only apps for business routes).
- `requests` (use `httpx`), `json` for large payloads (use `orjson`), `python-dotenv` as config source (use `pydantic-settings`).
- New dependencies not listed here require a stated reason in the plan or PR.

## Async preference

- Prefer async libraries: `httpx.AsyncClient`, `redis.asyncio`, `aiosqlite` (if async SQLite is needed), APScheduler `AsyncIOScheduler`.
- Sync-only libraries in this stack: `psycopg2`, `duckdb`, stdlib `sqlite3`. Call them through `starlette.concurrency.run_in_threadpool` from async code, or define the route as sync `def`.
