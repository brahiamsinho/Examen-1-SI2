import type { OperationalKpisDto } from './operational-kpis.models';

export type EstadoUsuario = 'ACTIVO' | 'INACTIVO' | 'BLOQUEADO' | 'PENDIENTE';
export type EstadoTaller = 'PENDIENTE' | 'ACTIVO' | 'SUSPENDIDO' | 'INACTIVO';
export type AccionBitacora =
  | 'CREAR'
  | 'ACTUALIZAR'
  | 'ELIMINAR'
  | 'INICIAR_SESION'
  | 'CERRAR_SESION'
  | 'RESTABLECER_CONTRASENA'
  | 'ASIGNAR_ROL'
  | 'ASIGNAR_PERMISO'
  | 'CONSULTAR';

export interface RolDto {
  id: number;
  nombre: string;
  descripcion: string | null;
  created_at: string | null;
}

export interface RolPermisosDto {
  rol_id: number;
  permiso_ids: number[];
}

export interface PermisoDto {
  id: number;
  codigo: string;
  nombre: string;
  modulo: string;
  descripcion: string | null;
}

export interface ClienteListDto {
  id: number;
  usuario_id: number;
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  estado: EstadoUsuario;
  ciudad: string | null;
  direccion: string | null;
  created_at: string | null;
}

export interface ClienteCreatePayload {
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  password: string;
  ciudad?: string | null;
  direccion?: string | null;
  estado?: EstadoUsuario;
}

export interface ClienteUpdatePayload {
  nombres?: string;
  apellidos?: string;
  email?: string;
  telefono?: string;
  ciudad?: string | null;
  direccion?: string | null;
  estado?: EstadoUsuario;
}

export interface UsuarioListDto {
  id: number;
  nombres: string;
  apellidos: string;
  username: string | null;
  email: string;
  telefono: string;
  estado: EstadoUsuario;
  ultimo_acceso_at: string | null;
  created_at: string | null;
  /** Presente en listados y GET detalle; puede faltar en respuestas POST legacy. */
  roles?: string[];
}

export interface UsuarioCreatePayload {
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  password: string;
  username?: string | null;
  estado?: EstadoUsuario;
  /** Organización SaaS (superadmin con filtro activo). Omitir = cuenta de plataforma. */
  tenant_id?: number | null;
}

export interface UsuarioUpdatePayload {
  nombres?: string;
  apellidos?: string;
  telefono?: string;
  username?: string | null;
  estado?: EstadoUsuario;
}

