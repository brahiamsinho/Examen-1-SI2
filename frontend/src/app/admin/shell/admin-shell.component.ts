import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  NavigationEnd,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';
import { filter } from 'rxjs/operators';
import { AdminApiService } from '../../core/services/admin-api.service';
import { AdminAuthService } from '../../core/services/admin-auth.service';
import { AdminTenantContextService } from '../../core/services/admin-tenant-context.service';
import type { MeResponse } from '../../core/models/auth.models';
import type { TenantDto } from '../../core/models/admin-api.models';

export type AdminNavIcon =
  | 'home'
  | 'chart'
  | 'building'
  | 'users'
  | 'shield'
  | 'key'
  | 'wrench'
  | 'clipboard'
  | 'credit-card';

export interface AdminNavItem {
  path: string;
  label: string;
  exact: boolean;
  icon: AdminNavIcon;
  superadminOnly?: boolean;
}

export interface AdminNavGroup {
  label: string;
  items: AdminNavItem[];
}

@Component({
  selector: 'app-admin-shell',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './admin-shell.component.html',
  styleUrl: './admin-shell.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminShellComponent implements OnInit {
  readonly auth = inject(AdminAuthService);
  readonly tenantCtx = inject(AdminTenantContextService);
  private readonly api = inject(AdminApiService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  tenants: TenantDto[] = [];
  me: MeResponse | null = null;
  /** Propiedad writable para ngModel (nunca un getter). */
  tenantFilter = 'all';
  pageTitle = 'Panel';
  sidebarCollapsed = false;
  mobileNavOpen = false;

  /** Evita recrear arrays en cada ciclo de detección (provocaba bucle con routerLinkActive). */
  navGroups: AdminNavGroup[] = [];

  private readonly navGroupsBase: AdminNavGroup[] = [
    {
      label: 'General',
      items: [
        { path: '/admin/panel', label: 'Resumen', exact: true, icon: 'home' },
        { path: '/admin/panel/finanzas', label: 'Finanzas', exact: true, icon: 'chart' },
      ],
    },
    {
      label: 'Plataforma SaaS',
      items: [
        {
          path: '/admin/panel/organizaciones',
          label: 'Organizaciones',
          exact: true,
          icon: 'building',
          superadminOnly: true,
        },
      ],
    },
    {
      label: 'Comercial',
      items: [
        {
          path: '/admin/panel/planes-precios',
          label: 'Planes y precios',
          exact: true,
          icon: 'credit-card',
          superadminOnly: true,
        },
      ],
    },
    {
      label: 'Operaciones',
      items: [
        { path: '/admin/panel/talleres', label: 'Talleres', exact: false, icon: 'wrench' },
        { path: '/admin/panel/bitacora', label: 'Bitácora', exact: false, icon: 'clipboard' },
      ],
    },
  ];

  ngOnInit(): void {
    this.me = this.auth.getMe();
    const stored = this.tenantCtx.selectedTenantId();
    this.tenantFilter = stored == null ? 'all' : String(stored);
    this.rebuildNavGroups();

    this.tenantCtx.tenantChanges$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((id) => {
        this.tenantFilter = id == null ? 'all' : String(id);
        this.cdr.markForCheck();
      });

    this.syncPageTitle(this.router.url);
    this.router.events
      .pipe(
        filter((e): e is NavigationEnd => e instanceof NavigationEnd),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((e) => {
        this.syncPageTitle(e.urlAfterRedirects);
        this.mobileNavOpen = false;
        this.cdr.markForCheck();
      });

    if (!this.tenantCtx.isPlatformSuperadmin()) {
      return;
    }
    this.api
      .listTenants()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (rows) => {
          this.tenants = rows;
          this.cdr.markForCheck();
        },
        error: () => {
          this.tenants = [];
          this.cdr.markForCheck();
        },
      });
  }

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
    this.cdr.markForCheck();
  }

  toggleMobileNav(): void {
    this.mobileNavOpen = !this.mobileNavOpen;
    this.cdr.markForCheck();
  }

  closeMobileNav(): void {
    this.mobileNavOpen = false;
    this.cdr.markForCheck();
  }

  onTenantFilterChange(raw: string): void {
    if (raw === '' || raw === 'all') {
      this.tenantFilter = 'all';
      this.tenantCtx.setSelectedTenantId(null);
    } else {
      const id = Number(raw);
      this.tenantFilter = Number.isFinite(id) ? String(id) : 'all';
      this.tenantCtx.setSelectedTenantId(Number.isFinite(id) ? id : null);
    }
    this.cdr.markForCheck();
  }

  userInitials(email: string | undefined): string {
    if (!email) return 'AD';
    const part = email.split('@')[0]?.slice(0, 2) ?? 'AD';
    return part.toUpperCase();
  }

  private rebuildNavGroups(): void {
    const sa = this.tenantCtx.isPlatformSuperadmin();
    this.navGroups = this.navGroupsBase
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => !item.superadminOnly || sa),
      }))
      .filter((group) => group.items.length > 0);
  }

  private syncPageTitle(url: string): void {
    const path = url.split('?')[0];
    const titles: Record<string, string> = {
      '/admin/panel': 'Resumen',
      '/admin/panel/finanzas': 'Finanzas',
      '/admin/panel/organizaciones': 'Organizaciones',
      '/admin/panel/planes-precios': 'Planes y precios',
      '/admin/panel/usuarios': 'Usuarios',
      '/admin/panel/roles': 'Roles',
      '/admin/panel/permisos': 'Permisos',
      '/admin/panel/talleres': 'Talleres',
      '/admin/panel/bitacora': 'Bitácora',
    };
    const match = Object.keys(titles)
      .sort((a, b) => b.length - a.length)
      .find((p) => path === p || path.startsWith(p + '/'));
    this.pageTitle = match ? titles[match] : 'Panel';
  }
}
