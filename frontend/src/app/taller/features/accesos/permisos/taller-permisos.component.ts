import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import type { PermisoDto } from '../../../../core/models/admin-api.models';

@Component({
  selector: 'app-taller-permisos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-permisos.component.html',
  styleUrl: './taller-permisos.component.scss',
})
export class TallerPermisosComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  permisos: PermisoDto[] = [];
  search = '';
  modulo = '';
  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.api.listPermisos().subscribe({
      next: (rows) => {
        this.permisos = rows;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudo cargar el catálogo de permisos.';
      },
    });
  }

  get modulos(): string[] {
    return [...new Set(this.permisos.map((p) => p.modulo))].sort();
  }

  get filtered(): PermisoDto[] {
    let rows = this.permisos;
    if (this.modulo) rows = rows.filter((p) => p.modulo === this.modulo);
    const q = this.search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (p) =>
          p.codigo.toLowerCase().includes(q) ||
          p.nombre.toLowerCase().includes(q) ||
          (p.descripcion && p.descripcion.toLowerCase().includes(q)),
      );
    }
    return rows;
  }
}
