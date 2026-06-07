# CU46 — KPIs operativos y financieros del panel administrador.
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.admin_finanzas.service import get_finanzas_reportes, get_finanzas_resumen
from app.modules.incidentes.emergencias.models import EstadoSolicitudSeguimientoEnum, SolicitudEmergencia
from app.modules.pagos_y_comisiones.pagos.models import EstadoPagoEnum, Pago


def _avg_minutes_attention(row_value: Any) -> float | None:
    if row_value is None:
        return None
    try:
        return round(float(row_value), 1)
    except (TypeError, ValueError):
        return None


async def get_panel_kpis(
    db: AsyncSession,
    *,
    desde: datetime | None,
    hasta: datetime | None,
    tenant_id: int | None = None,
) -> dict[str, Any]:
    """Agrega métricas de solicitudes, pagos y finanzas para CU46."""
    s_filters = []
    if tenant_id is not None:
        s_filters.append(SolicitudEmergencia.tenant_id == tenant_id)
    if desde:
        s_filters.append(SolicitudEmergencia.created_at >= desde)
    if hasta:
        s_filters.append(SolicitudEmergencia.created_at <= hasta)

    base_q = select(SolicitudEmergencia)
    if s_filters:
        base_q = base_q.where(*s_filters)

    total_row = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total_solicitudes = int(total_row.scalar_one() or 0)

    estado_rows = await db.execute(
        select(SolicitudEmergencia.estado, func.count()).where(*s_filters).group_by(
            SolicitudEmergencia.estado
        )
        if s_filters
        else select(SolicitudEmergencia.estado, func.count()).group_by(SolicitudEmergencia.estado)
    )
    solicitudes_por_estado = {e.value: int(n) for e, n in estado_rows.all()}

    activas = sum(
        n
        for est, n in solicitudes_por_estado.items()
        if est not in (
            EstadoSolicitudSeguimientoEnum.FINALIZADA.value,
            EstadoSolicitudSeguimientoEnum.CANCELADA.value,
        )
    )
    finalizadas = solicitudes_por_estado.get(EstadoSolicitudSeguimientoEnum.FINALIZADA.value, 0)
    canceladas = solicitudes_por_estado.get(EstadoSolicitudSeguimientoEnum.CANCELADA.value, 0)

    p_filters = [Pago.estado == EstadoPagoEnum.PAGADO]
    if tenant_id is not None:
        p_filters.append(SolicitudEmergencia.tenant_id == tenant_id)
    if desde:
        p_filters.append(Pago.pagado_at >= desde)
    if hasta:
        p_filters.append(Pago.pagado_at <= hasta)

    pagos_row = (
        await db.execute(
            select(
                func.count(Pago.id).label("n"),
                func.coalesce(func.sum(Pago.monto), 0).label("monto"),
            )
            .join(SolicitudEmergencia, SolicitudEmergencia.id == Pago.solicitud_id)
            .where(*p_filters)
        )
    ).mappings().one()

    att_filters = [
        SolicitudEmergencia.estado == EstadoSolicitudSeguimientoEnum.FINALIZADA,
        SolicitudEmergencia.finalizada_at.isnot(None),
    ]
    if tenant_id is not None:
        att_filters.append(SolicitudEmergencia.tenant_id == tenant_id)
    if desde:
        att_filters.append(SolicitudEmergencia.finalizada_at >= desde)
    if hasta:
        att_filters.append(SolicitudEmergencia.finalizada_at <= hasta)

    avg_att = await db.execute(
        select(
            func.avg(
                func.extract(
                    "epoch",
                    SolicitudEmergencia.finalizada_at - SolicitudEmergencia.created_at,
                )
                / 60.0
            )
        ).where(*att_filters)
    )
    tiempo_promedio = _avg_minutes_attention(avg_att.scalar_one())

    fin_resumen = await get_finanzas_resumen(db, desde=desde, hasta=hasta, tenant_id=tenant_id)
    fin_reportes = await get_finanzas_reportes(db, desde=desde, hasta=hasta, tenant_id=tenant_id)

    sin_datos = total_solicitudes == 0 and int(pagos_row["n"] or 0) == 0

    return {
        "periodo_desde": desde,
        "periodo_hasta": hasta,
        "tenant_id": tenant_id,
        "total_solicitudes": total_solicitudes,
        "solicitudes_activas": activas,
        "solicitudes_finalizadas": finalizadas,
        "solicitudes_canceladas": canceladas,
        "solicitudes_por_estado": solicitudes_por_estado,
        "pagos_confirmados": int(pagos_row["n"] or 0),
        "monto_pagos_bob": Decimal(str(pagos_row["monto"] or 0)),
        "tiempo_promedio_atencion_min": tiempo_promedio,
        "sin_datos_en_periodo": sin_datos,
        "resumen_financiero": fin_resumen,
        "top_talleres": fin_reportes.get("top_talleres", []),
        "serie_diaria": fin_reportes.get("serie_diaria", []),
    }