export interface BitacoraDto {
  id: number;
  usuario_id: number | null;
  modulo: string;
  entidad: string;
  entidad_id: number | null;
  accion: AccionBitacora;
  descripcion: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface TallerDto {
  id: number;
  tenant_id?: number | null;
  usuario_responsable_id: number;
  nombre_comercial: string;
  telefono_contacto: string;
  email_contacto: string;
  direccion: string;
  ciudad: string;
  descripcion: string | null;
  estado: EstadoTaller;
  created_at: string | null;
}

export interface TallerCreatePayload {
  tenant_id?: number | null;
  usuario_responsable_id: number;
  nombre_comercial: string;
  telefono_contacto: string;
  email_contacto: string;
  direccion: string;
  ciudad: string;
  descripcion?: string | null;
  estado?: EstadoTaller;
}

export interface TallerUpdatePayload {
  nombre_comercial?: string;
  telefono_contacto?: string;
  email_contacto?: string;
  direccion?: string;
  ciudad?: string;
  descripcion?: string | null;
  estado?: EstadoTaller;
}

/** Alta admin atómica: taller + cuenta responsable (login /taller). */
export interface TallerProvisionPayload {
  tenant_id?: number | null;
  nombre_comercial: string;
  telefono_contacto: string;
  email_contacto: string;
  direccion: string;
  ciudad: string;
  descripcion?: string | null;
  estado?: EstadoTaller;
  responsable_nombre_completo: string;
  responsable_email: string;
  responsable_telefono: string;
  responsable_password: string;
}

export interface TallerProvisionDto extends TallerDto {
  responsable_email: string;
  tenant_slug: string;
}

/** Resumen financiero global (solo ADMIN) — decimales como string (JSON). */
export interface TallerComisionFila {
  taller_id: number;
  nombre_comercial: string;
  n_comisiones: number;
  total_monto_servicio: string;
  total_comision_plataforma: string;
  total_neto_taller: string;
}

export interface AdminFinanzasResumen {
  porcentaje_plataforma: string;
  moneda: string;
  desde: string | null;
  hasta: string | null;
  n_comisiones: number;
  total_monto_servicio: string;
  total_comision_plataforma: string;
  total_neto_taller: string;
  n_pagos_pagados: number;
  total_monto_pagos: string;
  n_solicitudes_finalizadas: number;
  n_talleres_con_comision: number;
  ticket_promedio_pagado: string;
  tasa_conversion_pago_pct: string;
  por_taller: TallerComisionFila[];
}

export interface AdminComisionSerieFila {
  fecha: string;
  n_comisiones: number;
  total_monto_servicio: string;
  total_comision_plataforma: string;
  total_neto_taller: string;
}

export interface AdminFinanzasReportes {
  resumen: AdminFinanzasResumen;
  top_talleres: TallerComisionFila[];
  serie_diaria: AdminComisionSerieFila[];
}

/** Conteos + bitácora reciente (una sola petición para el resumen admin). */
export interface AdminPanelOverview {
  total_usuarios: number;
  total_talleres: number;
  total_roles: number;
  actividad_reciente: BitacoraDto[];
}

/** CU46 — KPIs operativos + financieros del administrador. */
export interface AdminKpisDto {
  periodo_desde: string | null;
  periodo_hasta: string | null;
  tenant_id: number | null;
  total_solicitudes: number;
  solicitudes_activas: number;
  solicitudes_finalizadas: number;
  solicitudes_canceladas: number;
  solicitudes_por_estado: Record<string, number>;
  pagos_confirmados: number;
  monto_pagos_bob: string;
  tiempo_promedio_atencion_min: number | null;
  sin_datos_en_periodo: boolean;
  resumen_financiero: AdminFinanzasResumen;
  top_talleres: TallerComisionFila[];
  serie_diaria: AdminComisionSerieFila[];
  analitica_operacional: OperationalKpisDto;
}

export interface PricingPlanDto {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  price_monthly_bob: number;
  currency: string;
  benefits: string[];
  featured: boolean;
  badge: string | null;
  cta_label: string;
  cta_router_link: string | null;
  cta_href: string | null;
  stripe_price_id: string | null;
  sort_order: number;
  active: boolean;
}

export interface PricingPlanUpdatePayload {
  name?: string;
  description?: string | null;
  price_monthly_bob?: number;
  currency?: string;
  benefits?: string[];
  featured?: boolean;
  badge?: string | null;
  cta_label?: string;
  cta_router_link?: string | null;
  cta_href?: string | null;
  stripe_price_id?: string | null;
  sort_order?: number;
  active?: boolean;
}

export interface StripePublicConfigDto {
  enabled: boolean;
  publishable_key: string | null;
}

export interface PublicCheckoutPayload {
  plan_slug: string;
  email: string;
  success_url: string;
  cancel_url: string;
}

export type EstadoTenant = 'ACTIVO' | 'INACTIVO' | 'SUSPENDIDO' | 'PENDIENTE';
export type PlanTenant = 'FREE' | 'STARTER' | 'PRO' | 'ENTERPRISE';
export type EstadoSuscripcionTenant =
  | 'TRIAL'
  | 'ACTIVA'
  | 'PAST_DUE'
  | 'CANCELADA'
  | 'SUSPENDIDA';

export interface TenantDto {
  id: number;
  slug: string;
  nombre: string;
  estado: EstadoTenant;
  plan: PlanTenant;
  dominio_custom: string | null;
  stripe_customer_id?: string | null;
  subscription_status?: EstadoSuscripcionTenant;
  subscription_ends_at?: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface TenantCreatePayload {
  slug: string;
  nombre: string;
  plan?: PlanTenant;
  dominio_custom?: string | null;
}

export interface TenantUpdatePayload {
  nombre?: string;
  estado?: EstadoTenant;
  plan?: PlanTenant;
  dominio_custom?: string | null;
  subscription_status?: EstadoSuscripcionTenant;
}

export type BackupTipo = 'PLATAFORMA' | 'TENANT' | 'TALLER' | 'EVIDENCIAS';
export type BackupEstado =
  | 'PENDIENTE'
  | 'EN_PROGRESO'
  | 'COMPLETADO'
  | 'FALLIDO'
  | 'RESTAURADO'
  | 'EXPIRADO';

export interface BackupDto {
  id: number;
  tenant_id: number | null;
  tenant_slug: string | null;
  tenant_nombre: string | null;
  tipo: BackupTipo;
  archivo: string;
  tamano_mb: number | null;
  estado: BackupEstado;
  incluye_evidencias: boolean;
  creado_en: string;
  expira_en: string | null;
  creado_por_usuario_id: number | null;
  error_mensaje: string | null;
  restaurado_en: string | null;
  restaurado_por_usuario_id: number | null;
  motivo_restore: string | null;
}

export interface BackupCreatePayload {
  tipo: BackupTipo;
  tenant_id?: number;
  incluir_evidencias?: boolean;
}
