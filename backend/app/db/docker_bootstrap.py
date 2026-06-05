"""Migraciones y seeds antes de uvicorn (entrypoint Docker)."""
from __future__ import annotations

import logging
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.seeds.runner import run_startup_seeds_sync, seeds_enabled_for_startup

_log = logging.getLogger(__name__)
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_MIGRATIONS_DIR = _BACKEND_ROOT / "migrations"


def _sync_database_url() -> str:
    url = settings.DATABASE_URL
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg", 1)
    return url


def wait_for_db(*, max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _log.info("Base de datos disponible (intento %s)", attempt)
            return
        except OperationalError as exc:
            _log.warning(
                "Esperando Postgres (%s/%s): %s",
                attempt,
                max_attempts,
                exc.orig if hasattr(exc, "orig") else exc,
            )
            time.sleep(delay_seconds)
    raise RuntimeError("Postgres no respondió a tiempo para migraciones/seeds")


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables "
            "  WHERE table_schema = 'public' AND table_name = :name"
            ")"
        ),
        {"name": table_name},
    ).scalar_one()
    return bool(row)


def _alembic_version(conn) -> str | None:
    if not _table_exists(conn, "alembic_version"):
        return None
    return conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one_or_none()


def run_alembic_migrations() -> None:
    engine = create_engine(_sync_database_url())
    with engine.connect() as conn:
        schema_ready = _table_exists(conn, "roles")
        current = _alembic_version(conn)

    if schema_ready and current is None:
        _log.info("Esquema ya creado (initdb) sin alembic_version → alembic stamp head")
        subprocess.check_call(["alembic", "stamp", "head"], cwd=_BACKEND_ROOT)
        return

    if not schema_ready and current is None:
        _log.warning(
            "BD sin esquema base: Postgres debería aplicar init.sql en primer arranque. "
            "Intentando alembic upgrade head de todas formas."
        )

    _log.info("Alembic upgrade head (versión actual: %s)", current or "ninguna")
    subprocess.check_call(["alembic", "upgrade", "head"], cwd=_BACKEND_ROOT)


def run_sql_migrations() -> None:
    """Aplica *.sql de backend/migrations/ (excepto init.sql) con tabla de control."""
    engine = create_engine(_sync_database_url())
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app_sql_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        applied = {
            row[0]
            for row in conn.execute(text("SELECT filename FROM app_sql_migrations")).fetchall()
        }

    sql_files = sorted(
        path
        for path in _MIGRATIONS_DIR.glob("*.sql")
        if path.name != "init.sql" and not path.name.startswith("99_")
    )
    for path in sql_files:
        if path.name in applied:
            continue
        _log.info("Aplicando migración SQL: %s", path.name)
        sql = path.read_text(encoding="utf-8")
        with engine.begin() as conn:
            conn.execute(text(sql))
            conn.execute(
                text("INSERT INTO app_sql_migrations (filename) VALUES (:filename)"),
                {"filename": path.name},
            )


def run_bootstrap() -> None:
    if settings.RUN_MIGRATIONS_ON_START:
        wait_for_db()
        run_alembic_migrations()
        run_sql_migrations()
    else:
        _log.info("RUN_MIGRATIONS_ON_START=false — migraciones omitidas")

    run_all_seeds = settings.RUN_SEEDS_ON_START
    if run_all_seeds or seeds_enabled_for_startup():
        if not settings.RUN_MIGRATIONS_ON_START:
            wait_for_db()
        run_startup_seeds_sync(run_all=run_all_seeds)
    else:
        _log.info("Sin seeds configurados — seeds omitidos")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    try:
        run_bootstrap()
    except Exception:
        _log.exception("Bootstrap Docker falló")
        sys.exit(1)


if __name__ == "__main__":
    main()
