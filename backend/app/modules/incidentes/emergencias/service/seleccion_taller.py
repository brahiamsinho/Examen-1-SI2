# CU37 — candidatos rankeados y selección de taller por el cliente.
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.ai import repository as ai_repository
from app.modules.ai.schemas import AssignmentRankIn, AssignmentRankOut, IncidentCategory, PriorityLevel
from app.modules.ai.services.assignment_scorer import rank_talleres
from app.modules.atencion.taller_emergencias.models import EstadoBandejaTallerEnum
from app.modules.atencion.taller_emergencias.repository import (
    ensure_bandeja_pendiente_para_taller,
    expirar_todas_bandeja_pendientes,
    get_bandeja_por_solicitud_taller,
)
from app.modules.incidentes.emergencias import repository
from app.modules.incidentes.emergencias.models import EstadoSolicitudSeguimientoEnum
from app.modules.incidentes.emergencias.schemas import SeleccionarTallerOut
from app.modules.talleres_y_tecnicos.talleres.models import EstadoTallerEnum, Taller


def _ubicacion_actual(solicitud) -> object | None:
    if not solicitud.ubicaciones:
        return None
    actuales = [u for u in solicitud.ubicaciones if u.es_actual]
    return actuales[0] if actuales else max(solicitud.ubicaciones, key=lambda x: x.registrado_at)


def _categoria_y_prioridad(ai_payload: dict | None) -> tuple[IncidentCategory, PriorityLevel]:
    categoria = IncidentCategory.OTROS
    prioridad = PriorityLevel.MEDIA
    if not ai_payload:
        return categoria, prioridad
    cls = ai_payload.get("clasificacion") or {}
    pri = ai_payload.get("prioridad") or {}
    try:
        if cls.get("categoria"):
            categoria = IncidentCategory(str(cls["categoria"]))
    except ValueError:
        pass
    try:
        if pri.get("nivel_prioridad"):
            prioridad = PriorityLevel(str(pri["nivel_prioridad"]))
    except ValueError:
        pass
    return categoria, prioridad


async def listar_talleres_candidatos(
    cliente_id: int,
    solicitud_id: int,
    db: AsyncSession,
) -> AssignmentRankOut:
    s = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
    )
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    ubic = _ubicacion_actual(s)
    if ubic is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Registrá al menos una ubicación antes de elegir taller.",
        )

    categoria, prioridad = _categoria_y_prioridad(s.ai_payload)
    taller_rows = await ai_repository.list_talleres_for_assignment(db, tenant_id=s.tenant_id)
    if not taller_rows:
        return AssignmentRankOut(candidatos=[], mejor_taller_id=None)

    return rank_talleres(
        AssignmentRankIn(
            incident_lat=ubic.latitud,
            incident_lng=ubic.longitud,
            categoria=categoria,
            nivel_prioridad=prioridad,
            ciudad_incidente=(ubic.direccion_referencia or None),
        ),
        taller_rows,
    )


async def seleccionar_taller(
    user: Usuario,
    cliente_id: int,
    solicitud_id: int,
    taller_id: int,
    db: AsyncSession,
) -> SeleccionarTallerOut:
    s = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=False
    )
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    if s.taller_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya tiene un taller asignado.",
        )
    if s.estado not in (
        EstadoSolicitudSeguimientoEnum.REGISTRADA,
        EstadoSolicitudSeguimientoEnum.EN_REVISION,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no admite selección de taller.",
        )

    res_t = await db.execute(select(Taller).where(Taller.id == taller_id))
    taller = res_t.scalar_one_or_none()
    if taller is None or taller.estado != EstadoTallerEnum.ACTIVO:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taller no disponible")
    if s.tenant_id is not None and taller.tenant_id != s.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El taller no pertenece a tu organización.",
        )

    existing = await get_bandeja_por_solicitud_taller(
        db, solicitud_id=solicitud_id, taller_id=taller_id
    )
    if existing is not None and existing.estado == EstadoBandejaTallerEnum.ACEPTADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El taller ya aceptó esta solicitud.",
        )

    now = utc_now_naive()
    bandeja = await ensure_bandeja_pendiente_para_taller(
        db, solicitud_id=solicitud_id, taller_id=taller_id, creado_at=now
    )
    await expirar_todas_bandeja_pendientes(
        db,
        solicitud_id=solicitud_id,
        respondido_at=now,
        excepto_bandeja_id=bandeja.id,
    )

    estado_anterior = s.estado
    if estado_anterior == EstadoSolicitudSeguimientoEnum.REGISTRADA:
        s.estado = EstadoSolicitudSeguimientoEnum.EN_REVISION
        await repository.insert_historial_estado(
            db,
            solicitud_id=s.id,
            estado_anterior=estado_anterior,
            estado_nuevo=EstadoSolicitudSeguimientoEnum.EN_REVISION,
            usuario_id=user.id,
            observacion="Cliente eligió taller",
            created_at=now,
        )
    s.updated_at = now

    await registrar_accion(
        db,
        "emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"CU37 cliente seleccionó taller_id={taller_id} solicitud_id={solicitud_id}",
        usuario_id=user.id,
        entidad_id=solicitud_id,
    )

    return SeleccionarTallerOut(
        solicitud_id=solicitud_id,
        taller_id=taller_id,
        bandeja_id=bandeja.id,
        estado=s.estado,
    )
