# CU42 — Registrar cotización del servicio (panel taller).
from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.incidentes.emergencias import repository as emergencias_repository
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.comunicacion_y_notificaciones.notificaciones import eventos_servicio
from app.modules.atencion.taller_emergencias.schemas import PresupuestoSolicitudRead, RegistrarPresupuestoIn
from app.modules.acceso_y_administracion.usuarios.models import Usuario

from . import helpers


def _to_read(se: SolicitudEmergencia, *, observaciones: str | None = None) -> PresupuestoSolicitudRead:
    if se.presupuesto_bob is None or se.presupuesto_registrado_at is None or not se.presupuesto_detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La solicitud aún no tiene cotización registrada.",
        )
    return PresupuestoSolicitudRead(
        solicitud_id=se.id,
        estado_solicitud=se.estado,
        presupuesto_bob=se.presupuesto_bob,
        presupuesto_detalle=se.presupuesto_detalle,
        presupuesto_registrado_at=se.presupuesto_registrado_at,
        observaciones_registro=observaciones,
    )


async def obtener_presupuesto_solicitud(
    taller_id: int, solicitud_id: int, db: AsyncSession
) -> PresupuestoSolicitudRead:
    res = await db.execute(
        select(SolicitudEmergencia).where(
            SolicitudEmergencia.id == solicitud_id,
            SolicitudEmergencia.taller_id == taller_id,
        )
    )
    se = res.scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return _to_read(se)


async def registrar_presupuesto_solicitud(
    user: Usuario,
    taller_id: int,
    solicitud_id: int,
    body: RegistrarPresupuestoIn,
    db: AsyncSession,
) -> PresupuestoSolicitudRead:
    now = utc_now_naive()

    res = await db.execute(
        select(SolicitudEmergencia)
        .where(SolicitudEmergencia.id == solicitud_id)
        .with_for_update()
    )
    se = res.scalar_one_or_none()
    if se is None or se.taller_id != taller_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    if helpers.estado_terminal_solicitud(se.estado):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya está cerrada y no admite cotización.",
        )
    if se.estado not in helpers.ESTADOS_PERMITE_COTIZACION:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud no admite cotización en su estado actual.",
        )
    if se.presupuesto_bob is not None and se.presupuesto_registrado_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe una cotización registrada para esta solicitud. "
                "No se puede reemplazar desde el panel del taller."
            ),
        )

    monto = body.presupuesto_bob
    se.presupuesto_bob = monto
    se.presupuesto_detalle = body.detalle
    se.presupuesto_registrado_at = now
    se.updated_at = now

    obs_historial = f"Cotización registrada: {monto} BOB. {body.detalle[:500]}"
    if body.observaciones:
        obs_historial = f"{obs_historial} Obs.: {body.observaciones[:500]}"

    await emergencias_repository.insert_historial_estado(
        db,
        solicitud_id=se.id,
        estado_anterior=se.estado,
        estado_nuevo=se.estado,
        usuario_id=user.id,
        observacion=obs_historial,
        created_at=now,
    )

    await registrar_accion(
        db,
        "taller_emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"solicitud_id={solicitud_id} presupuesto_bob={monto}",
        usuario_id=user.id,
        entidad_id=solicitud_id,
    )

    monto_label = f"{monto.quantize(Decimal('0.01'))} BOB"
    await eventos_servicio.on_presupuesto_registrado(
        db,
        solicitud=se,
        monto_label=monto_label,
        detalle=body.detalle,
    )

    return PresupuestoSolicitudRead(
        solicitud_id=se.id,
        estado_solicitud=se.estado,
        presupuesto_bob=monto,
        presupuesto_detalle=body.detalle,
        presupuesto_registrado_at=now,
        observaciones_registro=body.observaciones,
    )
