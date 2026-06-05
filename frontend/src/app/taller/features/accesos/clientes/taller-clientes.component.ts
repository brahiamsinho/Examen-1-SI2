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
import { TallerAuthService } from '../../../../core/services/taller-auth.service';
import type {
  ClienteCreatePayload,
  ClienteListDto,
  ClienteUpdatePayload,
  EstadoUsuario,
} from '../../../../core/models/admin-api.models';

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
  readonly auth = inject(TallerAuthService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  clientes: ClienteListDto[] = [];
  search = '';
  estado: EstadoUsuario | '' = '';
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  modalCreate = false;
  modalEdit = false;
  modalDetail = false;
  selected: ClienteListDto | null = null;

  createForm: ClienteCreatePayload = {
    nombres: '',
    apellidos: '',
    email: '',
    telefono: '',
    password: '',
    ciudad: '',
    direccion: '',
    estado: 'ACTIVO',
  };

  editForm: ClienteUpdatePayload = {};

  readonly estados: EstadoUsuario[] = ['ACTIVO', 'INACTIVO', 'BLOQUEADO', 'PENDIENTE'];

  ngOnInit(): void {
    this.reload();
  }

  get puedeCrear(): boolean {
    return this.auth.tienePermiso('clientes:crear');
  }

  get puedeEditar(): boolean {
    return this.auth.tienePermiso('clientes:actualizar');
  }

  get puedeEliminar(): boolean {
    return this.auth.tienePermiso('clientes:eliminar');
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

  openCreateModal(): void {
    this.error = null;
    this.createForm = {
      nombres: '',
      apellidos: '',
      email: '',
      telefono: '',
      password: '',
      ciudad: '',
      direccion: '',
      estado: 'ACTIVO',
    };
    this.modalCreate = true;
    this.cdr.markForCheck();
  }

  openDetail(c: ClienteListDto): void {
    this.selected = c;
    this.modalDetail = true;
    this.cdr.markForCheck();
  }

  openEdit(c: ClienteListDto): void {
    this.selected = c;
    this.editForm = {
      nombres: c.nombres,
      apellidos: c.apellidos,
      email: c.email,
      telefono: c.telefono,
      ciudad: c.ciudad,
      direccion: c.direccion,
      estado: c.estado,
    };
    this.modalEdit = true;
    this.cdr.markForCheck();
  }

  create(): void {
    if (!this.puedeCrear) return;
    if (!this.createForm.password || this.createForm.password.length < 4) {
      this.error = 'La contraseña debe tener al menos 4 caracteres.';
      this.cdr.markForCheck();
      return;
    }
    this.busy = true;
    this.api
      .createCliente({ ...this.createForm })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.modalCreate = false;
          this.busy = false;
          this.reload();
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo crear el cliente (email o teléfono duplicado).';
          this.cdr.markForCheck();
        },
      });
  }

  saveEdit(): void {
    if (!this.selected || !this.puedeEditar) return;
    this.busy = true;
    this.api
      .updateCliente(this.selected.id, this.editForm)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.modalEdit = false;
          this.busy = false;
          this.reload();
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo actualizar el cliente.';
          this.cdr.markForCheck();
        },
      });
  }

  desactivar(c: ClienteListDto): void {
    if (!this.puedeEditar) return;
    if (!confirm(`¿Desactivar la cuenta de ${c.nombres} ${c.apellidos}? No podrá iniciar sesión.`)) {
      return;
    }
    this.busy = true;
    this.api
      .desactivarCliente(c.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.reload();
          this.closeModals();
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo desactivar el cliente.';
          this.cdr.markForCheck();
        },
      });
  }

  activar(c: ClienteListDto): void {
    if (!this.puedeEditar) return;
    this.busy = true;
    this.api
      .updateCliente(c.id, { estado: 'ACTIVO' })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.reload();
          this.closeModals();
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo activar el cliente.';
          this.cdr.markForCheck();
        },
      });
  }

  eliminar(c: ClienteListDto): void {
    if (!this.puedeEliminar) return;
    if (
      !confirm(
        `¿Eliminar permanentemente a ${c.nombres} ${c.apellidos}? Solo es posible si no tiene vehículos, solicitudes ni pagos.`,
      )
    ) {
      return;
    }
    this.busy = true;
    this.api
      .deleteCliente(c.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.reload();
          this.closeModals();
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.busy = false;
          const msg = err?.error?.detail;
          this.error =
            typeof msg === 'string'
              ? msg
              : 'No se pudo eliminar el cliente (puede tener historial operativo).';
          this.cdr.markForCheck();
        },
      });
  }

  closeModals(): void {
    this.modalCreate = this.modalEdit = this.modalDetail = false;
    this.selected = null;
    this.cdr.markForCheck();
  }
}
