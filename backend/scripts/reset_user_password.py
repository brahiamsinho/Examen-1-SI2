"""Reset password for a user by email (dev/support)."""
from __future__ import annotations

import sys

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.core.timeutil import utc_now_naive


def _sync_database_url() -> str:
    url = settings.DATABASE_URL
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg", 1)
    return url


def reset_password(email: str, new_password: str) -> None:
    engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    new_hash = hash_password(new_password)
    with engine.begin() as conn:
        conn.execute(text("SELECT set_config('app.bypass_rls', 'on', true)"))
        r = conn.execute(
            text("SELECT id FROM usuarios WHERE email = :email"),
            {"email": email},
        )
        row = r.first()
        if row is None:
            raise SystemExit(f"Usuario no encontrado: {email}")
        conn.execute(
            text(
                "UPDATE usuarios SET password_hash = :hash, updated_at = :ts WHERE id = :id"
            ),
            {"hash": new_hash, "ts": utc_now_naive(), "id": row[0]},
        )
    ok = verify_password(new_password, new_hash)
    print(f"OK reset {email} verify={ok}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python -m scripts.reset_user_password EMAIL NUEVA_PASSWORD")
    reset_password(sys.argv[1], sys.argv[2])
