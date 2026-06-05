# Notificaciones in-app y disparo de push (FCM) asociado.
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.comunicacion_y_notificaciones.dispositivos_push.push_notify import send_fcm_to_usuario
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.comunicacion_y_notificaciones.notificaciones import repository as notif_repository
from app.modules.comunicacion_y_notificaciones.notificaciones import tenant_guard
from app.modules.comunicacion_y_notificaciones.notificaciones.models import TipoNotificacionEnum
from app.modules.comunicacion_y_notificaciones.notificaciones.schemas import NotificacionRead


async def crear_notificacion_y_push(
    db: AsyncSession,
    *,
    usuario_destino_id: int,
    solicitud_id: int | None,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
    evento_id: str | None = None,
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
        evento_id=evento_id,
    )
    data = {
        "tipo": tipo.value,
        "notificacion_id": str(row.id),
        **({"solicitud_id": str(solicitud_id)} if solicitud_id is not None else {}),
    }
    await send_fcm_to_usuario(
        db,
        usuario_id=usuario_destino_id,
        titulo=titulo,
        cuerpo=mensaje,
        data=data,
        log_omitir_si_sin_tokens=True,
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
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
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
    tec = await tenant_guard.validar_tecnico_solicitud(db, solicitud=solicitud)
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
    rows = await notif_repository.list_notificaciones_usuario_por_tenant(
        db,
        usuario_id=user.id,
        tenant_id=user.tenant_id,
        solo_no_leidas=solo_no_leidas,
        limit=limit,
    )
    return [NotificacionRead.model_validate(x) for x in rows]


async def marcar_notificacion_leida(user, notif_id: int, db: AsyncSession) -> NotificacionRead:
    n = await notif_repository.get_notificacion_propia(
        db, notif_id=notif_id, usuario_id=user.id, tenant_id=user.tenant_id
    )
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    await notif_repository.marcar_notificacion_leida(db, n=n, leida_at=utc_now_naive())
    await db.commit()
    await db.refresh(n)
    return NotificacionRead.model_validate(n)
