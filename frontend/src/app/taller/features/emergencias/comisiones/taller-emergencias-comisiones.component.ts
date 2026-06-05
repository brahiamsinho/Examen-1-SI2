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
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import type { ComisionTallerDto, ResumenComisionesDto } from '../../../../core/models/taller-emergencias.models';

@Component({
  selector: 'app-taller-emergencias-comisiones',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './taller-emergencias-comisiones.component.html',
  styleUrl: './taller-emergencias-comisiones.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerEmergenciasComisionesComponent implements OnInit {
  private readonly api = inject(TallerEmergenciasApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  resumen: ResumenComisionesDto | null = null;
  rows: ComisionTallerDto[] = [];
  readonly loading = signal(true);
  error: string | null = null;

  ngOnInit(): void {
    this.loading.set(true);
    this.error = null;
    forkJoin({
      resumen: this.api.getResumenComisiones(),
      rows: this.api.listComisiones(),
    })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: ({ resumen, rows }) => {
          this.resumen = resumen;
          this.rows = rows;
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.resumen = null;
          this.rows = [];
          this.error = this.msg(err, 'No se pudieron cargar las comisiones.');
          this.cdr.markForCheck();
        },
      });
  }

  parseDecimal(s: string): number {
    const n = Number(s);
    return Number.isFinite(n) ? n : 0;
  }

  formatoMoneda(val: string | number, moneda?: string | null): string {
    const n = typeof val === 'string' ? this.parseDecimal(val) : val;
    const cur = moneda && moneda.length === 3 ? moneda : 'BOB';
    try {
      return new Intl.NumberFormat('es-BO', {
        style: 'currency',
        currency: cur,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(n);
    } catch {
      return new Intl.NumberFormat('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
    }
  }

  formatoMonedaResumen(val: string | number): string {
    const n = typeof val === 'string' ? this.parseDecimal(val) : val;
    return new Intl.NumberFormat('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
  }

  estadoUi(e: string): string {
    const m: Record<string, string> = {
      PENDIENTE: 'Pendiente',
      CALCULADA: 'Calculada',
      LIQUIDADA: 'Liquidada',
      ANULADA: 'Anulada',
    };
    return m[e] ?? e;
  }

  linkDetalle(c: ComisionTallerDto): string[] | null {
    if (c.bandeja_id == null) return null;
    return ['/taller/panel/emergencias/solicitudes', String(c.bandeja_id)];
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
