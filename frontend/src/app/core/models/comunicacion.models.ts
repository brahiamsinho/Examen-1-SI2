export type TipoNotificacion =
  | 'SOLICITUD_CREADA'
  | 'ESTADO_ACTUALIZADO'
  | 'TALLER_ASIGNADO'
  | 'TECNICO_ASIGNADO'
  | 'MENSAJE_NUEVO'
  | 'SOLICITUD_PENDIENTE_TALLER';

export interface NotificacionDto {
  id: number;
  usuario_id: number;
  solicitud_id: number | null;
  tipo: TipoNotificacion;
  titulo: string;
  mensaje: string;
  leida: boolean;
  created_at: string;
  leida_at: string | null;
}
