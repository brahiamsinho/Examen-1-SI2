import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import type { ClienteListDto, EstadoUsuario } from '../../../../core/models/admin-api.models';

@Component({
  selector: 'app-taller-clientes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-clientes.component.html',
  styleUrl: './taller-clientes.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerClientesComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  clientes: ClienteListDto[] = [];
  search = '';
  estado: EstadoUsuario | '' = '';
  readonly loading = signal(true);
  error: string | null = null;

  readonly estados: EstadoUsuario[] = ['ACTIVO', 'INACTIVO', 'BLOQUEADO', 'PENDIENTE'];

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.api
      .listClientes()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (rows) => {
          this.clientes = rows;
          this.error = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudieron cargar las cuentas de clientes.';
          this.cdr.markForCheck();
        },
      });
  }

  get filtered(): ClienteListDto[] {
    let rows = this.clientes;
    if (this.estado) rows = rows.filter((c) => c.estado === this.estado);
    const q = this.search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (c) =>
          c.email.toLowerCase().includes(q) ||
          c.nombres.toLowerCase().includes(q) ||
          c.apellidos.toLowerCase().includes(q) ||
          (c.telefono && c.telefono.includes(q)),
      );
    }
    return rows;
  }
}
