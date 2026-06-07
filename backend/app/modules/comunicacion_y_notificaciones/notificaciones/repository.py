from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comunicacion_y_notificaciones.notificaciones.models import Notificacion, TipoNotificacionEnum
from app.modules.incidentes.emergencias.models import SolicitudEmergencia


async def insert_notificacion(
    db: AsyncSession,
    *,
    usuario_id: int,
    solicitud_id: int | None,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
    created_at,
    evento_id: str | None = None,
) -> Notificacion:
    row = Notificacion(
        usuario_id=usuario_id,
        solicitud_id=solicitud_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        leida=False,
        evento_id=evento_id,
        created_at=created_at,
        leida_at=None,
    )
    db.add(row)
    await db.flush()
    return row


async def get_notificacion_por_evento_id(
    db: AsyncSession, *, evento_id: str
) -> Notificacion | None:
    r = await db.execute(select(Notificacion).where(Notificacion.evento_id == evento_id))
    return r.scalar_one_or_none()


async def list_notificaciones_usuario(
    db: AsyncSession, *, usuario_id: int, solo_no_leidas: bool, limit: int
) -> list[Notificacion]:
    stmt = (
        select(Notificacion)
        .where(Notificacion.usuario_id == usuario_id)
        .order_by(Notificacion.created_at.desc())
    )
    if solo_no_leidas:
        stmt = stmt.where(Notificacion.leida.is_(False))
    stmt = stmt.limit(limit)
    r = await db.execute(stmt)
    return list(r.scalars().all())


async def list_notificaciones_usuario_por_tenant(
    db: AsyncSession,
    *,
    usuario_id: int,
    tenant_id: int | None,
    solo_no_leidas: bool,
    limit: int,
) -> list[Notificacion]:
    if tenant_id is None:
        return await list_notificaciones_usuario(
            db, usuario_id=usuario_id, solo_no_leidas=solo_no_leidas, limit=limit
        )
    stmt = (
        select(Notificacion)
        .outerjoin(SolicitudEmergencia, Notificacion.solicitud_id == SolicitudEmergencia.id)
        .where(Notificacion.usuario_id == usuario_id)
        .where(
            (Notificacion.solicitud_id.is_(None))
            | (SolicitudEmergencia.tenant_id == tenant_id)
        )
        .order_by(Notificacion.created_at.desc())
    )
    if solo_no_leidas:
        stmt = stmt.where(Notificacion.leida.is_(False))
    stmt = stmt.limit(limit)
    r = await db.execute(stmt)
    return list(r.scalars().unique().all())


async def get_notificacion_propia(
    db: AsyncSession, *, notif_id: int, usuario_id: int, tenant_id: int | None = None
) -> Notificacion | None:
    stmt = select(Notificacion).where(Notificacion.id == notif_id, Notificacion.usuario_id == usuario_id)
    if tenant_id is not None:
        stmt = stmt.outerjoin(
            SolicitudEmergencia, Notificacion.solicitud_id == SolicitudEmergencia.id
        ).where(
            (Notificacion.solicitud_id.is_(None))
            | (SolicitudEmergencia.tenant_id == tenant_id)
        )
    r = await db.execute(stmt)
    return r.scalar_one_or_none()


async def marcar_notificacion_leida(db: AsyncSession, *, n: Notificacion, leida_at) -> None:
    n.leida = True
    n.leida_at = leida_at
