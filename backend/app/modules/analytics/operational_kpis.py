# KPIs operacionales §3 — consultas agregadas sobre solicitudes reales.
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.ai.schemas import IncidentCategory
from app.modules.analytics.schemas import (
    IncidentePorTipoFila,
    OperationalKpisRead,
    SlaCumplimientoRead,
    TallerEficienciaFila,
    ZonaIncidentesFila,
)
from app.modules.incidentes.emergencias.models import (
    EstadoSolicitudSeguimientoEnum,
    SolicitudEmergencia,
    SolicitudHistorialEstado,
    SolicitudUbicacion,
)
from app.modules.talleres_y_tecnicos.talleres.models import Taller

_CATEGORY_LABELS: dict[str, str] = {
    IncidentCategory.BATERIA.value: "Batería",
    IncidentCategory.LLANTA.value: "Llanta",
    IncidentCategory.MOTOR.value: "Motor",
    IncidentCategory.CHOQUE.value: "Choque",
    IncidentCategory.OTROS.value: "Otros",
}

_ASSIGN_STATES = (
    EstadoSolicitudSeguimientoEnum.EN_REVISION,
    EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
)
_ARRIVAL_STATES = (
    EstadoSolicitudSeguimientoEnum.EN_CAMINO,
    EstadoSolicitudSeguimientoEnum.EN_ATENCION,
)


