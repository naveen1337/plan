# Data Access

## Postgres: psycopg2 + pypika (no ORM)

Pool in `core/db.py`:

```python
# app/core/db.py
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from app.core.config import get_settings

_pool: ThreadedConnectionPool | None = None


def open_pool() -> None:
    global _pool
    s = get_settings()
    _pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=s.db_pool_max,
        dsn=s.database_url.get_secret_value(),
    )


def close_pool() -> None:
    if _pool is not None:
        _pool.closeall()


@contextmanager
def get_conn() -> Iterator[psycopg2.extensions.connection]:
    if _pool is None:
        raise RuntimeError("database pool not opened")
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)
```

Rules:
- Use `ThreadedConnectionPool` (psycopg2 is thread-safe at the pool level, not async).
- Commit/rollback is handled by `get_conn()`. Helpers do not call `commit()` themselves.
- Build SQL with pypika using the Postgres dialect:

```python
from pypika import PostgreSQLQuery as PgQuery, Table, Order
orders = Table("orders")
sql = str(
    PgQuery.from_(orders)
    .select(orders.id, orders.total)
    .where(orders.user_id == Parameter("%s"))
    .orderby(orders.created_at, order=Order.desc)
    .limit(Parameter("%s"))
)
cur.execute(sql, (user_id, limit))
```

- pypika generates SQL text; psycopg2 binds values. Values never enter the SQL string.
- Schema changes are versioned `.sql` migration files under `backend/migrations/`. No `create_all`, no ORM metadata.
- Keep queries in helpers. Services receive plain dicts or dataclasses.
- Use transactions for multi-statement writes: one `get_conn()` block per unit of work.

## Redis cache

```python
# app/core/cache.py
from redis.asyncio import Redis

from app.core.config import get_settings


def create_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url.get_secret_value(), decode_responses=True)
```

Rules:
- Create once in lifespan; close on shutdown with `await redis.aclose()`.
- Every key has a TTL and a namespace prefix: `<module>:<entity>:<id>`.
- Cache-aside pattern lives in helpers: read cache → on miss read DB → write cache with TTL.
- Invalidate on write in the service via a helper call, not inline in ctrl.
- Cached values are JSON via `orjson` for large objects.

## SQLite local cache

- Use stdlib `sqlite3` (or `aiosqlite` when async access is required) through `core/local_cache.py`.
- Local, single-process use only. Do not use it as a shared store across instances.
- Store with a `expires_at` column; purge expired rows in a scheduled job.

## DuckDB analytics

- Use `duckdb` for read-heavy analytical queries: aggregations, scans over Parquet/CSV exports, report generation.
- Open a connection per request or per job via `core/analytics.py`; do not share one connection across threads.
- Run through `run_in_threadpool` (sync library).
- Never use DuckDB as the write path for transactional data.
- Query text is parameterized (`con.execute(sql, [params])`); never format user input into SQL.

## Migrations

- Plain `.sql` files, numbered: `0001_create_users.sql`, `0002_add_orders.sql`.
- Applied by a small runner script in `backend/scripts/` (not by the app on import).
