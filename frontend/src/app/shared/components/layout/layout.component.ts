// Shell principal alineado al AdminLayout del prototipo Figma Make (EmergenciasViales).
import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { filter, map, startWith } from 'rxjs/operators';
import { AuthService } from '../../../core/services/auth.service';

interface NavItem {
  path: string;
  label: string;
  icon: 'dashboard' | 'users' | 'shield' | 'key' | 'wrench' | 'clipboard' | 'car';
  exact?: boolean;
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class LayoutComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthService);

  /** Ruta actual (sin query) para títulos y estado activo reactivos */
  private readonly currentPath = toSignal(
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      map(() => this.router.url.split('?')[0]),
      startWith(this.router.url.split('?')[0])
    ),
    { initialValue: this.router.url.split('?')[0] }
  );

  readonly mobileOpen = signal(false);

  readonly navItems: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: 'dashboard', exact: true },
    { path: '/usuarios', label: 'Usuarios', icon: 'users' },
    { path: '/vehiculos', label: 'Vehículos', icon: 'car' },
    { path: '/acceso/roles', label: 'Roles', icon: 'shield' },
    { path: '/acceso/roles', label: 'Permisos', icon: 'key' },
    { path: '/talleres', label: 'Talleres', icon: 'wrench' },
    { path: '/bitacora', label: 'Bitácora', icon: 'clipboard' },
  ];

  readonly userInitials = computed(() => {
    const u = this.auth.currentUser();
    if (!u) return '??';
    const a = (u.nombres?.trim()?.[0] ?? '').toUpperCase();
    const b = (u.apellidos?.trim()?.[0] ?? '').toUpperCase();
    const ini = `${a}${b}`;
    return ini || (u.email?.[0]?.toUpperCase() ?? 'US');
  });

  readonly userDisplayName = computed(() => {
    const u = this.auth.currentUser();
    if (!u) return 'Usuario';
    const full = `${u.nombres ?? ''} ${u.apellidos ?? ''}`.trim();
    return full || u.email;
  });

  readonly pageTitle = computed(() => {
    const url = this.currentPath();
    for (const item of this.navItems) {
      if (item.exact && url === item.path) return item.label;
      if (!item.exact && (url === item.path || url.startsWith(item.path + '/'))) {
        return item.label;
      }
    }
    if (url === '/dashboard') return 'Dashboard';
    return 'Panel de Administración';
  });

  openMobile(): void {
    this.mobileOpen.set(true);
  }

  closeMobile(): void {
    this.mobileOpen.set(false);
  }

  onLogout(): void {
    this.closeMobile();
    this.auth.logout();
  }

  isNavActive(item: NavItem): boolean {
    const url = this.currentPath();
    if (item.exact) return url === item.path;
    return url === item.path || url.startsWith(item.path + '/');
  }
}