def _round_minutes(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def _solicitud_filters(
    *,
    tenant_id: int | None,
    taller_id: int | None,
    desde: datetime | None,
    hasta: datetime | None,
) -> list[Any]:
    clauses: list[Any] = []
    if tenant_id is not None:
        clauses.append(SolicitudEmergencia.tenant_id == tenant_id)
    if taller_id is not None:
        clauses.append(SolicitudEmergencia.taller_id == taller_id)
    if desde is not None:
        clauses.append(SolicitudEmergencia.created_at >= desde)
    if hasta is not None:
        clauses.append(SolicitudEmergencia.created_at <= hasta)
    return clauses


def _categoria_sql_expr():
    """Extrae categoría de incidente desde ai_payload JSONB."""
    return func.upper(
        func.coalesce(
            SolicitudEmergencia.ai_payload["clasificacion"]["categoria"].astext,
            SolicitudEmergencia.ai_payload["resumen_estructurado"]["ficha"]["tipo_problema"].astext,
            IncidentCategory.OTROS.value,
        )
    )


async def _avg_minutes_assignment(
    db: AsyncSession, filters: list[Any]
) -> float | None:
    first_assign = (
        select(
            SolicitudHistorialEstado.solicitud_id.label("sid"),
            func.min(SolicitudHistorialEstado.created_at).label("asignado_at"),
        )
        .where(SolicitudHistorialEstado.estado_nuevo.in_(_ASSIGN_STATES))
        .group_by(SolicitudHistorialEstado.solicitud_id)
        .subquery()
    )
    stmt = (
        select(
            func.avg(
                func.extract(
                    "epoch",
                    first_assign.c.asignado_at - SolicitudEmergencia.created_at,
                )
                / 60.0
            )
        )
        .select_from(SolicitudEmergencia)
        .join(first_assign, first_assign.c.sid == SolicitudEmergencia.id)
    )
    if filters:
        stmt = stmt.where(*filters)
    row = await db.execute(stmt)
    return _round_minutes(row.scalar_one())


async def _avg_minutes_arrival(db: AsyncSession, filters: list[Any]) -> float | None:
    first_arrival = (
        select(
            SolicitudHistorialEstado.solicitud_id.label("sid"),
            func.min(SolicitudHistorialEstado.created_at).label("llegada_at"),
        )
        .where(SolicitudHistorialEstado.estado_nuevo.in_(_ARRIVAL_STATES))
        .group_by(SolicitudHistorialEstado.solicitud_id)
        .subquery()
    )
    stmt = (
        select(
            func.avg(
                func.extract(
                    "epoch",
                    first_arrival.c.llegada_at - SolicitudEmergencia.tecnico_asignado_at,
                )
                / 60.0
            )
        )
        .select_from(SolicitudEmergencia)
        .join(first_arrival, first_arrival.c.sid == SolicitudEmergencia.id)
        .where(SolicitudEmergencia.tecnico_asignado_at.isnot(None))
    )
    if filters:
        stmt = stmt.where(*filters)
    row = await db.execute(stmt)
    return _round_minutes(row.scalar_one())


async def _incidentes_por_tipo(
    db: AsyncSession, filters: list[Any]
) -> list[IncidentePorTipoFila]:
    cat_expr = _categoria_sql_expr()
    stmt = select(cat_expr.label("categoria"), func.count().label("n")).select_from(
        SolicitudEmergencia
    )
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.group_by(cat_expr).order_by(func.count().desc())
    rows = (await db.execute(stmt)).all()
    result: list[IncidentePorTipoFila] = []
    for cat, n in rows:
        key = str(cat or IncidentCategory.OTROS.value).upper()
        if key not in _CATEGORY_LABELS:
            key = IncidentCategory.OTROS.value
        result.append(
            IncidentePorTipoFila(
                categoria=key,
                label=_CATEGORY_LABELS.get(key, key.title()),
                total=int(n),
            )
        )
    return result


async def _talleres_eficientes(
    db: AsyncSession,
    filters: list[Any],
    *,
    limit: int = 10,
) -> list[TallerEficienciaFila]:
    fin_filters = [
        *filters,
        SolicitudEmergencia.estado == EstadoSolicitudSeguimientoEnum.FINALIZADA,
        SolicitudEmergencia.finalizada_at.isnot(None),
        SolicitudEmergencia.taller_id.isnot(None),
    ]

    first_assign = (
        select(
            SolicitudHistorialEstado.solicitud_id.label("sid"),
            func.min(SolicitudHistorialEstado.created_at).label("asignado_at"),
        )
        .where(SolicitudHistorialEstado.estado_nuevo.in_(_ASSIGN_STATES))
        .group_by(SolicitudHistorialEstado.solicitud_id)
        .subquery()
    )

    resp_min = func.avg(
        func.extract(
            "epoch",
            first_assign.c.asignado_at - SolicitudEmergencia.created_at,
        )
        / 60.0
    )
    fin_min = func.avg(
        func.extract(
            "epoch",
            SolicitudEmergencia.finalizada_at - SolicitudEmergencia.created_at,
        )
        / 60.0
    )

    stmt = (
        select(
            Taller.id,
            Taller.nombre_comercial,
            func.count(SolicitudEmergencia.id).label("n_fin"),
            resp_min.label("resp_min"),
            fin_min.label("fin_min"),
        )
        .select_from(SolicitudEmergencia)
        .join(Taller, Taller.id == SolicitudEmergencia.taller_id)
        .outerjoin(first_assign, first_assign.c.sid == SolicitudEmergencia.id)
        .where(*fin_filters)
        .group_by(Taller.id, Taller.nombre_comercial)
        .having(func.count(SolicitudEmergencia.id) > 0)
        .order_by(fin_min.asc().nullslast(), resp_min.asc().nullslast())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [
        TallerEficienciaFila(
            taller_id=int(rid),
            nombre_comercial=str(nombre),
            solicitudes_finalizadas=int(n_fin),
            tiempo_respuesta_prom_min=_round_minutes(resp),
            tiempo_finalizacion_prom_min=_round_minutes(fin),
        )
        for rid, nombre, n_fin, resp, fin in rows
    ]


async def _zonas_incidentes(
    db: AsyncSession, filters: list[Any], *, limit: int = 8
) -> list[ZonaIncidentesFila]:
    grid_lat = func.round(SolicitudUbicacion.latitud, 2)
    grid_lng = func.round(SolicitudUbicacion.longitud, 2)
    stmt = (
        select(
            grid_lat.label("glat"),
            grid_lng.label("glng"),
            func.count().label("n"),
            func.avg(SolicitudUbicacion.latitud).label("lat_avg"),
            func.avg(SolicitudUbicacion.longitud).label("lng_avg"),
        )
        .select_from(SolicitudEmergencia)
        .join(
            SolicitudUbicacion,
            and_(
                SolicitudUbicacion.solicitud_id == SolicitudEmergencia.id,
                SolicitudUbicacion.es_actual.is_(True),
            ),
        )
    )
    if filters:
        stmt = stmt.where(*filters)
    stmt = (
        stmt.group_by(grid_lat, grid_lng)
        .order_by(func.count().desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    out: list[ZonaIncidentesFila] = []
    for glat, glng, n, lat_avg, lng_avg in rows:
        zona = f"Zona {float(glat):.2f}, {float(glng):.2f}"
        out.append(
            ZonaIncidentesFila(
                zona=zona,
                total=int(n),
                latitud_prom=_round_minutes(lat_avg),
                longitud_prom=_round_minutes(lng_avg),
            )
        )
    return out


async def _casos_cancelados_no_atendidos(
    db: AsyncSession, filters: list[Any]
) -> tuple[int, int]:
    canceladas_stmt = select(func.count()).select_from(SolicitudEmergencia).where(
        SolicitudEmergencia.estado == EstadoSolicitudSeguimientoEnum.CANCELADA,
        *filters,
    )
    canceladas = int((await db.execute(canceladas_stmt)).scalar_one() or 0)

    no_atendidas_stmt = select(func.count()).select_from(SolicitudEmergencia).where(
        SolicitudEmergencia.estado == EstadoSolicitudSeguimientoEnum.REGISTRADA,
        *filters,
    )
    no_atendidas = int((await db.execute(no_atendidas_stmt)).scalar_one() or 0)
    return canceladas, no_atendidas


async def _sla_cumplimiento(db: AsyncSession, filters: list[Any]) -> SlaCumplimientoRead:
    umbral = settings.SLA_ATENCION_MINUTOS
    sla_filters = [
        *filters,
        SolicitudEmergencia.estado == EstadoSolicitudSeguimientoEnum.FINALIZADA,
        SolicitudEmergencia.finalizada_at.isnot(None),
    ]
    minutes_expr = func.extract(
        "epoch",
        SolicitudEmergencia.finalizada_at - SolicitudEmergencia.created_at,
    ) / 60.0
    stmt = select(
        func.count().label("total"),
        func.sum(case((minutes_expr <= umbral, 1), else_=0)).label("dentro"),
    ).select_from(SolicitudEmergencia).where(*sla_filters)
    row = (await db.execute(stmt)).one()
    total = int(row.total or 0)
    dentro = int(row.dentro or 0)
    pct = round(dentro / total * 100.0, 1) if total > 0 else None
    return SlaCumplimientoRead(
        umbral_minutos=umbral,
        servicios_evaluados=total,
        servicios_dentro_sla=dentro,
        porcentaje_cumplimiento=pct,
    )


async def compute_operational_kpis(
    db: AsyncSession,
    *,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    tenant_id: int | None = None,
    taller_id: int | None = None,
) -> OperationalKpisRead:
    """Calcula los 7 KPIs operacionales del enunciado desde BD real."""
    filters = _solicitud_filters(
        tenant_id=tenant_id, taller_id=taller_id, desde=desde, hasta=hasta
    )

    canceladas, no_atendidas = await _casos_cancelados_no_atendidos(db, filters)

    return OperationalKpisRead(
        tiempo_promedio_asignacion_min=await _avg_minutes_assignment(db, filters),
        tiempo_promedio_llegada_min=await _avg_minutes_arrival(db, filters),
        incidentes_por_tipo=await _incidentes_por_tipo(db, filters),
        talleres_mas_eficientes=await _talleres_eficientes(
            db, filters, limit=1 if taller_id is not None else 10
        ),
        zonas_mas_incidentes=await _zonas_incidentes(db, filters),
        casos_cancelados=canceladas,
        casos_no_atendidos=no_atendidas,
        sla=await _sla_cumplimiento(db, filters),
    )
