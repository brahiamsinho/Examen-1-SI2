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
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import type { TallerDisponibilidadDto } from '../../../../core/models/taller-emergencias.models';

@Component({
  selector: 'app-taller-emergencias-disponibilidad',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-emergencias-disponibilidad.component.html',
  styleUrl: './taller-emergencias-disponibilidad.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerEmergenciasDisponibilidadComponent implements OnInit {
  private readonly api = inject(TallerEmergenciasApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  data: TallerDisponibilidadDto | null = null;
  acepta = true;
  capacidad = 10;
  observacion = '';
  readonly loading = signal(true);
  saving = false;
  error: string | null = null;
  success: string | null = null;

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error = null;
    this.success = null;
    this.api
      .getDisponibilidad()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (d) => {
          this.data = d;
          this.acepta = d.acepta_nuevas_solicitudes;
          this.capacidad = d.capacidad_maxima_diaria;
          this.observacion = d.observacion ?? '';
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.data = null;
          this.error = this.msg(err, 'No se pudo cargar la disponibilidad del taller.');
          this.cdr.markForCheck();
        },
      });
  }

  guardar(): void {
    if (this.capacidad < 1 || this.capacidad > 500) {
      this.error = 'La capacidad máxima diaria debe estar entre 1 y 500.';
      this.cdr.markForCheck();
      return;
    }
    this.saving = true;
    this.error = null;
    this.success = null;
    this.api
      .putDisponibilidad({
        acepta_nuevas_solicitudes: this.acepta,
        capacidad_maxima_diaria: this.capacidad,
        observacion: this.observacion.trim() || null,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (d) => {
          this.data = d;
          this.saving = false;
          this.success = 'Cambios guardados correctamente.';
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.saving = false;
          this.error = this.msg(err, 'No se pudo guardar la disponibilidad.');
          this.cdr.markForCheck();
        },
      });
  }

  private msg(err: { error?: { detail?: unknown } }, fallback: string): string {
    const d = err?.error?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d) && d.length && typeof d[0] === 'object' && d[0] !== null && 'msg' in d[0]) {
      return String((d[0] as { msg: string }).msg);
    }
    return fallback;
  }
}
