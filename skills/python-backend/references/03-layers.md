# Layer Contracts

Each module is split into four code files plus a schema file. Each file has one job.

## `<name>_ctrl.py` — transport layer

Responsibilities: route definition, Pydantic validation of input, auth, calling the service, building the response, mapping errors to HTTP.

Must NOT: contain SQL, `httpx`, Redis or business rules, or import helpers.

```python
# app/modules/user/user_ctrl.py
from fastapi import APIRouter, Depends, status

from app.core.security import TokenClaims, decode_access_token
from app.modules.user import user_service
from app.modules.user.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


def current_claims(claims: TokenClaims = Depends(decode_access_token)) -> TokenClaims:
    return claims


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate) -> UserResponse:
    user = await user_service.create_user(body.model_dump())
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def read_me(claims: TokenClaims = Depends(current_claims)) -> UserResponse:
    user = await user_service.get_user(claims.sub)
    return UserResponse.model_validate(user)
```

Auth rule: `decode_access_token` lives in `core/security.py` and is used as a dependency. Role/permission checks happen in the ctrl (`Depends`) before calling the service.

## `<name>_schema.py` — boundary models

```python
# app/modules/user/user_schema.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=256)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str
```

- Request models use `extra="forbid"`. Never return password or secret fields in response models.

## `<name>_service.py` — business logic

Responsibilities: enforce business rules, orchestrate helpers, call other modules' services, raise domain errors, emit business events/logs.

Must NOT: import `fastapi`, `starlette`, return HTTP objects, build SQL, call `httpx` directly.

```python
# app/modules/user/user_service.py
from app.core.errors import ConflictError, NotFoundError
from app.modules.user import user_helper, user_utils


async def create_user(data: dict) -> dict:
    clean = user_utils.normalize_user_input(data)
    if await user_helper.find_user_by_email(clean["email"]) is not None:
        raise ConflictError("email already registered")
    password_hash = user_utils.hash_password_placeholder(clean.pop("password"))
    return await user_helper.insert_user({**clean, "password_hash": password_hash})


async def get_user(user_id: int) -> dict:
    user = await user_helper.find_user_by_id(user_id)
    if user is None:
        raise NotFoundError("user not found")
    return user
```

Note: password hashing must use a real password hashing library approved in the plan (for example `argon2-cffi` or `bcrypt`). The placeholder name above is illustrative only; do not ship it.

## `<name>_helper.py` — I/O and support functions

Responsibilities: database access (pypika + psycopg2), Redis/SQLite cache, DuckDB queries, `httpx` calls with tenacity retries, file reads, payload parsing.

Must NOT: enforce business rules, raise HTTP errors, know about routes.

```python
# app/modules/user/user_helper.py
from pypika import PostgreSQLQuery as PgQuery, Table
from pypika.terms import Parameter
from starlette.concurrency import run_in_threadpool

from app.core.db import get_conn

users = Table("users")


def _find_user_by_email_sync(email: str) -> dict | None:
    sql = str(
        PgQuery.from_(users)
        .select(users.id, users.email, users.display_name)
        .where(users.email == Parameter("%s"))
    )
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (email,))
        row = cur.fetchone()
    return None if row is None else {"id": row[0], "email": row[1], "display_name": row[2]}


async def find_user_by_email(email: str) -> dict | None:
    return await run_in_threadpool(_find_user_by_email_sync, email)
```

Rules:
- Blocking psycopg2 code lives in `_sync` functions and is exposed as `async` via `run_in_threadpool`. Do not call psycopg2 inside `async def` directly.
- Values always go through the parameter tuple passed to `cursor.execute`. The `Parameter("%s")` placeholder is the psycopg2 style; never interpolate values into the SQL string.
- The snippet shows the pattern; apply `ruff format` and keep imports sorted (`ruff check --fix`) in real code.

## `<name>_utils.py` — pure functions

Responsibilities: validation beyond Pydantic (domain rules that are pure), cleaning, normalization, parsing of plain values, computation.

Must NOT: perform I/O, read env/config, log, import helper/service/ctrl, use `datetime.now()` or random values without injection.

```python
# app/modules/user/user_utils.py
def normalize_user_input(data: dict) -> dict:
    return {
        "email": data["email"].strip().lower(),
        "display_name": " ".join(data["display_name"].split()),
        "password": data["password"],
    }


def is_disposable_domain(email: str, blocked_domains: frozenset[str]) -> bool:
    return email.rsplit("@", 1)[-1] in blocked_domains
```

Pure means: same input → same output, no side effects, no hidden dependencies. Pass blocked lists, clocks, and ids as arguments.

## Cross-module rules

- A service may call another module's **service**, never its helper, ctrl, or utils-with-I/O.
- A ctrl may import only its own module's schema and service, plus `core/` dependencies.
- Shared pure logic used by 2+ modules and free of domain meaning goes to `core/`. Otherwise duplicate small logic rather than creating a hidden coupling.
