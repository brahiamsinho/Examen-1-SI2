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
import {
  NavigationEnd,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';
import { filter } from 'rxjs/operators';
import { take } from 'rxjs';
import { TallerAuthService } from '../../core/services/taller-auth.service';
import { TallerApiService } from '../../core/services/taller-api.service';
import type { MeResponse } from '../../core/models/auth.models';
import type { TallerSuscripcionDto } from '../../core/models/taller-api.models';

export type TallerNavIcon =
  | 'home'
  | 'chart'
  | 'clipboard'
  | 'wrench'
  | 'users'
  | 'shield'
  | 'key'
  | 'inbox'
  | 'layers';

export interface TallerNavItem {
  path: string;
  label: string;
  exact: boolean;
  icon: TallerNavIcon;
  permiso?: string;
}

export interface TallerNavGroup {
  label: string;
  items: TallerNavItem[];
}

@Component({
  selector: 'app-taller-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './taller-shell.component.html',
  styleUrl: './taller-shell.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerShellComponent implements OnInit {
  readonly auth = inject(TallerAuthService);
  private readonly tallerApi = inject(TallerApiService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  me: MeResponse | null = null;
  subscription: TallerSuscripcionDto | null = null;
  pageTitle = 'Resumen';
  sidebarCollapsed = false;
  mobileNavOpen = false;
  navGroups: TallerNavGroup[] = [];

  private readonly navGroupsBase: TallerNavGroup[] = [
    {
      label: 'General',
      items: [{ path: '/taller/panel', label: 'Resumen', exact: true, icon: 'home' }],
    },
    {
      label: 'Emergencias',
      items: [
        {
          path: '/taller/panel/emergencias/solicitudes',
          label: 'Solicitudes',
          exact: false,
          icon: 'inbox',
          permiso: 'solicitudes_taller:leer',
        },
        {
          path: '/taller/panel/emergencias/mis-solicitudes',
          label: 'Mis solicitudes',
          exact: true,
          icon: 'clipboard',
          permiso: 'historial_atenciones:leer',
        },
        {
          path: '/taller/panel/emergencias/historial',
          label: 'Historial',
          exact: true,
          icon: 'clipboard',
          permiso: 'historial_atenciones:leer',
        },
        {
          path: '/taller/panel/emergencias/servicios-asignados',
          label: 'Servicios asignados',
          exact: true,
          icon: 'clipboard',
          permiso: 'historial_atenciones:leer',
        },
        {
          path: '/taller/panel/emergencias/comisiones',
          label: 'Comisiones',
          exact: true,
          icon: 'chart',
          permiso: 'comisiones:leer',
        },
        {
          path: '/taller/panel/emergencias/disponibilidad',
          label: 'Disponibilidad',
          exact: true,
          icon: 'chart',
          permiso: 'disponibilidad:gestionar',
        },
      ],
    },
    {
      label: 'Equipo y taller',
      items: [
        { path: '/taller/panel/mi-taller', label: 'Mi taller', exact: false, icon: 'wrench' },
        { path: '/taller/panel/tecnicos', label: 'Técnicos', exact: false, icon: 'wrench' },
        { path: '/taller/panel/bitacora', label: 'Bitácora', exact: true, icon: 'clipboard' },
      ],
    },
    {
      label: 'Suscripción',
      items: [
        {
          path: '/taller/panel/suscripcion',
          label: 'Planes SaaS',
          exact: true,
          icon: 'layers',
        },
      ],
    },
    {
      label: 'Accesos y cuentas',
      items: [
        {
          path: '/taller/panel/accesos/usuarios',
          label: 'Usuarios del taller',
          exact: true,
          icon: 'users',
          permiso: 'usuarios:leer',
        },
        {
          path: '/taller/panel/accesos/clientes',
          label: 'Cuentas clientes',
          exact: true,
          icon: 'users',
          permiso: 'clientes:leer',
        },
        {
          path: '/taller/panel/accesos/roles',
          label: 'Roles',
          exact: true,
          icon: 'shield',
          permiso: 'roles:gestionar',
        },
        {
          path: '/taller/panel/accesos/permisos',
          label: 'Permisos',
          exact: true,
          icon: 'key',
          permiso: 'roles:gestionar',
        },
      ],
    },
  ];

  ngOnInit(): void {
    this.loadSubscription();

    this.auth
      .refreshMeSiHaySesion()
      .pipe(take(1), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.me = this.auth.getMe();
        this.rebuildNavGroups();
        this.cdr.markForCheck();
      });

    // Mientras llega /auth/me, usa caché local para no dejar el menú vacío.
    this.me = this.auth.getMe();
    this.rebuildNavGroups();

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

  goUpgrade(slug: string, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    void this.router.navigate(['/taller/panel/suscripcion'], { queryParams: { upgrade: slug } });
    this.closeMobileNav();
  }

  userInitials(email: string | undefined): string {
    if (!email) return 'TL';
    const part = email.split('@')[0]?.slice(0, 2) ?? 'TL';
    return part.toUpperCase();
  }

  private rebuildNavGroups(): void {
    this.navGroups = this.navGroupsBase
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => !item.permiso || this.auth.tienePermiso(item.permiso)),
      }))
      .filter((group) => group.items.length > 0);
  }

  private syncPageTitle(url: string): void {
    const path = url.split('?')[0];
    const titles: Record<string, string> = {
      '/taller/panel': 'Resumen',
      '/taller/panel/mi-taller': 'Mi taller',
      '/taller/panel/tecnicos': 'Técnicos',
      '/taller/panel/emergencias/solicitudes': 'Solicitudes',
      '/taller/panel/emergencias/mis-solicitudes': 'Mis solicitudes',
      '/taller/panel/emergencias/historial': 'Historial',
      '/taller/panel/emergencias/servicios-asignados': 'Servicios asignados',
      '/taller/panel/emergencias/comisiones': 'Comisiones',
      '/taller/panel/emergencias/disponibilidad': 'Disponibilidad',
      '/taller/panel/accesos/usuarios': 'Usuarios del taller',
      '/taller/panel/accesos/clientes': 'Cuentas clientes',
      '/taller/panel/accesos/roles': 'Roles',
      '/taller/panel/accesos/permisos': 'Permisos',
      '/taller/panel/suscripcion': 'Planes SaaS',
      '/taller/panel/bitacora': 'Bitácora',
    };
    const match = Object.keys(titles)
      .sort((a, b) => b.length - a.length)
      .find((p) => path === p || path.startsWith(p + '/'));
    this.pageTitle = match ? titles[match] : 'Panel taller';
  }

  private loadSubscription(): void {
    this.tallerApi
      .getSuscripcion()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.subscription = data;
          this.cdr.markForCheck();
        },
        error: () => {
          this.subscription = null;
          this.cdr.markForCheck();
        },
      });
  }
}
