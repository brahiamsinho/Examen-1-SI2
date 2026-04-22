# Lógica de negocio — bandeja y disponibilidad taller (ciclo 3 fase 1)
from __future__ import annotations

from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.bitacora.models import AccionBitacoraEnum
from app.modules.bitacora.service import registrar_accion
from app.modules.emergencias import repository as emergencias_repository
from app.modules.emergencias.models import EstadoSolicitudSeguimientoEnum, SolicitudEmergencia
from app.modules.portal_taller_emergencias import repository
from app.modules.portal_taller_emergencias.models import (
    EstadoAsignacionTecnicoEnum,
    EstadoBandejaTallerEnum,
    SolicitudAsignacionTecnico,
    TallerDisponibilidad,
)
from app.modules.portal_taller_emergencias.schemas import (
    AsignacionTecnicoRead,
    AsignarTecnicoIn,
    AsignarTecnicoOut,
    BandejaIncidenteBaseRead,
    ComisionTallerRead,
    HistorialAtencionRead,
    RechazarBandejaIn,
    ResumenComisionesRead,
    SolicitudBandejaDetalleRead,
    TallerDisponibilidadRead,
    TallerDisponibilidadUpdateIn,
)
from app.modules.talleres.models import Tecnico
from app.modules.usuarios.models import Usuario


_BASE_KEYS = frozenset(BandejaIncidenteBaseRead.model_fields.keys())


def _row_to_list_item(row: dict) -> BandejaIncidenteBaseRead:
    slim = {k: row[k] for k in _BASE_KEYS if k in row}
    return BandejaIncidenteBaseRead.model_validate(slim)


def _row_to_detalle(row: dict) -> SolicitudBandejaDetalleRead:
    slim = {k: row[k] for k in _BASE_KEYS if k in row}
    return SolicitudBandejaDetalleRead(
        **slim,
        estado_bandeja=row["estado_bandeja"],
        motivo_rechazo=row.get("motivo_rechazo"),
        creado_at=row["bandeja_creado_at"],
        respondido_at=row.get("respondido_at"),
    )


async def _ensure_disponibilidad(db: AsyncSession, taller_id: int) -> TallerDisponibilidad:
    row = await repository.get_disponibilidad(db, taller_id=taller_id)
    if row is not None:
        return row
    now = utc_now_naive()
    return await repository.insert_disponibilidad_default(db, taller_id=taller_id, updated_at=now)


async def listar_disponibles(taller_id: int, db: AsyncSession) -> list[BandejaIncidenteBaseRead]:
    rows = await repository.list_bandeja_pendiente_por_taller(db, taller_id=taller_id)
    return [_row_to_list_item(r) for r in rows]


