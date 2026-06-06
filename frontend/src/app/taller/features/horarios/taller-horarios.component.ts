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
import { TallerApiService } from '../../../core/services/taller-api.service';
import type { TallerHorarioDiaDto, TallerHorariosDto } from '../../../core/models/taller-api.models';

type HorarioRow = TallerHorarioDiaDto & {
  aperturaInput: string;
  cierreInput: string;
};

@Component({
  selector: 'app-taller-horarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-horarios.component.html',
  styleUrl: './taller-horarios.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerHorariosComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  data: TallerHorariosDto | null = null;
  rows: HorarioRow[] = [];
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
      .getHorarios()
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
          this.rows = d.horarios.map((h) => this.toRow(h));
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.data = null;
          this.rows = [];
          this.error = this.msg(err, 'No se pudieron cargar los horarios.');
          this.cdr.markForCheck();
        },
      });
  }

  guardar(): void {
    for (const row of this.rows) {
      if (row.activo && (!row.aperturaInput || !row.cierreInput)) {
        this.error = `Completá apertura y cierre para ${row.nombre_dia}.`;
        this.cdr.markForCheck();
        return;
      }
      if (row.activo && row.aperturaInput >= row.cierreInput) {
        this.error = `En ${row.nombre_dia}, la apertura debe ser anterior al cierre.`;
        this.cdr.markForCheck();
        return;
      }
    }

    this.saving = true;
    this.error = null;
    this.success = null;
    this.api
      .putHorarios({
        horarios: this.rows.map((r) => ({
          dia_semana: r.dia_semana,
          activo: r.activo,
          hora_apertura: r.activo ? this.toApiTime(r.aperturaInput) : null,
          hora_cierre: r.activo ? this.toApiTime(r.cierreInput) : null,
        })),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (d) => {
          this.data = d;
          this.rows = d.horarios.map((h) => this.toRow(h));
          this.saving = false;
          this.success = 'Horarios guardados. La disponibilidad para emergencias usa esta franja (hora Bolivia).';
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.saving = false;
          this.error = this.msg(err, 'No se pudieron guardar los horarios.');
          this.cdr.markForCheck();
        },
      });
  }

  private toRow(h: TallerHorarioDiaDto): HorarioRow {
    return {
      ...h,
      aperturaInput: this.fromApiTime(h.hora_apertura) ?? '08:00',
      cierreInput: this.fromApiTime(h.hora_cierre) ?? '18:00',
    };
  }

  private fromApiTime(value: string | null): string | null {
    if (!value) return null;
    return value.slice(0, 5);
  }

  private toApiTime(value: string): string {
    return value.length === 5 ? `${value}:00` : value;
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
