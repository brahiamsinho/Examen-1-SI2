from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.acceso_y_administracion.bitacora.schemas import BitacoraRead
from app.modules.acceso_y_administracion.admin_finanzas.schemas import (
    AdminComisionSerieFila,
    AdminFinanzasResumen,
    TallerComisionFila,
)
from app.modules.analytics.schemas import OperationalKpisRead


class AdminPanelOverview(BaseModel):
    total_usuarios: int
    total_talleres: int
    total_roles: int
    actividad_reciente: list[BitacoraRead]


class AdminKpisRead(BaseModel):
    """CU46 — dashboard KPIs administrador (operativo + financiero)."""

    periodo_desde: datetime | None = None
    periodo_hasta: datetime | None = None
    tenant_id: int | None = None
    total_solicitudes: int = 0
    solicitudes_activas: int = 0
    solicitudes_finalizadas: int = 0
    solicitudes_canceladas: int = 0
    solicitudes_por_estado: dict[str, int] = Field(default_factory=dict)
    pagos_confirmados: int = 0
    monto_pagos_bob: Decimal = Field(default=Decimal("0"))
    tiempo_promedio_atencion_min: float | None = None
    sin_datos_en_periodo: bool = False
    resumen_financiero: AdminFinanzasResumen
    top_talleres: list[TallerComisionFila] = Field(default_factory=list)
    serie_diaria: list[AdminComisionSerieFila] = Field(default_factory=list)
    analitica_operacional: OperationalKpisRead