async def obtener_detalle_bandeja(
    taller_id: int, bandeja_id: int, db: AsyncSession
) -> SolicitudBandejaDetalleRead:
    row = await repository.get_bandeja_detalle_por_taller(db, bandeja_id=bandeja_id, taller_id=taller_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada de bandeja no encontrada")
    return _row_to_detalle(row)


async def obtener_disponibilidad(taller_id: int, db: AsyncSession) -> TallerDisponibilidadRead:
    row = await _ensure_disponibilidad(db, taller_id)
    return TallerDisponibilidadRead(
        taller_id=row.taller_id,
        acepta_nuevas_solicitudes=row.acepta_nuevas_solicitudes,
        capacidad_maxima_diaria=row.capacidad_maxima_diaria,
        servicios_activos=row.servicios_activos,
        observacion=row.observacion,
        updated_at=row.updated_at,
        updated_by_usuario_id=row.updated_by_usuario_id,
    )


async def actualizar_disponibilidad(
    user: Usuario, taller_id: int, body: TallerDisponibilidadUpdateIn, db: AsyncSession
) -> TallerDisponibilidadRead:
    row = await _ensure_disponibilidad(db, taller_id)
    now = utc_now_naive()
    patch = body.model_dump(exclude_unset=True)
    await repository.update_disponibilidad(
        db,
        row=row,
        acepta_nuevas_solicitudes=patch.get("acepta_nuevas_solicitudes"),
        capacidad_maxima_diaria=patch.get("capacidad_maxima_diaria"),
        observacion=patch.get("observacion"),
        updated_by_usuario_id=user.id,
        updated_at=now,
    )
    await registrar_accion(
        db,
        "portal_taller_emergencias",
        "taller_disponibilidad",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"taller_id={taller_id}",
        usuario_id=user.id,
        entidad_id=row.id,
    )
    return await obtener_disponibilidad(taller_id, db)


async def rechazar_solicitud(
    user: Usuario,
    taller_id: int,
    bandeja_id: int,
    body: RechazarBandejaIn,
    db: AsyncSession,
) -> SolicitudBandejaDetalleRead:
    st = body.motivo_rechazo.strip()
    now = utc_now_naive()
    affected = await repository.marcar_bandeja(
        db,
        bandeja_id=bandeja_id,
        taller_id=taller_id,
        estado=EstadoBandejaTallerEnum.RECHAZADA,
        respondido_at=now,
        motivo_rechazo=st,
    )
    if affected == 0:
        b = await repository.get_bandeja_row(db, bandeja_id=bandeja_id, taller_id=taller_id)
        if b is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada de bandeja no encontrada")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no está pendiente de respuesta.",
        )
    await registrar_accion(
        db,
        "portal_taller_emergencias",
        "solicitud_taller_bandeja",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Rechazo bandeja_id={bandeja_id} taller_id={taller_id}",
        usuario_id=user.id,
        entidad_id=bandeja_id,
    )
    return await obtener_detalle_bandeja(taller_id, bandeja_id, db)


def _estado_terminal_solicitud(estado: EstadoSolicitudSeguimientoEnum) -> bool:
    return estado in (
        EstadoSolicitudSeguimientoEnum.FINALIZADA,
        EstadoSolicitudSeguimientoEnum.CANCELADA,
    )


_ESTADOS_PERMITE_ASIGNAR_TECNICO = frozenset(
    (
        EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
        EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
    )
)


def _tecnico_disponible_para_asignar(t: Tecnico) -> bool:
    if t.disponibilidad is None:
        return True
    d = t.disponibilidad.strip().lower()
    if d in ("no", "no_disponible", "ausente", "ocupado"):
        return False
    return True


def _to_asignacion_read(row: SolicitudAsignacionTecnico) -> AsignacionTecnicoRead:
    return AsignacionTecnicoRead.model_validate(row)


def _to_asignar_out(se: SolicitudEmergencia, asignacion: SolicitudAsignacionTecnico) -> AsignarTecnicoOut:
    return AsignarTecnicoOut(
        solicitud_id=se.id,
        estado_solicitud=se.estado,
        tecnico_id=se.tecnico_id,
        tecnico_asignado_at=se.tecnico_asignado_at,
        asignacion=_to_asignacion_read(asignacion),
    )


async def listar_asignaciones_tecnico(
    taller_id: int, solicitud_id: int, db: AsyncSession
) -> list[AsignacionTecnicoRead]:
    se = await _get_solicitud_taller_o_none(db, solicitud_id=solicitud_id, taller_id=taller_id)
    if se is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    rows = await repository.list_asignaciones_tecnico_por_solicitud_taller(
        db, solicitud_id=solicitud_id, taller_id=taller_id
    )
    return [_to_asignacion_read(r) for r in rows]


async def _get_solicitud_taller_o_none(
    db: AsyncSession, *, solicitud_id: int, taller_id: int
) -> SolicitudEmergencia | None:
    res = await db.execute(
        select(SolicitudEmergencia).where(
            SolicitudEmergencia.id == solicitud_id,
            SolicitudEmergencia.taller_id == taller_id,
        )
    )
    return res.scalar_one_or_none()


