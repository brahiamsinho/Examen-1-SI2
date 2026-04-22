# Lógica — operación técnico en emergencias (CU32–CU35, script 008)
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.bitacora.models import AccionBitacoraEnum
from app.modules.bitacora.service import registrar_accion
from app.modules.comunicaciones import service as comunicaciones_service
from app.modules.comunicaciones.schemas import MensajeSolicitudCreateIn, MensajeSolicitudRead
from app.modules.emergencias import repository as emergencias_repository
from app.modules.emergencias.models import EstadoSolicitudSeguimientoEnum, SolicitudEmergencia
from app.modules.portal_tecnico.service import get_tecnico_row_for_usuario
from app.modules.portal_tecnico_emergencias import repository
from app.modules.portal_tecnico_emergencias.schemas import (
    ActualizarEstadoServicioIn,
    ServicioAsignadoRead,
    UbicacionClienteActualRead,
)
from app.modules.usuarios.models import Usuario

_ALLOWED_TRANSITIONS: dict[
    EstadoSolicitudSeguimientoEnum, frozenset[EstadoSolicitudSeguimientoEnum]
] = {
    EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO: frozenset({EstadoSolicitudSeguimientoEnum.EN_CAMINO}),
    EstadoSolicitudSeguimientoEnum.EN_CAMINO: frozenset({EstadoSolicitudSeguimientoEnum.EN_ATENCION}),
    EstadoSolicitudSeguimientoEnum.EN_ATENCION: frozenset({EstadoSolicitudSeguimientoEnum.FINALIZADA}),
}


def _estado_terminal(estado: EstadoSolicitudSeguimientoEnum) -> bool:
    return estado in (
        EstadoSolicitudSeguimientoEnum.FINALIZADA,
        EstadoSolicitudSeguimientoEnum.CANCELADA,
    )


async def listar_servicios_asignados(user: Usuario, db: AsyncSession) -> list[ServicioAsignadoRead]:
    t = await get_tecnico_row_for_usuario(user.id, db)
    rows = await repository.list_servicios_asignados_a_tecnico(db, tecnico_id=t.id)
    return [ServicioAsignadoRead.model_validate(r) for r in rows]


async def obtener_ubicacion_cliente(
    user: Usuario, solicitud_id: int, db: AsyncSession
) -> UbicacionClienteActualRead:
    t = await get_tecnico_row_for_usuario(user.id, db)
    row = await repository.get_ubicacion_actual_para_solicitud_tecnico(
        db, solicitud_id=solicitud_id, tecnico_id=t.id
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ubicación no disponible o solicitud no asignada a tu cuenta.",
        )
    return UbicacionClienteActualRead.model_validate(row)


async def actualizar_estado_servicio(
    user: Usuario, solicitud_id: int, body: ActualizarEstadoServicioIn, db: AsyncSession
) -> ServicioAsignadoRead:
    t = await get_tecnico_row_for_usuario(user.id, db)
    now = utc_now_naive()
    obs = body.observacion.strip() if body.observacion else None
    obs = obs if obs else None

    res = await db.execute(
        select(SolicitudEmergencia)
        .where(SolicitudEmergencia.id == solicitud_id)
        .with_for_update()
    )
    se = res.scalar_one_or_none()
    if se is None or se.tecnico_id != t.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada.",
        )
    if _estado_terminal(se.estado):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya está cerrada.",
        )

    permitidos = _ALLOWED_TRANSITIONS.get(se.estado, frozenset())
    if body.nuevo_estado not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede pasar de {se.estado.value} a {body.nuevo_estado.value}.",
        )

    estado_anterior = se.estado
    se.estado = body.nuevo_estado
    se.updated_at = now
    if body.nuevo_estado == EstadoSolicitudSeguimientoEnum.FINALIZADA:
        se.finalizada_at = now

    await emergencias_repository.insert_historial_estado(
        db,
        solicitud_id=se.id,
        estado_anterior=estado_anterior,
        estado_nuevo=body.nuevo_estado,
        usuario_id=user.id,
        observacion=obs or f"Actualización estado técnico (CU34): {body.nuevo_estado.value}",
        created_at=now,
    )

    await registrar_accion(
        db,
        "portal_tecnico_emergencias",
        "solicitudes_emergencia",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"solicitud_id={solicitud_id} estado={body.nuevo_estado.value}",
        usuario_id=user.id,
        entidad_id=solicitud_id,
    )

    row = await repository.get_servicio_asignado_detalle(db, solicitud_id=solicitud_id, tecnico_id=t.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")
    return ServicioAsignadoRead.model_validate(row)


async def listar_mensajes_solicitud(
    user: Usuario, solicitud_id: int, db: AsyncSession
) -> list[MensajeSolicitudRead]:
    return await comunicaciones_service.listar_mensajes(user, solicitud_id, db, actor="tecnico")


async def enviar_mensaje_solicitud(
    user: Usuario, solicitud_id: int, body: MensajeSolicitudCreateIn, db: AsyncSession
) -> MensajeSolicitudRead:
    return await comunicaciones_service.enviar_mensaje(user, solicitud_id, body, db, actor="tecnico")
