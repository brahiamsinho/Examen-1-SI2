import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { BitacoraDto } from '../../../core/models/admin-api.models';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss',
})
export class AdminDashboardComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  totalUsuarios = 0;
  totalTalleres = 0;
  totalRoles = 0;
  actividad: BitacoraDto[] = [];
  loading = true;
  error: string | null = null;

  readonly quick = [
    { path: '/admin/panel/usuarios', label: 'Usuarios' },
    { path: '/admin/panel/roles', label: 'Roles' },
    { path: '/admin/panel/permisos', label: 'Permisos' },
    { path: '/admin/panel/talleres', label: 'Talleres' },
    { path: '/admin/panel/bitacora', label: 'Bitácora' },
  ] as const;

  ngOnInit(): void {
    this.loading = true;
    forkJoin({
      usuarios: this.api.listUsuarios().pipe(catchError(() => of([]))),
      talleres: this.api.listTalleres().pipe(catchError(() => of([]))),
      roles: this.api.listRoles().pipe(catchError(() => of([]))),
      bitacora: this.api.listBitacora({ limit: 8, offset: 0 }).pipe(catchError(() => of([]))),
    }).subscribe({
      next: ({ usuarios, talleres, roles, bitacora }) => {
        this.totalUsuarios = usuarios.length;
        this.totalTalleres = talleres.length;
        this.totalRoles = roles.length;
        this.actividad = bitacora;
        this.loading = false;
        this.error = null;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudieron cargar los datos del panel.';
      },
    });
  }
}
