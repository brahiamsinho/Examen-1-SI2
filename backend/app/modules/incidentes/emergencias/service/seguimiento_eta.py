# CU44 — Consultar tiempo estimado de reparación/atención (cliente).
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidentes.emergencias import repository
from app.modules.incidentes.emergencias.models import EstadoSolicitudSeguimientoEnum
from app.modules.incidentes.emergencias.schemas import EtaDisponibilidadEnum, SolicitudEtaRead


def _mensaje_contextual(estado: EstadoSolicitudSeguimientoEnum, minutos: int) -> str:
    if estado == EstadoSolicitudSeguimientoEnum.EN_CAMINO:
        return f"El técnico llegará en aproximadamente {minutos} min."
    if estado == EstadoSolicitudSeguimientoEnum.EN_ATENCION:
        return f"Tiempo estimado de reparación/atención: {minutos} min."
    if estado in (
        EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
        EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
    ):
        return f"Tiempo estimado informado por el taller: {minutos} min."
    return f"Tiempo estimado de atención: {minutos} min."


def _build_eta_read(s) -> SolicitudEtaRead:
    """Construye respuesta CU44 a partir de la solicitud cargada."""
    estados_cerrados = {
        EstadoSolicitudSeguimientoEnum.FINALIZADA,
        EstadoSolicitudSeguimientoEnum.CANCELADA,
    }
    tiene_eta = s.tiempo_estimado_min is not None and s.tiempo_estimado_min >= 0

    if s.estado in estados_cerrados:
        if tiene_eta:
            return SolicitudEtaRead(
                solicitud_id=s.id,
                estado=s.estado,
                tiempo_estimado_min=s.tiempo_estimado_min,
                disponibilidad=EtaDisponibilidadEnum.HISTORICO,
                eta_aplicable=False,
                mensaje=(
                    f"Servicio {s.estado.value.lower()}. "
                    f"Última estimación registrada: {s.tiempo_estimado_min} min."
                ),
                actualizado_at=s.updated_at,
                taller_id=s.taller_id,
                tecnico_id=s.tecnico_id,
            )
        return SolicitudEtaRead(
            solicitud_id=s.id,
            estado=s.estado,
            tiempo_estimado_min=None,
            disponibilidad=EtaDisponibilidadEnum.NO_APLICABLE,
            eta_aplicable=False,
            mensaje="El servicio finalizó o fue cancelado; no hay ETA activa.",
            actualizado_at=s.updated_at,
            taller_id=s.taller_id,
            tecnico_id=s.tecnico_id,
        )

    if s.taller_id is None:
        return SolicitudEtaRead(
            solicitud_id=s.id,
            estado=s.estado,
            tiempo_estimado_min=None,
            disponibilidad=EtaDisponibilidadEnum.NO_APLICABLE,
            eta_aplicable=False,
            mensaje="Seleccioná un taller para que puedan estimar tiempos de atención.",
            actualizado_at=s.updated_at,
            taller_id=None,
            tecnico_id=s.tecnico_id,
        )

    if not tiene_eta:
        return SolicitudEtaRead(
            solicitud_id=s.id,
            estado=s.estado,
            tiempo_estimado_min=None,
            disponibilidad=EtaDisponibilidadEnum.PENDIENTE,
            eta_aplicable=True,
            mensaje="Estimación pendiente. El taller o técnico la publicará cuando avance la atención.",
            actualizado_at=s.updated_at,
            taller_id=s.taller_id,
            tecnico_id=s.tecnico_id,
        )

    return SolicitudEtaRead(
        solicitud_id=s.id,
        estado=s.estado,
        tiempo_estimado_min=s.tiempo_estimado_min,
        disponibilidad=EtaDisponibilidadEnum.DISPONIBLE,
        eta_aplicable=True,
        mensaje=_mensaje_contextual(s.estado, s.tiempo_estimado_min),
        actualizado_at=s.updated_at,
        taller_id=s.taller_id,
        tecnico_id=s.tecnico_id,
    )


async def obtener_eta_cliente(
    cliente_id: int,
    solicitud_id: int,
    db: AsyncSession,
) -> SolicitudEtaRead:
    s = await repository.get_solicitud_seguimiento_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id
    )
    if s is not None:
        return _build_eta_read(s)

    owner = await repository.get_solicitud_cliente_id(db, solicitud_id=solicitud_id)
    if owner is not None and owner != cliente_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para consultar esta solicitud.",
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
