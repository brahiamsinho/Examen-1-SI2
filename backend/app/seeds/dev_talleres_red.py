# Seed idempotente: al menos 5 talleres ACTIVO en demo-sc + horarios default.
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.acceso_y_administracion.roles.models import Rol
from app.seeds.talleres_red_seed import (
    DEMO_SC_EXTRA_TALLERES,
    DEMO_SC_TECNICOS_RED,
    ensure_horarios_y_disponibilidad_tenant,
    ensure_min_talleres_red,
    ensure_tecnicos_red,
)

logger = logging.getLogger(__name__)


async def _rol_taller_responsable_id(db: AsyncSession) -> int | None:
    r = await db.execute(select(Rol.id).where(Rol.nombre == "TALLER_RESPONSABLE"))
    row = r.scalar_one_or_none()
    if row is None:
        logger.error("Seed talleres red: falta rol TALLER_RESPONSABLE.")
        return None
    return int(row)


async def ensure_talleres_red_demo_sc(
    db: AsyncSession,
    *,
    tenant_id: int,
    require_enabled_flag: bool = True,
) -> None:
    if require_enabled_flag and not settings.SEED_TALLERES_RED_ON_START:
        return

    rol_id = await _rol_taller_responsable_id(db)
    if rol_id is None:
        return

    total = await ensure_min_talleres_red(
        db,
        tenant_id=tenant_id,
        rol_taller_responsable_id=rol_id,
        extra_defs=DEMO_SC_EXTRA_TALLERES,
        min_count=6,
    )
    await ensure_horarios_y_disponibilidad_tenant(db, tenant_id)
    await ensure_tecnicos_red(db, tenant_id=tenant_id, defs=DEMO_SC_TECNICOS_RED)
    logger.info("Seed talleres red demo-sc: %s talleres activos (tenant_id=%s).", total, tenant_id)
