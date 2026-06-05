# Emisor central de notificaciones por eventos de atención (push + in-app).
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.comunicacion_y_notificaciones.notificaciones import repository as notif_repository
from app.modules.comunicacion_y_notificaciones.notificaciones import service as notif_service
from app.modules.comunicacion_y_notificaciones.notificaciones import tenant_guard
from app.modules.comunicacion_y_notificaciones.notificaciones.models import TipoNotificacionEnum
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.talleres_y_tecnicos.talleres.models import Taller


def _evento_id(solicitud: SolicitudEmergencia, suffix: str) -> str:
    tid = solicitud.tenant_id if solicitud.tenant_id is not None else 0
    return f"t{tid}:s{solicitud.id}:{suffix}"


async def _emit(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    usuario_destino_id: int,
    tipo: TipoNotificacionEnum,
    titulo: str,
    mensaje: str,
    evento_suffix: str,
) -> None:
    if not await tenant_guard.validar_destinatario_solicitud(
        db, solicitud=solicitud, usuario_destino_id=usuario_destino_id
    ):
        return
    eid = _evento_id(solicitud, evento_suffix)
    if await notif_repository.get_notificacion_por_evento_id(db, evento_id=eid) is not None:
        return
    await notif_service.crear_notificacion_y_push(
        db,
        usuario_destino_id=usuario_destino_id,
        solicitud_id=solicitud.id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        evento_id=eid,
    )


async def _usuario_responsable_taller(db: AsyncSession, taller_id: int) -> int | None:
    res = await db.execute(select(Taller.usuario_responsable_id).where(Taller.id == taller_id))
    return res.scalar_one_or_none()


async def on_solicitud_pendiente_taller(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    taller_id: int,
) -> None:
    uid = await _usuario_responsable_taller(db, taller_id)
    if uid is None:
        return
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=uid,
        tipo=TipoNotificacionEnum.SOLICITUD_PENDIENTE_TALLER,
        titulo="Nueva solicitud pendiente",
        mensaje=f"Hay una emergencia #{solicitud.id} esperando respuesta de tu taller.",
        evento_suffix=f"taller{taller_id}:pendiente",
    )


async def on_taller_acepto(db: AsyncSession, *, solicitud: SolicitudEmergencia) -> None:
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
    if cli is None:
        return
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=cli.usuario_id,
        tipo=TipoNotificacionEnum.TALLER_ASIGNADO,
        titulo="Taller asignado",
        mensaje="Un taller aceptó atender tu emergencia. Puedes ver el detalle en la app.",
        evento_suffix="cliente:taller_acepto",
    )


async def on_taller_rechazo(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    taller_id: int,
) -> None:
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
    if cli is None:
        return
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=cli.usuario_id,
        tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
        titulo="Actualización de emergencia",
        mensaje="Un taller no pudo aceptar tu solicitud. Revisa el estado de tu caso en la app.",
        evento_suffix=f"taller{taller_id}:rechazo",
    )


async def on_tecnico_asignado(db: AsyncSession, *, solicitud: SolicitudEmergencia) -> None:
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
    if cli is not None:
        await _emit(
            db,
            solicitud=solicitud,
            usuario_destino_id=cli.usuario_id,
            tipo=TipoNotificacionEnum.TECNICO_ASIGNADO,
            titulo="Técnico asignado",
            mensaje="Se asignó un técnico a tu emergencia. Sigue el avance en la app.",
            evento_suffix="cliente:tecnico_asignado",
        )

    tec = await tenant_guard.validar_tecnico_solicitud(db, solicitud=solicitud)
    if tec is not None:
        await _emit(
            db,
            solicitud=solicitud,
            usuario_destino_id=tec.usuario_id,
            tipo=TipoNotificacionEnum.TECNICO_ASIGNADO,
            titulo="Nueva asignación",
            mensaje=f"Te asignaron la emergencia #{solicitud.id}. Abre la app para ver detalles.",
            evento_suffix=f"tecnico{tec.id}:asignado",
        )

    if solicitud.taller_id is not None:
        uid = await _usuario_responsable_taller(db, solicitud.taller_id)
        if uid is not None:
            await _emit(
                db,
                solicitud=solicitud,
                usuario_destino_id=uid,
                tipo=TipoNotificacionEnum.TECNICO_ASIGNADO,
                titulo="Técnico asignado al servicio",
                mensaje=f"Se asignó un técnico a la emergencia #{solicitud.id}.",
                evento_suffix=f"taller{solicitud.taller_id}:tecnico_asignado",
            )


async def on_estado_servicio(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    mensaje_cliente: str,
    etiqueta_corta: str,
) -> None:
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
    if cli is not None:
        await _emit(
            db,
            solicitud=solicitud,
            usuario_destino_id=cli.usuario_id,
            tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
            titulo="Estado de tu servicio",
            mensaje=mensaje_cliente,
            evento_suffix=f"cliente:estado:{solicitud.estado.value}",
        )

    tec = await tenant_guard.validar_tecnico_solicitud(db, solicitud=solicitud)
    if tec is not None:
        await _emit(
            db,
            solicitud=solicitud,
            usuario_destino_id=tec.usuario_id,
            tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
            titulo="Cambio de estado",
            mensaje=f"La emergencia #{solicitud.id}: {etiqueta_corta}.",
            evento_suffix=f"tecnico{tec.id}:estado:{solicitud.estado.value}",
        )

    if solicitud.taller_id is not None:
        uid = await _usuario_responsable_taller(db, solicitud.taller_id)
        if uid is not None:
            await _emit(
                db,
                solicitud=solicitud,
                usuario_destino_id=uid,
                tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
                titulo="Actualización de servicio",
                mensaje=f"Emergencia #{solicitud.id}: {etiqueta_corta}.",
                evento_suffix=f"taller{solicitud.taller_id}:estado:{solicitud.estado.value}",
            )
