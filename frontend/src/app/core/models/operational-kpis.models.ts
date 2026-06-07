/** KPIs operacionales §3 — Analítica desde datos reales (compartido admin/taller). */

export interface IncidentePorTipoDto {
  categoria: string;
  label: string;
  total: number;
}

export interface TallerEficienciaDto {
  taller_id: number;
  nombre_comercial: string;
  solicitudes_finalizadas: number;
  tiempo_respuesta_prom_min: number | null;
  tiempo_finalizacion_prom_min: number | null;
}

export interface ZonaIncidentesDto {
  zona: string;
  total: number;
  latitud_prom: number | null;
  longitud_prom: number | null;
}

export interface SlaCumplimientoDto {
  umbral_minutos: number;
  servicios_evaluados: number;
  servicios_dentro_sla: number;
  porcentaje_cumplimiento: number | null;
}

export interface OperationalKpisDto {
  tiempo_promedio_asignacion_min: number | null;
  tiempo_promedio_llegada_min: number | null;
  incidentes_por_tipo: IncidentePorTipoDto[];
  talleres_mas_eficientes: TallerEficienciaDto[];
  zonas_mas_incidentes: ZonaIncidentesDto[];
  casos_cancelados: number;
  casos_no_atendidos: number;
  sla: SlaCumplimientoDto;
}
