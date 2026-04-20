from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comunicaciones.models import Notificacion, SolicitudMensaje, TipoNotificacionEnum, UsuarioFcmToken
from app.modules.emergencias.models import SolicitudEmergencia
from app.modules.talleres.models import Tecnico
from app.modules.usuarios.models import Cliente


async def get_solicitud_by_id(db: AsyncSession, solicitud_id: int) -> SolicitudEmergencia | None:
    r = await db.execute(select(SolicitudEmergencia).where(SolicitudEmergencia.id == solicitud_id))
    return r.scalar_one_or_none()


async def get_cliente_usuario_id(db: AsyncSession, *, cliente_id: int) -> int | None:
    r = await db.execute(select(Cliente.usuario_id).where(Cliente.id == cliente_id))
    row = r.scalar_one_or_none()
    return int(row) if row is not None else None


async def get_tecnico_usuario_id_for_solicitud(db: AsyncSession, *, tecnico_row_id: int) -> int | None:
    r = await db.execute(select(Tecnico.usuario_id).where(Tecnico.id == tecnico_row_id))
    row = r.scalar_one_or_none()
    return int(row) if row is not None else None


async def get_tecnico_id_for_usuario(db: AsyncSession, *, usuario_id: int) -> int | None:
    r = await db.execute(select(Tecnico.id).where(Tecnico.usuario_id == usuario_id))
    row = r.scalar_one_or_none()
    return int(row) if row is not None else None


async def insert_notificacion(
    db: AsyncSession,
    *,
    usuario_id: int,
    solicitud_id: int | None,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
    created_at,
) -> Notificacion:
    row = Notificacion(
        usuario_id=usuario_id,
        solicitud_id=solicitud_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        leida=False,
        created_at=created_at,
        leida_at=None,
    )
    db.add(row)
    await db.flush()
    return row


async def list_notificaciones_usuario(
    db: AsyncSession, *, usuario_id: int, solo_no_leidas: bool, limit: int
) -> list[Notificacion]:
    stmt = select(Notificacion).where(Notificacion.usuario_id == usuario_id).order_by(Notificacion.created_at.desc())
    if solo_no_leidas:
        stmt = stmt.where(Notificacion.leida.is_(False))
    stmt = stmt.limit(limit)
    r = await db.execute(stmt)
    return list(r.scalars().all())


async def get_notificacion_propia(db: AsyncSession, *, notif_id: int, usuario_id: int) -> Notificacion | None:
    r = await db.execute(
        select(Notificacion).where(Notificacion.id == notif_id, Notificacion.usuario_id == usuario_id)
    )
    return r.scalar_one_or_none()


async def marcar_notificacion_leida(db: AsyncSession, *, n: Notificacion, leida_at) -> None:
    n.leida = True
    n.leida_at = leida_at


async def list_mensajes_solicitud(db: AsyncSession, *, solicitud_id: int) -> list[SolicitudMensaje]:
    r = await db.execute(
        select(SolicitudMensaje)
        .where(SolicitudMensaje.solicitud_id == solicitud_id)
        .order_by(SolicitudMensaje.created_at.asc())
    )
    return list(r.scalars().all())


async def insert_mensaje(
    db: AsyncSession,
    *,
    solicitud_id: int,
    emisor_usuario_id: int,
    receptor_usuario_id: int,
    texto: str,
    created_at,
) -> SolicitudMensaje:
    row = SolicitudMensaje(
        solicitud_id=solicitud_id,
        emisor_usuario_id=emisor_usuario_id,
        receptor_usuario_id=receptor_usuario_id,
        mensaje=texto,
        created_at=created_at,
        leido_at=None,
    )
    db.add(row)
    await db.flush()
    return row


async def upsert_fcm_token(
    db: AsyncSession, *, usuario_id: int, token: str, platform: str | None, now
) -> UsuarioFcmToken:
    tbl = UsuarioFcmToken.__table__
    stmt = (
        pg_insert(tbl)
        .values(usuario_id=usuario_id, token=token, platform=platform, created_at=now, updated_at=now)
        .on_conflict_do_update(
            index_elements=[tbl.c.token],
            set_={"usuario_id": usuario_id, "platform": platform, "updated_at": now},
        )
    )
    await db.execute(stmt)
    await db.flush()
    r = await db.execute(select(UsuarioFcmToken).where(UsuarioFcmToken.token == token))
    return r.scalar_one()


async def delete_fcm_token(db: AsyncSession, *, usuario_id: int, token: str) -> int:
    r = await db.execute(
        delete(UsuarioFcmToken).where(
            UsuarioFcmToken.token == token,
            UsuarioFcmToken.usuario_id == usuario_id,
        )
    )
    return r.rowcount or 0


async def list_fcm_tokens_usuario(db: AsyncSession, *, usuario_id: int) -> list[str]:
    r = await db.execute(select(UsuarioFcmToken.token).where(UsuarioFcmToken.usuario_id == usuario_id))
    return [str(x[0]) for x in r.fetchall()]
