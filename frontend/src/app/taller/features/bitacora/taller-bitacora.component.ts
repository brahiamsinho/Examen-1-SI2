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
import { TallerApiService } from '../../../core/services/taller-api.service';
import { TallerAuthService } from '../../../core/services/taller-auth.service';
import type { MeResponse } from '../../../core/models/auth.models';
import type {
  TallerAccionBitacora,
  TallerBitacoraDto,
  TecnicoPortalDto,
} from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-bitacora',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-bitacora.component.html',
  styleUrl: './taller-bitacora.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerBitacoraComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly auth = inject(TallerAuthService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  me: MeResponse | null = null;
  rows: TallerBitacoraDto[] = [];
  tecnicos: TecnicoPortalDto[] = [];
  loading = true;
  error: string | null = null;

  usuarioId = '';
  modulo = '';
  accion: TallerAccionBitacora | '' = '';
  desde = '';
  hasta = '';

  detail: TallerBitacoraDto | null = null;

  readonly modulos = [
    'auth',
    'talleres',
    'taller_responsable',
    'taller_emergencias',
    'tecnico',
    'taller_portal',
    'usuarios',
  ];

  readonly acciones: TallerAccionBitacora[] = [
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

  responsableLabel(): string {
    if (!this.me) return 'Responsable';
    const parts = [this.me.nombres, this.me.apellidos].filter(Boolean);
    return parts.length ? parts.join(' ') : this.me.email;
  }

  ngOnInit(): void {
    this.me = this.auth.getMe();
    this.api
      .listTecnicos()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (t) => {
          this.tecnicos = t;
          this.cdr.markForCheck();
        },
      });
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
          this.rows = r;
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.error =
            typeof detail === 'string'
              ? detail
              : 'No se pudo consultar la bitácora de tu taller.';
        },
      });
  }

  openDetail(row: TallerBitacoraDto): void {
    this.detail = row;
    this.cdr.markForCheck();
  }

  closeDetail(): void {
    this.detail = null;
    this.cdr.markForCheck();
  }
}
