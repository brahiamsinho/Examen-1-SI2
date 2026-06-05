import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import type {
  AccionBitacora,
  AdminFinanzasReportes,
  AdminFinanzasResumen,
  AdminPanelOverview,
  BitacoraDto,
  ClienteListDto,
  PermisoDto,
  RolDto,
  RolPermisosDto,
  TallerCreatePayload,
  TallerDto,
  TallerProvisionDto,
  TallerProvisionPayload,
  TallerUpdatePayload,
  TenantCreatePayload,
  TenantDto,
  TenantUpdatePayload,
  UsuarioCreatePayload,
  UsuarioListDto,
  UsuarioUpdatePayload,
  PricingPlanDto,
  PricingPlanUpdatePayload,
} from '../models/admin-api.models';

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;
  private tenantsList$: Observable<TenantDto[]> | null = null;
  private pricingPlansList$: Observable<PricingPlanDto[]> | null = null;

  listTenants(): Observable<TenantDto[]> {
    if (!this.tenantsList$) {
      this.tenantsList$ = this.http.get<TenantDto[]>(`${this.base}/admin/tenants`).pipe(
        shareReplay({ bufferSize: 1, refCount: true }),
      );
    }
    return this.tenantsList$;
  }

  /** Tras crear/editar organización o vincular Stripe; el shell y listados deben ver datos frescos. */
  invalidateTenantsList(): void {
    this.tenantsList$ = null;
  }

  createTenant(body: TenantCreatePayload): Observable<TenantDto> {
    return this.http
      .post<TenantDto>(`${this.base}/admin/tenants`, body)
      .pipe(tap(() => this.invalidateTenantsList()));
  }

  updateTenant(id: number, body: TenantUpdatePayload): Observable<TenantDto> {
    return this.http
      .patch<TenantDto>(`${this.base}/admin/tenants/${id}`, body)
      .pipe(tap(() => this.invalidateTenantsList()));
  }

  linkTenantStripeCustomer(id: number, stripe_customer_id: string): Observable<TenantDto> {
    return this.http
      .post<TenantDto>(`${this.base}/admin/tenants/${id}/stripe-customer`, {
        stripe_customer_id,
      })
      .pipe(tap(() => this.invalidateTenantsList()));
  }

  createTenantCheckout(
    id: number,
    body: { success_url: string; cancel_url: string },
  ): Observable<{ checkout_url: string; session_id: string }> {
    return this.http.post<{ checkout_url: string; session_id: string }>(
      `${this.base}/admin/tenants/${id}/checkout-session`,
      body,
    );
  }

  createTenantBillingPortal(
    id: number,
    return_url: string,
  ): Observable<{ portal_url: string }> {
    return this.http.post<{ portal_url: string }>(
      `${this.base}/admin/tenants/${id}/billing-portal`,
      { return_url },
    );
  }

  listPublicTenants(): Observable<{ slug: string; nombre: string }[]> {
    return this.http.get<{ slug: string; nombre: string }[]>(`${this.base}/public/tenants`);
  }

  listUsuarios(filters?: { tenant_id?: number }): Observable<UsuarioListDto[]> {
    let params = new HttpParams();
    if (filters?.tenant_id != null) {
      params = params.set('tenant_id', String(filters.tenant_id));
    }
    return this.http.get<UsuarioListDto[]>(`${this.base}/usuarios/`, { params });
  }

  listClientes(filters?: { tenant_id?: number }): Observable<ClienteListDto[]> {
    let params = new HttpParams();
    if (filters?.tenant_id != null) {
      params = params.set('tenant_id', String(filters.tenant_id));
    }
    return this.http.get<ClienteListDto[]>(`${this.base}/clientes/`, { params });
  }

  getUsuario(id: number): Observable<UsuarioListDto> {
    return this.http.get<UsuarioListDto>(`${this.base}/usuarios/${id}`);
  }

  createUsuario(body: UsuarioCreatePayload): Observable<UsuarioListDto> {
    return this.http.post<UsuarioListDto>(`${this.base}/usuarios/`, body);
  }

  updateUsuario(id: number, body: UsuarioUpdatePayload): Observable<UsuarioListDto> {
    // Backend devuelve UsuarioRead; reinyectamos roles en el componente si hace falta.
    return this.http.put<UsuarioListDto>(`${this.base}/usuarios/${id}`, body);
  }

  deleteUsuario(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/usuarios/${id}`);
  }

  assignRoles(usuarioId: number, rolIds: number[]): Observable<void> {
    return this.http.put<void>(`${this.base}/usuarios/${usuarioId}/roles`, {
      rol_ids: rolIds,
    });
  }

  listRoles(): Observable<RolDto[]> {
    return this.http.get<RolDto[]>(`${this.base}/roles/`);
  }

  createRol(nombre: string, descripcion: string | null): Observable<RolDto> {
    return this.http.post<RolDto>(`${this.base}/roles/`, { nombre, descripcion });
  }

  getRolPermisoIds(rolId: number): Observable<RolPermisosDto> {
    return this.http.get<RolPermisosDto>(`${this.base}/roles/${rolId}/permisos`);
  }

  setRolPermisos(rolId: number, permisoIds: number[]): Observable<void> {
    return this.http.put<void>(`${this.base}/roles/${rolId}/permisos`, {
      permiso_ids: permisoIds,
    });
  }

  listPermisos(): Observable<PermisoDto[]> {
    return this.http.get<PermisoDto[]>(`${this.base}/permisos/`);
  }

  listBitacora(filters: {
    usuario_id?: number;
    modulo?: string;
    accion?: AccionBitacora;
    desde?: string;
    hasta?: string;
    limit?: number;
    offset?: number;
  }): Observable<BitacoraDto[]> {
    let params = new HttpParams();
    if (filters.usuario_id != null) {
      params = params.set('usuario_id', String(filters.usuario_id));
    }
    if (filters.modulo) params = params.set('modulo', filters.modulo);
    if (filters.accion) params = params.set('accion', filters.accion);
    if (filters.desde) params = params.set('desde', filters.desde);
    if (filters.hasta) params = params.set('hasta', filters.hasta);
    if (filters.limit != null) params = params.set('limit', String(filters.limit));
    if (filters.offset != null) params = params.set('offset', String(filters.offset));
    return this.http.get<BitacoraDto[]>(`${this.base}/bitacora/`, { params });
  }

  listTalleres(filters?: { tenant_id?: number }): Observable<TallerDto[]> {
    let params = new HttpParams();
    if (filters?.tenant_id != null) {
      params = params.set('tenant_id', String(filters.tenant_id));
    }
    return this.http.get<TallerDto[]>(`${this.base}/talleres/`, { params });
  }

  getTaller(id: number): Observable<TallerDto> {
    return this.http.get<TallerDto>(`${this.base}/talleres/${id}`);
  }

  createTaller(body: TallerCreatePayload): Observable<TallerDto> {
    return this.http.post<TallerDto>(`${this.base}/talleres/`, body);
  }

  provisionTaller(body: TallerProvisionPayload): Observable<TallerProvisionDto> {
    return this.http.post<TallerProvisionDto>(`${this.base}/talleres/provision`, body);
  }

  updateTaller(id: number, body: TallerUpdatePayload): Observable<TallerDto> {
    return this.http.put<TallerDto>(`${this.base}/talleres/${id}`, body);
  }

  getPanelOverview(filters?: { tenant_id?: number }): Observable<AdminPanelOverview> {
    let params = new HttpParams();
    if (filters?.tenant_id != null) {
      params = params.set('tenant_id', String(filters.tenant_id));
    }
    return this.http.get<AdminPanelOverview>(`${this.base}/admin/panel/overview`, { params });
  }

  getFinanzasResumen(filters?: {
    desde?: string;
    hasta?: string;
    tenant_id?: number;
  }): Observable<AdminFinanzasResumen> {
    let params = new HttpParams();
    if (filters?.desde) params = params.set('desde', filters.desde);
    if (filters?.hasta) params = params.set('hasta', filters.hasta);
    if (filters?.tenant_id != null) params = params.set('tenant_id', String(filters.tenant_id));
    return this.http.get<AdminFinanzasResumen>(`${this.base}/admin/finanzas/resumen`, { params });
  }

  getFinanzasReportes(filters?: {
    desde?: string;
    hasta?: string;
    tenant_id?: number;
  }): Observable<AdminFinanzasReportes> {
    let params = new HttpParams();
    if (filters?.desde) params = params.set('desde', filters.desde);
    if (filters?.hasta) params = params.set('hasta', filters.hasta);
    if (filters?.tenant_id != null) params = params.set('tenant_id', String(filters.tenant_id));
    return this.http.get<AdminFinanzasReportes>(`${this.base}/admin/finanzas/reportes`, { params });
  }

  listPricingPlans(): Observable<PricingPlanDto[]> {
    if (!this.pricingPlansList$) {
      this.pricingPlansList$ = this.http
        .get<PricingPlanDto[]>(`${this.base}/admin/pricing-plans`)
        .pipe(shareReplay({ bufferSize: 1, refCount: true }));
    }
    return this.pricingPlansList$;
  }

  invalidatePricingPlansList(): void {
    this.pricingPlansList$ = null;
  }

  updatePricingPlan(slug: string, payload: PricingPlanUpdatePayload): Observable<PricingPlanDto> {
    return this.http
      .patch<PricingPlanDto>(`${this.base}/admin/pricing-plans/${slug}`, payload)
      .pipe(tap(() => this.invalidatePricingPlansList()));
  }
}
