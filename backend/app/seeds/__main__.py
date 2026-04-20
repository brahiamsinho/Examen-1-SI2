# Ejecutar desde carpeta backend: python -m app.seeds
# Requiere DATABASE_URL y mismas vars que seed (sin depender de SEED_ADMIN_ON_START).
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


async def _run() -> None:
    import app.db_metadata  # noqa: F401 — registra todos los modelos (relación Cliente → Vehiculo).

    from app.core.database import AsyncSessionLocal
    from app.seeds.dev_admin import ensure_baseline_rol_permisos, ensure_dev_admin
    from app.seeds.dev_catalogos_vehiculo import ensure_catalogos_vehiculo_demo
    from app.seeds.dev_cliente import ensure_dev_cliente
    from app.seeds.dev_taller import ensure_dev_taller
    from app.seeds.dev_tecnico import ensure_dev_tecnico

    async with AsyncSessionLocal() as session:
        await ensure_baseline_rol_permisos(session)
        await ensure_catalogos_vehiculo_demo(session)
        await ensure_dev_admin(session, require_enabled_flag=False)
        await ensure_dev_cliente(session, require_enabled_flag=False)
        await ensure_dev_taller(session, require_enabled_flag=False)
        await ensure_dev_tecnico(session, require_enabled_flag=False)
        await session.commit()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
