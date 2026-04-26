# Notificaciones in-app y disparo de push (FCM) asociado.
from __future__ import annotations

import asyncio
import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.dispositivos_push import fcm_client
from app.modules.dispositivos_push import repository as fcm_repository
from app.modules.emergencias.models import SolicitudEmergencia
from app.modules.notificaciones import repository as notif_repository
from app.modules.notificaciones.models import TipoNotificacionEnum
from app.modules.notificaciones.schemas import NotificacionRead
from app.modules.talleres.models import Tecnico
from app.modules.usuarios.models import Cliente

_log = logging.getLogger(__name__)


async def _notificar_push(
    db: AsyncSession,
    *,
    usuario_destino_id: int,
    titulo: str,
    cuerpo: str,
    data: dict[str, str],
) -> None:
    if not settings.FCM_ENABLED:
        return
    tokens = await fcm_repository.list_fcm_tokens_usuario(db, usuario_id=usuario_destino_id)
    if not tokens:
        _log.info(
            "FCM omitido: usuario_id=%s sin tokens registrados (titulo=%r)",
            usuario_destino_id,
            titulo,
        )
        return
    try:
        await asyncio.to_thread(
            fcm_client.send_push_multicast_sync,
            tokens,
            title=titulo,
            body=cuerpo,
            data=data,
        )
    except Exception:
        _log.exception("Error en hilo FCM")


async def crear_notificacion_y_push(
    db: AsyncSession,
    *,
    usuario_destino_id: int,
    solicitud_id: int | None,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
) -> NotificacionRead:
    now = utc_now_naive()
    row = await notif_repository.insert_notificacion(
        db,
        usuario_id=usuario_destino_id,
        solicitud_id=solicitud_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        created_at=now,
    )
    data = {
        "tipo": tipo.value,
        "notificacion_id": str(row.id),
        **({"solicitud_id": str(solicitud_id)} if solicitud_id is not None else {}),
    }
    await _notificar_push(
        db, usuario_destino_id=usuario_destino_id, titulo=titulo, cuerpo=mensaje, data=data
    )
    return NotificacionRead.model_validate(row)


async def notificar_cliente_solicitud_emergencia(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
) -> None:
    res = await db.execute(select(Cliente).where(Cliente.id == solicitud.cliente_id))
    cli = res.scalar_one_or_none()
    if cli is None:
        return
    await crear_notificacion_y_push(
        db,
        usuario_destino_id=cli.usuario_id,
        solicitud_id=solicitud.id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
    )


async def notificar_tecnico_solicitud_emergencia(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
) -> None:
    if solicitud.tecnico_id is None:
        return
    res = await db.execute(select(Tecnico).where(Tecnico.id == solicitud.tecnico_id))
    tec = res.scalar_one_or_none()
    if tec is None:
        return
    await crear_notificacion_y_push(
        db,
        usuario_destino_id=tec.usuario_id,
        solicitud_id=solicitud.id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
    )


async def listar_notificaciones(
    user, db: AsyncSession, *, solo_no_leidas: bool, limit: int
) -> list[NotificacionRead]:
    rows = await notif_repository.list_notificaciones_usuario(
        db, usuario_id=user.id, solo_no_leidas=solo_no_leidas, limit=limit
    )
    return [NotificacionRead.model_validate(x) for x in rows]


async def marcar_notificacion_leida(user, notif_id: int, db: AsyncSession) -> NotificacionRead:
    n = await notif_repository.get_notificacion_propia(db, notif_id=notif_id, usuario_id=user.id)
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    await notif_repository.marcar_notificacion_leida(db, n=n, leida_at=utc_now_naive())
    await db.commit()
    await db.refresh(n)
    return NotificacionRead.model_validate(n)
