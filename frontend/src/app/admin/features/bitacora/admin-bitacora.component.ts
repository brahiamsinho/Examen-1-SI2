import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { AccionBitacora, BitacoraDto } from '../../../core/models/admin-api.models';

@Component({
  selector: 'app-admin-bitacora',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-bitacora.component.html',
  styleUrl: './admin-bitacora.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminBitacoraComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  rows: BitacoraDto[] = [];
  loading = true;
  error: string | null = null;

  usuarioId = '';
  modulo = '';
  accion: AccionBitacora | '' = '';
  desde = '';
  hasta = '';

  detail: BitacoraDto | null = null;

  readonly acciones: AccionBitacora[] = [
    'CREAR',
    'ACTUALIZAR',
    'ELIMINAR',
    'INICIAR_SESION',
    'CERRAR_SESION',
    'RESTABLECER_CONTRASENA',
    'ASIGNAR_ROL',
    'ASIGNAR_PERMISO',
    'CONSULTAR',
  ];

  ngOnInit(): void {
    this.fetch();
  }

  fetch(): void {
    this.loading = true;
    this.error = null;
    const uid = this.usuarioId.trim() ? Number(this.usuarioId) : undefined;
    if (this.usuarioId.trim() && Number.isNaN(uid)) {
      this.error = 'ID de usuario inválido.';
      this.loading = false;
      this.cdr.markForCheck();
      return;
    }
    const desdeIso = this.desde ? new Date(this.desde).toISOString() : undefined;
    const hastaIso = this.hasta ? new Date(this.hasta).toISOString() : undefined;
    this.api
      .listBitacora({
        usuario_id: uid,
        modulo: this.modulo.trim() || undefined,
        accion: this.accion || undefined,
        desde: desdeIso,
        hasta: hastaIso,
        limit: 100,
        offset: 0,
      })
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (r) => {
          this.rows = Array.isArray(r) ? r : [];
        },
        error: () => {
          this.error = 'No se pudo consultar la bitácora.';
        },
      });
  }

  openDetail(row: BitacoraDto): void {
    this.detail = row;
    this.cdr.markForCheck();
  }

  closeDetail(): void {
    this.detail = null;
    this.cdr.markForCheck();
  }
}
