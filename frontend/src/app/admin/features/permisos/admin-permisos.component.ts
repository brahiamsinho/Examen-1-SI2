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
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { PermisoDto } from '../../../core/models/admin-api.models';
import { filterRowsByQuery } from '../../../core/utils/list-filter.util';

@Component({
  selector: 'app-admin-permisos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-permisos.component.html',
  styleUrl: './admin-permisos.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminPermisosComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  readonly permisos = signal<PermisoDto[]>([]);
  readonly modulo = signal('');
  readonly search = signal('');
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly modulos = computed(() =>
    [...new Set(this.permisos().map((x) => x.modulo))].sort(),
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
      next: (p) => {
        this.permisos.set(p);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('No se pudieron cargar los permisos.');
      },
    });
  }
}