async def asignar_tecnico_a_solicitud(
    user: Usuario,
    taller_id: int,
    solicitud_id: int,
    body: AsignarTecnicoIn,
    db: AsyncSession,
) -> AsignarTecnicoOut:
    now = utc_now_naive()
    obs: str | None = None
    if body.observacion is not None:
        st_obs = body.observacion.strip()
        obs = st_obs if st_obs else None

    res_se = await db.execute(
        select(SolicitudEmergencia)
        .where(SolicitudEmergencia.id == solicitud_id)
        .with_for_update()
    )
    se = res_se.scalar_one_or_none()
    if se is None or se.taller_id != taller_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    if _estado_terminal_solicitud(se.estado):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no admite asignación de técnico.",
        )
    if se.estado not in _ESTADOS_PERMITE_ASIGNAR_TECNICO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud no admite asignación de técnico en su estado actual.",
        )

    tecnico = await repository.get_tecnico_del_taller_activo(
        db, tecnico_id=body.tecnico_id, taller_id=taller_id
    )
    if tecnico is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Técnico no encontrado, inactivo o no pertenece a este taller.",
        )
    if not _tecnico_disponible_para_asignar(tecnico):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El técnico no está disponible para asignación.",
        )

    if se.tecnico_id == body.tecnico_id and se.estado == EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO:
        existente = await repository.find_asignacion_activa_mismo_tecnico(
            db, solicitud_id=solicitud_id, taller_id=taller_id, tecnico_id=body.tecnico_id
        )
        if existente is not None:
            return _to_asignar_out(se, existente)

    if se.tecnico_id is not None and se.tecnico_id != body.tecnico_id:
        await repository.marcar_asignaciones_activas_como_reasignado(
            db, solicitud_id=solicitud_id, taller_id=taller_id
        )

    estado_antes = se.estado
    tecnico_previo = se.tecnico_id
    se.tecnico_id = body.tecnico_id
    se.tecnico_asignado_at = now
    se.updated_at = now

    if estado_antes == EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO:
        se.estado = EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO
        msg_hist = (
            "Asignación técnico (CU28)"
            if tecnico_previo is None
            else "Cambio de técnico (CU28) — solicitud en TALLER_ASIGNADO"
        )
        await emergencias_repository.insert_historial_estado(
            db,
            solicitud_id=se.id,
            estado_anterior=estado_antes,
            estado_nuevo=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
            usuario_id=user.id,
            observacion=msg_hist,
            created_at=now,
        )
    elif estado_antes == EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO:
        await emergencias_repository.insert_historial_estado(
            db,
            solicitud_id=se.id,
            estado_anterior=estado_antes,
            estado_nuevo=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
            usuario_id=user.id,
            observacion="Reasignación técnico (CU28)",
            created_at=now,
        )

    asignacion = await repository.insert_asignacion_tecnico(
        db,
        solicitud_id=solicitud_id,
        taller_id=taller_id,
        tecnico_id=body.tecnico_id,
        estado=EstadoAsignacionTecnicoEnum.ASIGNADO,
        asignado_por_usuario_id=user.id,
        observacion=obs,
        created_at=now,
    )

    await registrar_accion(
        db,
        "portal_taller_emergencias",
        "solicitud_asignaciones_tecnico",
        AccionBitacoraEnum.CREAR,
        descripcion=f"solicitud_id={solicitud_id} tecnico_id={body.tecnico_id}",
        usuario_id=user.id,
        entidad_id=asignacion.id,
    )

    return _to_asignar_out(se, asignacion)


