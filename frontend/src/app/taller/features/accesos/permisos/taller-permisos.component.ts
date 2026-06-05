import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import type { PermisoDto } from '../../../../core/models/admin-api.models';
import { filterRowsByQuery } from '../../../../core/utils/list-filter.util';

@Component({
  selector: 'app-taller-permisos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-permisos.component.html',
  styleUrl: './taller-permisos.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerPermisosComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly permisos = signal<PermisoDto[]>([]);
  readonly search = signal('');
  readonly modulo = signal('');
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly modulos = computed(() =>
    [...new Set(this.permisos().map((p) => p.modulo))].sort(),
  );

  readonly filtered = computed(() => {
    let rows = this.permisos();
    const modulo = this.modulo();
    if (modulo) rows = rows.filter((p) => p.modulo === modulo);
    return filterRowsByQuery(rows, this.search(), (p) => [
      p.codigo,
      p.nombre,
      p.descripcion,
    ]);
  });

  ngOnInit(): void {
    this.api.listPermisos().subscribe({
      next: (rows) => {
        this.permisos.set(rows);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('No se pudo cargar el catálogo de permisos.');
      },
    });
  }
}
