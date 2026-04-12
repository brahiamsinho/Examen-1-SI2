import { Routes } from '@angular/router';
export const BITACORA_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./bitacora-list/bitacora-list.component').then(m => m.BitacoraListComponent)
  }
];
