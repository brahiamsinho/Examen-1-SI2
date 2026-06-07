# Cancelación de solicitud por el cliente + eventos WS/notificaciones.
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.atencion.taller_emergencias import repository as taller_repository
from app.modules.atencion.taller_emergencias.service import helpers as taller_helpers
from app.modules.comunicacion_y_notificaciones.notificaciones import eventos_servicio
from app.modules.comunicacion_y_notificaciones.tiempo_real.publish import queue_solicitud_event
from app.modules.comunicacion_y_notificaciones.tiempo_real.schemas import RealtimeEventType
from app.modules.incidentes.emergencias import repository
from app.modules.incidentes.emergencias.models import (
    EstadoSolicitudSeguimientoEnum,
    SolicitudEmergencia,
)
from app.modules.incidentes.emergencias.schemas import CancelarSolicitudIn, SolicitudSeguimientoRead

from . import helpers


async def cancelar_solicitud(
    user: Usuario,
    cliente_id: int,
    solicitud_id: int,
    body: CancelarSolicitudIn,
    db: AsyncSession,
) -> SolicitudSeguimientoRead:
    res = await db.execute(
        select(SolicitudEmergencia)
        .where(
            SolicitudEmergencia.id == solicitud_id,
            SolicitudEmergencia.cliente_id == cliente_id,
        )
        .with_for_update()
    )
    se = res.scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    helpers.require_cancelable_cliente(se)

    now = utc_now_naive()
    estado_anterior = se.estado
    obs = body.motivo or "Cancelada por el cliente"
    se.estado = EstadoSolicitudSeguimientoEnum.CANCELADA
    se.updated_at = now

    await repository.insert_historial_estado(
        db,
        solicitud_id=se.id,
        estado_anterior=estado_anterior,
        estado_nuevo=se.estado,
        usuario_id=user.id,
        observacion=obs,
        created_at=now,
    )

    await taller_repository.cerrar_bandejas_por_cancelacion_cliente(
        db, solicitud_id=se.id, respondido_at=now
    )

    if estado_anterior in helpers.ESTADOS_LIBERAN_CUPO_TALLER and se.taller_id is not None:
        disp = await taller_helpers.ensure_disponibilidad(db, se.taller_id)
        if int(disp.servicios_activos) > 0:
            disp.servicios_activos = int(disp.servicios_activos) - 1
            disp.updated_at = now

    await registrar_accion(
        db,
        "emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Cancelación cliente solicitud_id={se.id}",
        usuario_id=user.id,
        entidad_id=se.id,
    )

    await eventos_servicio.on_cliente_cancelo(db, solicitud=se, motivo=obs)

    queue_solicitud_event(
        db,
        solicitud_id=se.id,
        tipo=RealtimeEventType.ESTADO_INCIDENTE,
        payload={
            "estado_anterior": estado_anterior.value,
            "estado_nuevo": se.estado.value,
            "motivo": "cliente_cancelo",
            "taller_id": se.taller_id,
        },
        occurred_at=now,
    )
    queue_solicitud_event(
        db,
        solicitud_id=se.id,
        tipo=RealtimeEventType.BANDEJA_ACTUALIZADA,
        payload={"motivo": "cliente_cancelo", "estado_bandeja": "EXPIRADA"},
        occurred_at=now,
    )
    queue_solicitud_event(
        db,
        solicitud_id=se.id,
        tipo=RealtimeEventType.SEGUIMIENTO_ACTUALIZADO,
        payload={"motivo": "cliente_cancelo"},
        occurred_at=now,
    )

    s2 = await repository.get_solicitud_seguimiento_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id
    )
    assert s2 is not None
    return helpers.to_seguimiento(s2)
