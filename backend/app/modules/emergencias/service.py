# Lógica de negocio — emergencias fase 1
from __future__ import annotations

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.bitacora.models import AccionBitacoraEnum
from app.modules.bitacora.service import registrar_accion
from app.modules.emergencias import repository
from app.modules.ai.services.post_create import enrich_solicitud_ai_after_create
from app.modules.emergencias.models import EstadoSolicitudSeguimientoEnum, SolicitudEmergencia
from app.modules.portal_taller_emergencias.repository import (
    insert_bandeja_pendiente_por_cada_taller,
)
from app.modules.emergencias.schemas import (
    EvidenciaCreateIn,
    SolicitudEmergenciaCreateIn,
    SolicitudEmergenciaDetailRead,
    SolicitudEmergenciaRead,
    SolicitudEmergenciaUpdateTextoIn,
    SolicitudEvidenciaRead,
    SolicitudHistorialEstadoRead,
    SolicitudSeguimientoRead,
    SolicitudUbicacionRead,
    TallerSeguimientoRead,
    TecnicoSeguimientoRead,
    UbicacionCreateIn,
    UbicacionTecnicoCompartidaRead,
)
from app.modules.usuarios.models import Usuario


def _to_detail(s: SolicitudEmergencia) -> SolicitudEmergenciaDetailRead:
    base = SolicitudEmergenciaRead.model_validate(s)
    ubs = sorted(s.ubicaciones, key=lambda x: x.registrado_at, reverse=True)
    evs = sorted(s.evidencias, key=lambda x: x.created_at, reverse=True)
    return SolicitudEmergenciaDetailRead(
        **base.model_dump(),
        ubicaciones=[SolicitudUbicacionRead.model_validate(x) for x in ubs],
        evidencias=[SolicitudEvidenciaRead.model_validate(x) for x in evs],
    )


def _require_registrada(s: SolicitudEmergencia) -> None:
    if s.estado != EstadoSolicitudSeguimientoEnum.REGISTRADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La solicitud está en estado {s.estado.value} y no admite esta operación.",
        )


async def crear_solicitud(
    user: Usuario,
    cliente_id: int,
    body: SolicitudEmergenciaCreateIn,
    db: AsyncSession,
) -> SolicitudEmergenciaDetailRead:
    v = await repository.get_vehiculo_if_cliente(db, vehiculo_id=body.vehiculo_id, cliente_id=cliente_id)
    if v is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece a tu cuenta.",
        )

    now = utc_now_naive()
    desc: str | None
    if body.descripcion_texto is None:
        desc = None
    else:
        st = body.descripcion_texto.strip()
        desc = st if st else None

    sol = await repository.insert_solicitud(
        db,
        cliente_id=cliente_id,
        vehiculo_id=body.vehiculo_id,
        descripcion_texto=desc,
        estado=EstadoSolicitudSeguimientoEnum.REGISTRADA,
        created_at=now,
        updated_at=now,
    )
    await repository.insert_historial_estado(
        db,
        solicitud_id=sol.id,
        estado_anterior=None,
        estado_nuevo=sol.estado,
        usuario_id=user.id,
        observacion="Alta solicitud (CU11)",
        created_at=now,
    )

    if body.ubicacion_inicial is not None:
        await _add_ubicacion_internal(db, sol, body.ubicacion_inicial, now)

    await insert_bandeja_pendiente_por_cada_taller(
        db, solicitud_id=sol.id, creado_at=now
    )

    await registrar_accion(
        db,
        "emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.CREAR,
        descripcion=f"Solicitud emergencia vehículo_id={body.vehiculo_id}",
        usuario_id=user.id,
        entidad_id=sol.id,
    )

    await enrich_solicitud_ai_after_create(db, solicitud_id=sol.id, cliente_id=cliente_id)

    s2 = await repository.get_solicitud_for_cliente(
        db, solicitud_id=sol.id, cliente_id=cliente_id, with_children=True
    )
    assert s2 is not None
    return _to_detail(s2)


async def listar_solicitudes(
    cliente_id: int,
    db: AsyncSession,
    *,
    limit: int = 100,
) -> list[SolicitudEmergenciaRead]:
    rows = await repository.list_solicitudes_cliente(db, cliente_id=cliente_id, limit=limit)
    return [SolicitudEmergenciaRead.model_validate(r) for r in rows]


async def obtener_detalle(
    cliente_id: int,
    solicitud_id: int,
    db: AsyncSession,
) -> SolicitudEmergenciaDetailRead:
    s = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
    )
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return _to_detail(s)


def _to_seguimiento(s: SolicitudEmergencia) -> SolicitudSeguimientoRead:
    historial = sorted(s.historial_estados, key=lambda h: h.created_at)
    taller = TallerSeguimientoRead.model_validate(s.taller) if s.taller is not None else None
    tecnico: TecnicoSeguimientoRead | None = None
    if s.tecnico is not None and s.tecnico.usuario is not None:
        u = s.tecnico.usuario
        tecnico = TecnicoSeguimientoRead(
            id=s.tecnico.id,
            nombres=u.nombres,
            apellidos=u.apellidos,
            telefono=u.telefono,
        )
    return SolicitudSeguimientoRead(
        solicitud_id=s.id,
        estado=s.estado,
        updated_at=s.updated_at,
        ai_payload=s.ai_payload,
        tiempo_estimado_min=s.tiempo_estimado_min,
        finalizada_at=s.finalizada_at,
        taller=taller,
        tecnico=tecnico,
        historial_estados=[SolicitudHistorialEstadoRead.model_validate(h) for h in historial],
    )


