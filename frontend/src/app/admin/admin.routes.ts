import { Routes } from '@angular/router';
import { adminAuthGuard } from '../core/guards/admin-auth.guard';
import { adminGuestGuard } from '../core/guards/admin-guest.guard';
import { AdminLoginComponent } from './features/auth/admin-login/admin-login.component';
import { AdminShellComponent } from './shell/admin-shell.component';

/**
 * Shell eager; dashboard lazy (si el dashboard falla, el shell y la barra lateral siguen visibles).
 */
export const ADMIN_ROUTES: Routes = [
  {
    path: 'login',
    component: AdminLoginComponent,
    canActivate: [adminGuestGuard],
  },
  {
    path: 'recuperar',
    loadComponent: () =>
      import('./features/auth/admin-recover/admin-recover.component').then(
        (m) => m.AdminRecoverComponent,
      ),
  },
  {
    path: 'panel',
    component: AdminShellComponent,
    canActivate: [adminAuthGuard],
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('./features/dashboard/admin-dashboard.component').then(
            (m) => m.AdminDashboardComponent,
          ),
      },
      {
        path: 'usuarios',
        loadComponent: () =>
          import('./features/usuarios/admin-usuarios.component').then((m) => m.AdminUsuariosComponent),
      },
      {
        path: 'roles',
        loadComponent: () =>
          import('./features/roles/admin-roles.component').then((m) => m.AdminRolesComponent),
      },
      {
        path: 'permisos',
        loadComponent: () =>
          import('./features/permisos/admin-permisos.component').then((m) => m.AdminPermisosComponent),
      },
      {
        path: 'talleres',
        loadComponent: () =>
          import('./features/talleres/admin-talleres.component').then((m) => m.AdminTalleresComponent),
      },
      {
        path: 'bitacora',
        loadComponent: () =>
          import('./features/bitacora/admin-bitacora.component').then((m) => m.AdminBitacoraComponent),
      },
      {
        path: 'finanzas',
        loadComponent: () =>
          import('./features/finanzas/admin-finanzas.component').then((m) => m.AdminFinanzasComponent),
      },
      {
        path: 'organizaciones',
        loadComponent: () =>
          import('./features/organizaciones/admin-organizaciones.component').then(
            (m) => m.AdminOrganizacionesComponent,
          ),
      },
    ],
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'login',
  },
];
