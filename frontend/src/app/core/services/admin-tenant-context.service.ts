import { Injectable, inject, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { AdminAuthService } from './admin-auth.service';

const STORAGE_KEY = 'ev_admin_selected_tenant_id';

/** Organización activa para superadmin de plataforma (filtros ?tenant_id=). */
@Injectable({ providedIn: 'root' })
export class AdminTenantContextService {
  private readonly auth = inject(AdminAuthService);

  readonly selectedTenantId = signal<number | null>(this.readStored());

  private readonly tenantChanges = new Subject<number | null>();
  readonly tenantChanges$ = this.tenantChanges.asObservable();

  isPlatformSuperadmin(): boolean {
    return !!this.auth.getMe()?.is_platform_superadmin;
  }

  setSelectedTenantId(id: number | null): void {
    if (this.selectedTenantId() === id) {
      return;
    }
    this.selectedTenantId.set(id);
    if (id == null) {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, String(id));
    }
    this.tenantChanges.next(id);
  }

  tenantQueryParam(): { tenant_id?: number } {
    if (!this.isPlatformSuperadmin()) {
      return {};
    }
    const id = this.selectedTenantId();
    return id != null ? { tenant_id: id } : {};
  }

  /** tenant_id en body POST al crear usuarios/talleres dentro de una organización. */
  tenantCreateBody(): { tenant_id?: number } {
    return this.tenantQueryParam();
  }

  orgScopeLabel(tenants: { id: number; slug: string; nombre: string }[]): string {
    if (!this.isPlatformSuperadmin()) {
      return '';
    }
    const id = this.selectedTenantId();
    if (id == null) {
      return 'Todas (plataforma) — elige una organización para dar de alta personal o talleres.';
    }
    const t = tenants.find((x) => x.id === id);
    return t ? `${t.nombre} · slug: ${t.slug}` : `Organización #${id}`;
  }

  tenantById(
    tenants: { id: number; slug: string; nombre: string }[],
    id: number | null,
  ): { id: number; slug: string; nombre: string } | null {
    if (id == null) return null;
    return tenants.find((x) => x.id === id) ?? null;
  }

  private readStored(): number | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  }
}
