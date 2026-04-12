import { Routes } from '@angular/router';
export const ACCESO_ROUTES: Routes = [
  {
    path: 'roles',
    loadComponent: () => import('./roles/roles.component').then(m => m.RolesComponent)
  }
];
