"""Ejecuta seeds idempotentes (arranque Docker, lifespan o `python -m app.seeds`)."""
from __future__ import annotations

import asyncio
import logging

from app.core.config import settings

_log = logging.getLogger(__name__)

_startup_seed_lock = asyncio.Lock()


def seeds_enabled_for_startup(*, run_all: bool = False) -> bool:
    """True si hay al menos un seed configurado para arranque."""
    if run_all:
        return True
    return bool(
        settings.SEED_ADMIN_ON_START
        or settings.SEED_CLIENTE_ON_START
        or settings.SEED_TALLER_ON_START
        or settings.SEED_TECNICO_ON_START
        or settings.SEED_DEMO_SANTA_CRUZ_ON_START
        or settings.SEED_DEMO_MEDIA_PRIORIDAD_ON_START
        or settings.SEED_STRESS_VISUAL_ON_START
        or settings.SEED_MULTI_ORGS_ON_START
        or settings.SEED_MULTI_ORG_EMERGENCIAS_ON_START
        or settings.SEED_TALLERES_RED_ON_START
    )


async def run_startup_seeds(*, run_all: bool = False, max_attempts: int = 8) -> None:
    """Aplica seeds según flags SEED_* (o todos si run_all=True)."""
    if not seeds_enabled_for_startup(run_all=run_all):
        return

    import app.db_metadata  # noqa: F401 — registra modelos ORM

    from app.core.database import AsyncSessionLocal
    from app.seeds.dev_admin import ensure_baseline_rol_permisos, ensure_dev_admin
    from app.seeds.dev_catalogos_vehiculo import ensure_catalogos_vehiculo_demo
    from app.seeds.dev_cliente import ensure_dev_cliente
    from app.seeds.dev_demo_media_prioridad import ensure_demo_media_prioridad
    from app.seeds.dev_demo_santa_cruz import ensure_demo_santa_cruz_datos
    from app.seeds.dev_stress_visual import ensure_stress_visual_seed
    from app.seeds.dev_multi_orgs import ensure_multi_orgs_seed
    from app.seeds.dev_multi_org_emergencias import ensure_multi_org_emergencias_seed
    from app.seeds.dev_tecnico import ensure_dev_tecnico
    from app.seeds.dev_taller import ensure_dev_taller
    from app.seeds.dev_talleres_red import ensure_talleres_red_demo_sc
    from app.seeds.dev_tenant import ensure_default_tenant

    async with _startup_seed_lock:
        last_err: BaseException | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                async with AsyncSessionLocal() as session:
                    tenant_id = await ensure_default_tenant(session)
                    await ensure_baseline_rol_permisos(session)
                    await ensure_catalogos_vehiculo_demo(session)

                    if run_all or settings.SEED_ADMIN_ON_START:
                        await ensure_dev_admin(session, require_enabled_flag=False)
                    if run_all or settings.SEED_CLIENTE_ON_START:
                        await ensure_dev_cliente(
                            session, tenant_id=tenant_id, require_enabled_flag=False
                        )
                    if run_all or settings.SEED_TALLER_ON_START:
                        await ensure_dev_taller(
                            session, tenant_id=tenant_id, require_enabled_flag=False
                        )
                    if run_all or settings.SEED_TECNICO_ON_START:
                        await ensure_dev_tecnico(
                            session, tenant_id=tenant_id, require_enabled_flag=False
                        )
                    if run_all or settings.SEED_DEMO_SANTA_CRUZ_ON_START:
                        await ensure_demo_santa_cruz_datos(session, require_enabled_flag=False)
                    if run_all or settings.SEED_DEMO_MEDIA_PRIORIDAD_ON_START:
                        await ensure_demo_media_prioridad(session, require_enabled_flag=False)
                    if run_all or settings.SEED_STRESS_VISUAL_ON_START:
                        await ensure_stress_visual_seed(session, require_enabled_flag=False)
                    if run_all or settings.SEED_MULTI_ORGS_ON_START:
                        await ensure_multi_orgs_seed(session, require_enabled_flag=False)
                    if run_all or settings.SEED_MULTI_ORG_EMERGENCIAS_ON_START:
                        await ensure_multi_org_emergencias_seed(session, require_enabled_flag=False)
                    if run_all or settings.SEED_TALLERES_RED_ON_START:
                        await ensure_talleres_red_demo_sc(
                            session, tenant_id=tenant_id, require_enabled_flag=False
                        )

                    await session.commit()
                _log.info("Seeds aplicados correctamente")
                return
            except Exception as exc:
                last_err = exc
                _log.warning(
                    "Seeds intento %s/%s: %s — reintento en 2s",
                    attempt,
                    max_attempts,
                    exc,
                )
                await asyncio.sleep(2)

        _log.error(
            "Seeds no pudieron tras %s intentos. Manual: docker compose exec backend python -m app.seeds",
            max_attempts,
            exc_info=last_err,
        )


def run_startup_seeds_sync(*, run_all: bool = False) -> None:
    asyncio.run(run_startup_seeds(run_all=run_all))
