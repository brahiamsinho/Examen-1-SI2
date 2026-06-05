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


async def _nombre_cliente(db: AsyncSession, solicitud: SolicitudEmergencia) -> str:
    from app.modules.acceso_y_administracion.usuarios.models import Usuario
    from app.modules.clientes_y_vehiculos.clientes.models import Cliente

    res = await db.execute(
        select(Usuario.nombres, Usuario.apellidos)
        .join(Cliente, Cliente.usuario_id == Usuario.id)
        .where(Cliente.id == solicitud.cliente_id)
    )
    row = res.one_or_none()
    if row is None:
        return "Un cliente"
    return f"{row[0]} {row[1]}".strip()


async def on_solicitud_pendiente_taller(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    taller_id: int,
) -> None:
    uid = await _usuario_responsable_taller(db, taller_id)
    if uid is None:
        return
    nombre = await _nombre_cliente(db, solicitud)
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=uid,
        tipo=TipoNotificacionEnum.SOLICITUD_PENDIENTE_TALLER,
        titulo="Cliente eligió tu taller",
        mensaje=f"{nombre} seleccionó tu taller para la emergencia #{solicitud.id}. Revisá la bandeja.",
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


async def on_mensaje_cliente(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    mensaje_id: int,
    texto_preview: str,
) -> None:
    """Cliente escribió en el chat: avisa al responsable del taller asignado."""
    if solicitud.taller_id is None:
        return
    uid = await _usuario_responsable_taller(db, solicitud.taller_id)
    if uid is None:
        return
    nombre = await _nombre_cliente(db, solicitud)
    preview = texto_preview[:120] + ("…" if len(texto_preview) > 120 else "")
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=uid,
        tipo=TipoNotificacionEnum.MENSAJE_NUEVO,
        titulo=f"Mensaje de {nombre}",
        mensaje=f"Emergencia #{solicitud.id}: {preview}",
        evento_suffix=f"taller{solicitud.taller_id}:msg:{mensaje_id}",
    )


async def on_pago_cliente(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    pago_id: int,
    monto_label: str | None = None,
) -> None:
    """Cliente confirmó un pago vinculado a la solicitud."""
    if solicitud.taller_id is None:
        return
    uid = await _usuario_responsable_taller(db, solicitud.taller_id)
    if uid is None:
        return
    nombre = await _nombre_cliente(db, solicitud)
    extra = f" Monto: {monto_label}." if monto_label else ""
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=uid,
        tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
        titulo="Pago confirmado por cliente",
        mensaje=f"{nombre} confirmó el pago de la emergencia #{solicitud.id}.{extra}",
        evento_suffix=f"taller{solicitud.taller_id}:pago:{pago_id}",
    )


async def on_presupuesto_registrado(
    db: AsyncSession,
    *,
    solicitud: SolicitudEmergencia,
    monto_label: str,
    detalle: str | None = None,
) -> None:
    """Taller registró cotización: avisa al cliente (CU42 → CU41 opcional)."""
    cli = await tenant_guard.validar_cliente_solicitud(db, solicitud=solicitud)
    if cli is None:
        return
    preview = ""
    if detalle:
        preview = detalle[:160] + ("…" if len(detalle) > 160 else "")
    mensaje = f"Tu taller registró una cotización de {monto_label} para la emergencia #{solicitud.id}."
    if preview:
        mensaje = f"{mensaje} Detalle: {preview}"
    await _emit(
        db,
        solicitud=solicitud,
        usuario_destino_id=cli.usuario_id,
        tipo=TipoNotificacionEnum.ESTADO_ACTUALIZADO,
        titulo="Cotización del servicio",
        mensaje=mensaje,
        evento_suffix="cliente:presupuesto_registrado",
    )
