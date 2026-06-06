# Emergencias operativas demo para cada organización multi-org (bandeja, historial, comisiones).
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.clientes_y_vehiculos.clientes.models import Cliente
from app.modules.clientes_y_vehiculos.vehiculos.models import Vehiculo
from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico
from app.seeds.demo_emergencias_pack import seed_emergencias_operativas_taller
from app.seeds.identidades_multi_org import MULTI_ORGS, OrgSeed

logger = logging.getLogger(__name__)


async def _ctx_org(
    db: AsyncSession,
    org: OrgSeed,
) -> tuple[int, int, int, int, int, list[int], int] | None:
    """tenant_id, taller_id, tecnico_id, cliente_id, uid_cliente, vehiculo_ids, uid_resp."""
    tenant = await tenants_service.get_tenant_by_slug(db, org.slug)
    if tenant is None:
        return None

    email_resp = org.email(org.responsable)
    ur = await db.execute(select(Usuario).where(Usuario.email == email_resp))
    u_resp = ur.scalar_one_or_none()
    if u_resp is None:
        logger.warning("Multi-org emergencias: sin responsable %s", email_resp)
        return None

    tr = await db.execute(
        select(Taller).where(Taller.usuario_responsable_id == u_resp.id, Taller.tenant_id == tenant.id)
    )
    taller = tr.scalar_one_or_none()
    if taller is None:
        return None

    email_tec = org.email(org.tecnicos[0])
    ut = (await db.execute(select(Usuario).where(Usuario.email == email_tec))).scalar_one_or_none()
    tecnico_id = 0
    if ut is not None:
        tec = (await db.execute(select(Tecnico).where(Tecnico.usuario_id == ut.id))).scalar_one_or_none()
        if tec is not None:
            tecnico_id = tec.id

    email_cli = org.email(org.clientes[0])
    uc = (await db.execute(select(Usuario).where(Usuario.email == email_cli))).scalar_one_or_none()
    if uc is None:
        return None
    cli = (await db.execute(select(Cliente).where(Cliente.usuario_id == uc.id))).scalar_one_or_none()
    if cli is None:
        return None

    vrows = await db.execute(
        select(Vehiculo.id).where(Vehiculo.cliente_id == cli.id).order_by(Vehiculo.id)
    )
    vids = [int(x[0]) for x in vrows.fetchall()]
    if not vids:
        return None

    return tenant.id, taller.id, tecnico_id, cli.id, uc.id, vids, u_resp.id


async def ensure_multi_org_emergencias_seed(
    db: AsyncSession,
    *,
    require_enabled_flag: bool = True,
) -> None:
    if require_enabled_flag and not settings.SEED_MULTI_ORG_EMERGENCIAS_ON_START:
        return

    total = 0
    for org in MULTI_ORGS:
        ctx = await _ctx_org(db, org)
        if ctx is None:
            logger.warning("Multi-org emergencias: omitido %s (falta contexto).", org.slug)
            continue
        tenant_id, taller_id, tecnico_id, cliente_id, uid_cli, vids, uid_resp = ctx
        marker = f"[MULTI-ORG-{org.slug}]"
        n = await seed_emergencias_operativas_taller(
            db,
            marker=marker,
            tenant_id=tenant_id,
            taller_id=taller_id,
            tecnico_id=tecnico_id,
            cliente_id=cliente_id,
            uid_cliente=uid_cli,
            uid_resp=uid_resp,
            vehiculo_ids=vids,
            lat=org.lat,
            lng=org.lng,
        )
        total += n

    if total:
        logger.info("Multi-org emergencias: %s solicitudes nuevas en total.", total)
    else:
        logger.info("Multi-org emergencias: sin inserciones (ya existían o falta contexto).")
