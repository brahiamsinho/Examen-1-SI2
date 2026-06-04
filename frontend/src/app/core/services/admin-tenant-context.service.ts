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

  private readStored(): number | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  }
}