async def aceptar_solicitud(
    user: Usuario,
    taller_id: int,
    bandeja_id: int,
    db: AsyncSession,
) -> SolicitudBandejaDetalleRead:
    now = utc_now_naive()
    bandeja = await repository.get_bandeja_row(db, bandeja_id=bandeja_id, taller_id=taller_id)
    if bandeja is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada de bandeja no encontrada")

    if bandeja.estado == EstadoBandejaTallerEnum.ACEPTADA:
        return await obtener_detalle_bandeja(taller_id, bandeja_id, db)
    if bandeja.estado != EstadoBandejaTallerEnum.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no está pendiente de respuesta.",
        )

    res_se = await db.execute(
        select(SolicitudEmergencia)
        .where(SolicitudEmergencia.id == bandeja.solicitud_id)
        .with_for_update()
    )
    se = res_se.scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    if _estado_terminal_solicitud(se.estado):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no admite asignación de taller.",
        )
    if se.taller_id is not None and se.taller_id != taller_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya fue asignada a otro taller.",
        )

    disp = await _ensure_disponibilidad(db, taller_id)
    if not disp.acepta_nuevas_solicitudes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El taller no acepta nuevas solicitudes en este momento.",
        )
    if disp.servicios_activos >= disp.capacidad_maxima_diaria:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capacidad máxima alcanzada; no se pueden aceptar más servicios.",
        )

    affected = await repository.marcar_bandeja(
        db,
        bandeja_id=bandeja_id,
        taller_id=taller_id,
        estado=EstadoBandejaTallerEnum.ACEPTADA,
        respondido_at=now,
    )
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya no está pendiente de respuesta.",
        )

    await repository.expirar_otras_bandeja_pendientes(
        db,
        solicitud_id=bandeja.solicitud_id,
        bandeja_ganadora_id=bandeja_id,
        respondido_at=now,
    )

    estado_anterior = se.estado
    se.taller_id = taller_id
    if estado_anterior in (
        EstadoSolicitudSeguimientoEnum.REGISTRADA,
        EstadoSolicitudSeguimientoEnum.EN_REVISION,
    ):
        se.estado = EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO
        await emergencias_repository.insert_historial_estado(
            db,
            solicitud_id=se.id,
            estado_anterior=estado_anterior,
            estado_nuevo=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
            usuario_id=user.id,
            observacion="Taller acepta asistencia (CU26)",
            created_at=now,
        )
    se.updated_at = now

    disp.servicios_activos = int(disp.servicios_activos) + 1
    disp.updated_by_usuario_id = user.id
    disp.updated_at = now

    await registrar_accion(
        db,
        "portal_taller_emergencias",
        "solicitud_taller_bandeja",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Aceptación bandeja_id={bandeja_id} solicitud_id={bandeja.solicitud_id}",
        usuario_id=user.id,
        entidad_id=bandeja_id,
    )

    return await obtener_detalle_bandeja(taller_id, bandeja_id, db)


async def listar_historial_atenciones(
    taller_id: int,
    db: AsyncSession,
    *,
    estado: EstadoSolicitudSeguimientoEnum | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    limit: int = 200,
) -> list[HistorialAtencionRead]:
    """CU30 — solo solicitudes del taller (taller_id explícito en consulta)."""
    lim = max(1, min(limit, 500))
    desde_dt = datetime.combine(desde, time.min) if desde is not None else None
    hasta_dt = datetime.combine(hasta, time(23, 59, 59)) if hasta is not None else None
    rows = await repository.list_historial_atenciones_taller(
        db,
        taller_id=taller_id,
        estado=estado,
        desde=desde_dt,
        hasta=hasta_dt,
        limit=lim,
    )
    return [HistorialAtencionRead.model_validate(r) for r in rows]


async def listar_comisiones_taller(taller_id: int, db: AsyncSession) -> list[ComisionTallerRead]:
    """CU31 — detalle con join opcional a pagos."""
    rows = await repository.list_comisiones_taller_con_pago(db, taller_id=taller_id)
    return [ComisionTallerRead.model_validate(r) for r in rows]


async def obtener_resumen_comisiones(taller_id: int, db: AsyncSession) -> ResumenComisionesRead:
    """CU31 — totales por taller."""
    row = await repository.resumen_comisiones_taller(db, taller_id=taller_id)
    return ResumenComisionesRead.model_validate(row)
