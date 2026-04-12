// src/app/app.routes.ts
// =========================================================
// Rutas principales de la aplicación Angular — Ciclo 1
// Lazy loading por módulo para mejor performance
// =========================================================
import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () =>
      import('./modules/landing/landing.component').then((m) => m.LandingComponent),
  },
  {
    path: 'movil',
    loadComponent: () =>
      import('./modules/movil/movil-info.component').then((m) => m.MovilInfoComponent),
  },

  // Autenticación (sin guard) — rutas explícitas para /auth y /auth/login
  {
    path: 'auth',
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'login' },
      {
        path: 'login',
        loadComponent: () =>
          import('./modules/auth/login/login.component').then((m) => m.LoginComponent),
      },
    ],
  },

  // Rutas protegidas
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./shared/components/layout/layout.component').then(
        (m) => m.LayoutComponent
      ),
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./modules/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent
          ),
      },
      {
        path: 'usuarios',
        loadChildren: () =>
          import('./modules/usuarios/usuarios.routes').then((m) => m.USUARIOS_ROUTES),
      },
      {
        path: 'vehiculos',
        loadChildren: () =>
          import('./modules/vehiculos/vehiculos.routes').then((m) => m.VEHICULOS_ROUTES),
      },
      {
        path: 'talleres',
        loadChildren: () =>
          import('./modules/talleres/talleres.routes').then((m) => m.TALLERES_ROUTES),
      },
      {
        path: 'bitacora',
        loadChildren: () =>
          import('./modules/bitacora/bitacora.routes').then((m) => m.BITACORA_ROUTES),
      },
      {
        path: 'acceso',
        loadChildren: () =>
          import('./modules/acceso/acceso.routes').then((m) => m.ACCESO_ROUTES),
      },
    ],
  },

  { path: '**', redirectTo: '' },
];
