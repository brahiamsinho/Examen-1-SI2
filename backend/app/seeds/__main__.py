# Ejecutar desde carpeta backend: python -m app.seeds
# Requiere DATABASE_URL y mismas vars que seed (sin depender de SEED_ADMIN_ON_START).
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


async def _run() -> None:
    import app.db_metadata  # noqa: F401 — registra todos los modelos (relación Cliente → Vehiculo).

    from app.core.database import AsyncSessionLocal
    from app.seeds.dev_admin import ensure_dev_admin

    async with AsyncSessionLocal() as session:
        await ensure_dev_admin(session, require_enabled_flag=False)
        await session.commit()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
