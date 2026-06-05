export type EstadoTaller = 'PENDIENTE' | 'ACTIVO' | 'SUSPENDIDO' | 'INACTIVO';
export type EstadoTecnico = 'ACTIVO' | 'INACTIVO';

export interface RegistroTallerPayload {
  nombre_comercial: string;
  email: string;
  telefono: string;
  direccion: string;
  ciudad: string;
  descripcion?: string | null;
  responsable_nombre_completo: string;
  password: string;
}

export interface MiTallerDto {
  id: number;
  nombre_comercial: string;
  telefono_contacto: string;
  email_contacto: string;
  direccion: string;
  ciudad: string;
  descripcion: string | null;
  estado: EstadoTaller;
  created_at: string | null;
  responsable_nombres: string;
  responsable_apellidos: string;
  responsable_email: string;
  responsable_telefono: string;
  pendiente_verificacion_email?: boolean;
}

export interface MiTallerUpdatePayload {
  nombre_comercial?: string;
  telefono_contacto?: string;
  email_contacto?: string;
  direccion?: string;
  ciudad?: string;
  descripcion?: string | null;
  usuario?: {
    nombres?: string;
    apellidos?: string;
    telefono?: string;
  };
}

export interface TallerDashboardDto {
  tecnicos_registrados: number;
  tecnicos_activos: number;
  disponibilidad_general: string;
  taller_estado: EstadoTaller;
  usuarios_activos: number;
  clientes_registrados: number;
}

export interface EspecialidadDto {
  id: number;
  nombre: string;
  descripcion: string | null;
}

export interface TecnicoPortalDto {
  id: number;
  usuario_id: number;
  taller_id: number;
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  documento: string | null;
  especialidad_id: number | null;
  especialidad_nombre: string | null;
  disponibilidad: string | null;
  estado: EstadoTecnico;
  created_at: string | null;
  resumen_actividad: string | null;
}

export interface TecnicoPortalCreatePayload {
  nombre_completo: string;
  email: string;
  telefono: string;
  password: string;
  documento?: string | null;
  especialidad_id?: number | null;
  disponibilidad?: string | null;
  estado?: EstadoTecnico;
}

export interface TecnicoPortalUpdatePayload {
  nombre_completo?: string;
  email?: string;
  telefono?: string;
  documento?: string | null;
  especialidad_id?: number | null;
  disponibilidad?: string | null;
  estado?: EstadoTecnico;
}

export interface TallerPlanOptionDto {
  slug: string;
  name: string;
  description?: string | null;
  price_monthly_bob: number;
  currency: string;
  benefits: string[];
  featured: boolean;
  badge?: string | null;
  sort_order: number;
  is_current: boolean;
  can_upgrade: boolean;
  stripe_checkout_available: boolean;
}

export interface TallerSuscripcionDto {
  tenant_nombre: string;
  tenant_slug: string;
  current_plan_slug: string;
  current_plan_name: string;
  subscription_status: string;
  subscription_ends_at?: string | null;
  stripe_enabled: boolean;
  plans: TallerPlanOptionDto[];
}

export interface TallerSuscripcionCheckoutPayload {
  plan_slug: string;
  success_url: string;
  cancel_url: string;
}

export interface TallerSuscripcionCheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface TallerSuscripcionConfirmPayload {
  session_id: string;
}

export type TallerAccionBitacora =
  | 'CREAR'
  | 'ACTUALIZAR'
  | 'ELIMINAR'
  | 'INICIAR_SESION'
  | 'CERRAR_SESION'
  | 'RESTABLECER_CONTRASENA'
  | 'ASIGNAR_ROL'
  | 'ASIGNAR_PERMISO'
  | 'CONSULTAR';

export interface TallerBitacoraDto {
  id: number;
  usuario_id: number | null;
  usuario_nombre: string | null;
  modulo: string;
  entidad: string;
  entidad_id: number | null;
  accion: TallerAccionBitacora;
  descripcion: string | null;
  created_at: string;
}

export interface TallerBitacoraListParams {
  usuario_id?: number;
  modulo?: string;
  accion?: TallerAccionBitacora;
  desde?: string;
  hasta?: string;
  limit?: number;
  offset?: number;
}

export type TallerBackupEstado =
  | 'PENDIENTE'
  | 'EN_PROGRESO'
  | 'COMPLETADO'
  | 'FALLIDO'
  | 'RESTAURADO'
  | 'EXPIRADO';

export interface TallerBackupDto {
  id: number;
  tenant_id: number | null;
  taller_id: number | null;
  tipo: string;
  archivo: string;
  tamano_mb: number | null;
  estado: TallerBackupEstado;
  incluye_evidencias: boolean;
  creado_en: string;
  expira_en: string | null;
  error_mensaje: string | null;
  restaurado_en: string | null;
  motivo_restore: string | null;
}

export interface TallerBackupConfigDto {
  id: number;
  taller_id: number;
  backup_automatico: boolean;
  hora_backup: string;
  frecuencia: 'daily' | 'weekly';
  retencion_dias: number;
  ultimo_backup_auto: string | null;
  actualizado_en: string;
}

export interface TallerBackupConfigUpdatePayload {
  backup_automatico?: boolean;
  hora_backup?: string;
  frecuencia?: 'daily' | 'weekly';
  retencion_dias?: number;
}

export interface TallerBackupRestorePayload {
  confirmar: boolean;
  motivo: string;
}
