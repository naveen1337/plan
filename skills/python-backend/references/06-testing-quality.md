# Testing and Quality

## Tooling

- `pytest` for all tests. Async tests use `pytest-asyncio` (`asyncio_mode = "auto"` in `pyproject.toml`).
- HTTP tests use `httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")`.
- `ruff` for lint and format. Configure once in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "S", "ASYNC"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Test layout

- Mirror the app: `tests/modules/<name>/test_<name>_<layer>.py`.
- Unit-test `utils` and `service` without I/O (fake helpers or monkeypatch).
- Test `helper` against a real Postgres (docker or CI service) for SQL; mock only `httpx` via `respx` or a fake transport.
- Test `ctrl` through the ASGI client: status codes, validation errors (422), auth errors (401), response shape.
- Do not assert on internal call counts unless the behavior requires it.

## Fixtures

- `conftest.py` provides: test `Settings` override, app instance, ASGI client, DB pool for integration tests, a signed token factory.
- Never read the developer's real `.env` in tests.

## Minimum coverage per feature

For each feature:

1. `utils`: one test per pure function, including edge cases (empty, whitespace, unicode).
2. `service`: happy path plus each domain error.
3. `ctrl`: success response, invalid body (422), missing/invalid token (401) where auth applies, not-found (404) and conflict (409) mapping.
4. `helper`: SQL returns expected rows; parameterized values round-trip.

## Verification commands

Run from `backend/`:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Never report a backend task as done with any of these failing. If a check cannot run (missing Postgres, missing credentials), say so explicitly in the report instead of marking it passed.

## Review checklist (layer violations)

- ctrl imports `helper`? → move logic to service.
- service imports `fastapi`/`starlette`? → raise domain error, map in ctrl/errors handler.
- helper raises `HTTPException`? → return data or raise domain error.
- utils imports `psycopg2`, `httpx`, `os.environ`, `datetime.now()`? → inject the value, move I/O out.
- Any f-string SQL? → rewrite with pypika + parameters.
- Any `sqlalchemy` / `sqlmodel` import? → rewrite with pypika + psycopg2.
