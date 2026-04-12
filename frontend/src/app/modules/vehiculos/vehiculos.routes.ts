import { Routes } from '@angular/router';
export const VEHICULOS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./vehiculos-list/vehiculos-list.component').then(m => m.VehiculosListComponent)
  }
];
