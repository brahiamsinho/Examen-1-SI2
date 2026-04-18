import { Routes } from '@angular/router';
import { tallerAuthGuard } from '../core/guards/taller-auth.guard';

/** Rutas bajo `/taller` (login, recuperar, registro, panel). */
export const TALLER_ROUTES: Routes = [
  {
    path: 'recuperar',
    loadComponent: () =>
      import('./features/auth/taller-recover/taller-recover.component').then(
        (m) => m.TallerRecoverComponent,
      ),
  },
  {
    path: 'registro',
    loadComponent: () =>
      import('./features/auth/taller-register/taller-register.component').then(
        (m) => m.TallerRegisterComponent,
      ),
  },
  {
    path: 'panel',
    loadComponent: () => import('./shell/taller-shell.component').then((m) => m.TallerShellComponent),
    canActivate: [tallerAuthGuard],
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('./features/dashboard/taller-dashboard.component').then((m) => m.TallerDashboardComponent),
      },
      {
        path: 'mi-taller',
        loadComponent: () =>
          import('./features/mi-taller/taller-mi-taller.component').then((m) => m.TallerMiTallerComponent),
      },
      {
        path: 'tecnicos',
        loadComponent: () =>
          import('./features/tecnicos/taller-tecnicos.component').then((m) => m.TallerTecnicosComponent),
      },
    ],
  },
  {
    path: '',
    loadComponent: () =>
      import('./features/auth/taller-login/taller-login.component').then((m) => m.TallerLoginComponent),
  },
];
