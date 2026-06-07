# Validación de tenant al emitir/consultar notificaciones.
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.clientes_y_vehiculos.clientes.models import Cliente
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico

_log = logging.getLogger(__name__)


def tenants_coinciden(
    solicitud_tenant_id: int | None,
    actor_tenant_id: int | None,
) -> bool:
    if solicitud_tenant_id is None or actor_tenant_id is None:
        return True
    return solicitud_tenant_id == actor_tenant_id


async def validar_destinatario_solicitud(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    usuario_destino_id: int,
) -> bool:
    res = await db.execute(select(Usuario.tenant_id).where(Usuario.id == usuario_destino_id))
    actor_tenant_id = res.scalar_one_or_none()
    if actor_tenant_id is None:
        _log.warning(
            "Notificación omitida: usuario destino %s no existe (solicitud %s)",
            usuario_destino_id,
            solicitud.id,
        )
        return False
    if not tenants_coinciden(solicitud.tenant_id, actor_tenant_id):
        _log.warning(
            "Notificación omitida: tenant destino %s != solicitud %s (solicitud_id=%s)",
            actor_tenant_id,
            solicitud.tenant_id,
            solicitud.id,
        )
        return False
    return True


async def validar_cliente_solicitud(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
) -> Cliente | None:
    res = await db.execute(select(Cliente).where(Cliente.id == solicitud.cliente_id))
    cli = res.scalar_one_or_none()
    if cli is None:
        return None
    if not tenants_coinciden(solicitud.tenant_id, cli.tenant_id):
        _log.warning("Notificación cliente omitida por tenant (solicitud_id=%s)", solicitud.id)
        return None
    return cli


async def validar_tecnico_solicitud(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
) -> Tecnico | None:
    if solicitud.tecnico_id is None:
        return None
    res = await db.execute(select(Tecnico).where(Tecnico.id == solicitud.tecnico_id))
    tec = res.scalar_one_or_none()
    if tec is None:
        return None
    res_t = await db.execute(select(Taller.tenant_id).where(Taller.id == tec.taller_id))
    taller_tenant = res_t.scalar_one_or_none()
    if not tenants_coinciden(solicitud.tenant_id, taller_tenant):
        _log.warning("Notificación técnico omitida por tenant (solicitud_id=%s)", solicitud.id)
        return None
    return tec
