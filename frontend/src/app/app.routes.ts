import { Routes } from '@angular/router';
import { ADMIN_ROUTES } from './admin/admin.routes';

/** Rutas raíz. Admin sin lazy load (evita pantalla negra al cargar /admin/panel). */
export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () =>
      import('./public/pages/landing/landing-page.component').then((m) => m.LandingPageComponent),
  },
  {
    path: 'admin',
    children: ADMIN_ROUTES,
  },
  {
    path: 'taller',
    loadChildren: () => import('./taller/taller.routes').then((m) => m.TALLER_ROUTES),
  },
  { path: '**', redirectTo: '' },
];
