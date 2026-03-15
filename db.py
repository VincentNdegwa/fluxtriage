import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, create_engine

from config import settings


_metadata = MetaData()
_event_table_cache: Table | None = None


def _table_name() -> str:
    return settings.triage_table


def _get_engine():
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for persistence")
    return create_engine(settings.database_url, pool_pre_ping=True)


def _event_table() -> Table:
    global _event_table_cache
    if _event_table_cache is not None:
        return _event_table_cache

    _event_table_cache = Table(
        _table_name(),
        _metadata,
        Column("job_id", String(64), primary_key=True),
        Column("request_json", Text, nullable=False),
        Column("result_json", Text, nullable=True),
        Column("provider", String(32), nullable=True),
        Column("latency_ms", Integer, nullable=True),
        Column("error", Text, nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        extend_existing=True,
    )
    return _event_table_cache


def init_db() -> None:
    engine = _get_engine()
    _metadata.create_all(engine)


def insert_event(job_id: str, request: dict[str, Any]) -> None:
    engine = _get_engine()
    table = _event_table()
    now = datetime.now(timezone.utc)
    payload = {
        "job_id": job_id,
        "request_json": json.dumps(request),
        "created_at": now,
        "updated_at": now,
    }
    with engine.begin() as conn:
        conn.execute(table.insert().values(**payload))


def update_event(
    job_id: str,
    result: dict[str, Any] | None,
    provider: str | None,
    latency_ms: int | None,
    error: str | None,
) -> None:
    engine = _get_engine()
    table = _event_table()
    now = datetime.now(timezone.utc)
    payload = {
        "result_json": json.dumps(result) if result else None,
        "provider": provider,
        "latency_ms": latency_ms,
        "error": error,
        "updated_at": now,
    }
    with engine.begin() as conn:
        conn.execute(
            table.update().where(table.c.job_id == job_id).values(**payload)
        )
