import { Injectable } from '@angular/core';

const KEY = 'ev_tenant_slug';

/** Slug de organización para login taller (header X-Tenant-Slug). */
@Injectable({ providedIn: 'root' })
export class TenantSlugService {
  get(): string | null {
    return localStorage.getItem(KEY);
  }

  set(slug: string | null): void {
    const s = slug?.trim().toLowerCase();
    if (!s) {
      localStorage.removeItem(KEY);
      return;
    }
    localStorage.setItem(KEY, s);
  }

  resolveFromQueryParam(org: string | null | undefined): string | null {
    if (org?.trim()) {
      const s = org.trim().toLowerCase();
      this.set(s);
      return s;
    }
    return this.get();
  }
}
