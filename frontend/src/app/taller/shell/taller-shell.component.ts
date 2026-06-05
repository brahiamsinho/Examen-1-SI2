import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
  signal,
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
import { catchError, interval, of, startWith, switchMap, take } from 'rxjs';
import { TallerAuthService } from '../../core/services/taller-auth.service';
import { TallerComunicacionApiService } from '../../core/services/taller-comunicacion-api.service';
import type { MeResponse } from '../../core/models/auth.models';

export type TallerNavIcon =
  | 'home'
  | 'chart'
  | 'clipboard'
  | 'wrench'
  | 'users'
  | 'shield'
  | 'key'
  | 'inbox'
  | 'bell';

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
  private readonly comunicacion = inject(TallerComunicacionApiService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  me: MeResponse | null = null;
  pageTitle = 'Resumen';
  sidebarCollapsed = false;
  mobileNavOpen = false;
  navGroups: TallerNavGroup[] = [];
  readonly unreadNotificaciones = signal(0);
  showNotificaciones = true;
  private notifPollStarted = false;

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
        {
          path: '/taller/panel/comunicacion/notificaciones',
          label: 'Notificaciones',
          exact: true,
          icon: 'bell',
          permiso: 'notificaciones:leer',
        },
      ],
    },
    {
      label: 'Equipo y taller',
      items: [
        { path: '/taller/panel/mi-taller', label: 'Mi taller', exact: false, icon: 'wrench' },
        { path: '/taller/panel/tecnicos', label: 'Técnicos', exact: false, icon: 'wrench' },
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
    this.me = this.auth.getMe();
    this.actualizarAccesoNotificaciones();
    this.rebuildNavGroups();
    this.iniciarPollingNotificaciones();

    this.auth
      .refreshMeSiHaySesion()
      .pipe(take(1), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.me = this.auth.getMe();
        this.actualizarAccesoNotificaciones();
        this.rebuildNavGroups();
        this.iniciarPollingNotificaciones();
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
      '/taller/panel/comunicacion/notificaciones': 'Notificaciones',
      '/taller/panel/accesos/usuarios': 'Usuarios del taller',
      '/taller/panel/accesos/clientes': 'Cuentas clientes',
      '/taller/panel/accesos/roles': 'Roles',
      '/taller/panel/accesos/permisos': 'Permisos',
    };
    if (titles[path]) {
      this.pageTitle = titles[path];
      return;
    }
    const match = Object.keys(titles)
      .filter((p) => p !== '/taller/panel')
      .sort((a, b) => b.length - a.length)
      .find((p) => path.startsWith(p + '/'));
    this.pageTitle = match ? titles[match] : path === '/taller/panel' ? 'Resumen' : 'Panel taller';
  }

  private actualizarAccesoNotificaciones(): void {
    this.showNotificaciones =
      !this.auth.getMe()?.permisos?.length || this.auth.tienePermiso('notificaciones:leer');
  }

  private iniciarPollingNotificaciones(): void {
    if (this.notifPollStarted || !this.showNotificaciones) return;
    this.notifPollStarted = true;
    interval(30_000)
      .pipe(
        startWith(0),
        switchMap(() =>
          this.comunicacion.listNotificaciones({ soloNoLeidas: true, limit: 99 }).pipe(catchError(() => of([]))),
        ),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((list) => {
        this.unreadNotificaciones.set(list.length);
        this.cdr.markForCheck();
      });
  }
}
