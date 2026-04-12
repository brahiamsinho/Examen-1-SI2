import { Routes } from '@angular/router';
export const TALLERES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./talleres-list/talleres-list.component').then(m => m.TalleresListComponent)
  }
];
