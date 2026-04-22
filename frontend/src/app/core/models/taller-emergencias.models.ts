/** Contratos alineados a `portal_taller_emergencias` (FastAPI). */

export type EstadoSolicitudSeguimiento =
  | 'REGISTRADA'
  | 'EN_REVISION'
  | 'TALLER_ASIGNADO'
  | 'TECNICO_ASIGNADO'
  | 'EN_CAMINO'
  | 'EN_ATENCION'
  | 'FINALIZADA'
  | 'CANCELADA';

export type EstadoBandejaTaller = 'PENDIENTE' | 'ACEPTADA' | 'RECHAZADA' | 'EXPIRADA';

export interface BandejaIncidenteBaseDto {
  bandeja_id: number;
  taller_id: number;
  solicitud_id: number;
  estado_solicitud: EstadoSolicitudSeguimiento;
  descripcion_texto: string | null;
  created_at: string;
  vehiculo_id: number;
  placa: string;
  marca: string | null;
  modelo: string | null;
  tipo_vehiculo: string | null;
  cliente_id: number;
  nombres: string;
  apellidos: string;
  latitud: string | null;
  longitud: string | null;
  direccion_referencia: string | null;
}

export interface SolicitudBandejaDetalleDto extends BandejaIncidenteBaseDto {
  estado_bandeja: EstadoBandejaTaller;
  motivo_rechazo: string | null;
  creado_at: string;
  respondido_at: string | null;
}

export interface TallerDisponibilidadDto {
  taller_id: number;
  acepta_nuevas_solicitudes: boolean;
  capacidad_maxima_diaria: number;
  servicios_activos: number;
  observacion: string | null;
  updated_at: string;
  updated_by_usuario_id: number | null;
}

export interface TallerDisponibilidadUpdatePayload {
  acepta_nuevas_solicitudes?: boolean;
  capacidad_maxima_diaria?: number;
  observacion?: string | null;
}

export interface RechazarBandejaPayload {
  motivo_rechazo: string;
}

/** POST `/portal/taller/emergencias/solicitudes/{id}/asignar-tecnico` */
export interface AsignarTecnicoPayload {
  tecnico_id: number;
  observacion?: string | null;
}

export type EstadoAsignacionTecnico = 'ASIGNADO' | 'REASIGNADO' | 'CANCELADO';

export interface AsignacionTecnicoDto {
  id: number;
  solicitud_id: number;
  taller_id: number;
  tecnico_id: number;
  estado: EstadoAsignacionTecnico;
  asignado_por_usuario_id: number | null;
  observacion: string | null;
  created_at: string;
}

export interface AsignarTecnicoResultDto {
  solicitud_id: number;
  estado_solicitud: EstadoSolicitudSeguimiento;
  tecnico_id: number | null;
  tecnico_asignado_at: string | null;
  asignacion: AsignacionTecnicoDto;
}