async def obtener_seguimiento(
    cliente_id: int,
    solicitud_id: int,
    db: AsyncSession,
) -> SolicitudSeguimientoRead:
    """CU16–CU18: estado, historial, taller/técnico asignados y ETA (solo solicitudes propias)."""
    s = await repository.get_solicitud_seguimiento_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id
    )
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return _to_seguimiento(s)


async def actualizar_texto(
    user: Usuario,
    cliente_id: int,
    solicitud_id: int,
    body: SolicitudEmergenciaUpdateTextoIn,
    db: AsyncSession,
) -> SolicitudEmergenciaDetailRead:
    s = await repository.get_solicitud_for_cliente(db, solicitud_id=solicitud_id, cliente_id=cliente_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    _require_registrada(s)

    patch = body.model_dump(exclude_unset=True)
    if "descripcion_texto" not in patch:
        s2 = await repository.get_solicitud_for_cliente(
            db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
        )
        assert s2 is not None
        return _to_detail(s2)

    raw = patch["descripcion_texto"]
    if raw is None:
        s.descripcion_texto = None
    else:
        st = raw.strip()
        s.descripcion_texto = st if st else None
    s.updated_at = utc_now_naive()

    await registrar_accion(
        db,
        "emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion="Actualización texto adicional (CU15)",
        usuario_id=user.id,
        entidad_id=s.id,
    )

    s2 = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
    )
    assert s2 is not None
    return _to_detail(s2)


async def _add_ubicacion_internal(
    db: AsyncSession,
    sol: SolicitudEmergencia,
    body: UbicacionCreateIn,
    now,
) -> None:
    if body.es_actual:
        await repository.clear_ubicacion_actual_for_solicitud(db, sol.id)
    await repository.insert_ubicacion(
        db,
        solicitud_id=sol.id,
        latitud=body.latitud,
        longitud=body.longitud,
        precision_metros=body.precision_metros,
        direccion_referencia=body.direccion_referencia,
        es_actual=body.es_actual,
        registrado_at=now,
    )
    sol.updated_at = now


async def agregar_ubicacion(
    user: Usuario,
    cliente_id: int,
    solicitud_id: int,
    body: UbicacionCreateIn,
    db: AsyncSession,
) -> SolicitudEmergenciaDetailRead:
    s = await repository.get_solicitud_for_cliente(db, solicitud_id=solicitud_id, cliente_id=cliente_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    _require_registrada(s)

    now = utc_now_naive()
    await _add_ubicacion_internal(db, s, body, now)

    await registrar_accion(
        db,
        "emergencias",
        "solicitud_ubicaciones",
        AccionBitacoraEnum.CREAR,
        descripcion="Ubicación enviada (CU12)",
        usuario_id=user.id,
        entidad_id=solicitud_id,
    )

    s2 = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
    )
    assert s2 is not None
    return _to_detail(s2)


async def agregar_evidencia(
    user: Usuario,
    cliente_id: int,
    solicitud_id: int,
    body: EvidenciaCreateIn,
    db: AsyncSession,
) -> SolicitudEmergenciaDetailRead:
    s = await repository.get_solicitud_for_cliente(db, solicitud_id=solicitud_id, cliente_id=cliente_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    _require_registrada(s)

    now = utc_now_naive()
    await repository.insert_evidencia(
        db,
        solicitud_id=s.id,
        tipo=body.tipo,
        archivo_url=body.archivo_url.strip(),
        mime_type=body.mime_type,
        nombre_archivo=body.nombre_archivo,
        tamano_bytes=body.tamano_bytes,
        created_at=now,
    )
    s.updated_at = now

    await registrar_accion(
        db,
        "emergencias",
        "solicitud_evidencias",
        AccionBitacoraEnum.CREAR,
        descripcion=f"Evidencia tipo={body.tipo.value} (CU13/CU14)",
        usuario_id=user.id,
        entidad_id=solicitud_id,
    )

    s2 = await repository.get_solicitud_for_cliente(
        db, solicitud_id=solicitud_id, cliente_id=cliente_id, with_children=True
    )
    assert s2 is not None
    return _to_detail(s2)


async def obtener_ubicacion_tecnico_compartida_cliente(
    cliente_id: int,
    solicitud_id: int,
    db: AsyncSession,
) -> UbicacionTecnicoCompartidaRead:
    s = await repository.get_solicitud_for_cliente(db, solicitud_id=solicitud_id, cliente_id=cliente_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    if s.tecnico_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aún no hay técnico asignado a esta solicitud.",
        )
    if s.tecnico_ult_ubicacion_at is None or s.tecnico_ult_latitud is None or s.tecnico_ult_longitud is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El técnico aún no ha compartido su ubicación.",
        )
    return UbicacionTecnicoCompartidaRead(
        solicitud_id=s.id,
        latitud=s.tecnico_ult_latitud,
        longitud=s.tecnico_ult_longitud,
        precision_metros=s.tecnico_ult_precision_metros,
        actualizado_at=s.tecnico_ult_ubicacion_at,
    )
