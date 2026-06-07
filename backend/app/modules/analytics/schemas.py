from __future__ import annotations

from pydantic import BaseModel, Field


class IncidentePorTipoFila(BaseModel):
    categoria: str
    label: str
    total: int


class TallerEficienciaFila(BaseModel):
    taller_id: int
    nombre_comercial: str
    solicitudes_finalizadas: int
    tiempo_respuesta_prom_min: float | None = Field(
        None, description="Promedio minutos desde reporte hasta taller asignado."
    )
    tiempo_finalizacion_prom_min: float | None = Field(
        None, description="Promedio minutos desde reporte hasta finalización."
    )


class ZonaIncidentesFila(BaseModel):
    zona: str
    total: int
    latitud_prom: float | None = None
    longitud_prom: float | None = None


class SlaCumplimientoRead(BaseModel):
    umbral_minutos: int
    servicios_evaluados: int
    servicios_dentro_sla: int
    porcentaje_cumplimiento: float | None = None


class OperationalKpisRead(BaseModel):
    """KPIs operacionales del enunciado §3 — Analítica operacional."""

    tiempo_promedio_asignacion_min: float | None = None
    tiempo_promedio_llegada_min: float | None = None
    incidentes_por_tipo: list[IncidentePorTipoFila] = Field(default_factory=list)
    talleres_mas_eficientes: list[TallerEficienciaFila] = Field(default_factory=list)
    zonas_mas_incidentes: list[ZonaIncidentesFila] = Field(default_factory=list)
    casos_cancelados: int = 0
    casos_no_atendidos: int = 0
    sla: SlaCumplimientoRead
