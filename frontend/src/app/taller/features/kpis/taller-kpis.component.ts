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
import { finalize, timeout } from 'rxjs/operators';
import { TallerEmergenciasApiService } from '../../../core/services/taller-emergencias-api.service';
import type { ReporteTallerDashboardDto } from '../../../core/models/taller-emergencias.models';

function toIsoDateLocal(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

interface EstadoChip {
  label: string;
  n: number;
}

@Component({
  selector: 'app-taller-kpis',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-kpis.component.html',
  styleUrl: './taller-kpis.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerKpisComponent implements OnInit {
  private readonly emergenciasApi = inject(TallerEmergenciasApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  reporte: ReporteTallerDashboardDto | null = null;
  estadosReporte: EstadoChip[] = [];
  readonly loading = signal(true);
  error: string | null = null;
  permisoDenegado = false;

  desdeStr = '';
  hastaStr = '';

  ngOnInit(): void {
    const hasta = new Date();
    const desde = new Date();
    desde.setDate(desde.getDate() - 30);
    this.desdeStr = toIsoDateLocal(desde);
    this.hastaStr = toIsoDateLocal(hasta);
    this.cargarKpis();
  }

  cargarKpis(): void {
    this.loading.set(true);
    this.error = null;
    this.permisoDenegado = false;

    this.emergenciasApi
      .getReporteKpis({
        desde: this.desdeStr || undefined,
        hasta: this.hastaStr || undefined,
      })
      .pipe(
        timeout(25_000),
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (r) => {
          this.reporte = r;
          this.estadosReporte = this.estadoChipsDe(r);
          this.cdr.markForCheck();
        },
        error: (e: { status?: number }) => {
          if (e?.status === 403) {
            this.permisoDenegado = true;
            this.error = 'Tu rol no incluye permiso `reportes:leer` para ver KPIs del taller.';
          } else {
            this.error = 'No se pudieron cargar los KPIs. Revisá la conexión o intentá de nuevo.';
          }
          this.cdr.markForCheck();
        },
      });
  }

  parseDecimal(s: string): number {
    const n = Number(s);
    return Number.isFinite(n) ? n : 0;
  }

  formatoMoneda(val: string | number): string {
    const n = typeof val === 'string' ? this.parseDecimal(val) : val;
    return new Intl.NumberFormat('es-BO', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(n);
  }

  sinDatosEnPeriodo(): boolean {
    const r = this.reporte;
    if (!r) return false;
    const estados = Object.values(r.solicitudes_por_estado ?? {});
    const totalEstados = estados.reduce((a, b) => a + b, 0);
    const com = r.resumen_comisiones;
    const sinComision =
      this.parseDecimal(com.total_servicios) === 0 &&
      com.total_registros === 0 &&
      r.bandeja_pendientes === 0;
    return totalEstados === 0 && sinComision;
  }

  exportarCsv(): void {
    const r = this.reporte;
    if (!r) return;
    const rows: string[][] = [
      ['Métrica', 'Valor'],
      ['Ingreso neto taller', r.resumen_comisiones.total_neto],
      ['Comisión plataforma', r.resumen_comisiones.total_comision],
      ['Volumen servicios', r.resumen_comisiones.total_servicios],
      ['Ofertas pendientes bandeja', String(r.bandeja_pendientes)],
    ];
    for (const [estado, n] of Object.entries(r.solicitudes_por_estado ?? {})) {
      rows.push([`Estado ${estado}`, String(n)]);
    }
    rows.push([]);
    rows.push(['Ganancias por técnico']);
    rows.push(['Técnico', 'Comisiones', 'Facturado', 'Comisión plataf.', 'Neto taller']);
    for (const t of r.ganancias_por_tecnico) {
      rows.push([
        `${t.nombres} ${t.apellidos}`,
        String(t.comisiones_registradas),
        t.total_monto_servicio,
        t.total_monto_comision,
        t.total_monto_taller_neto,
      ]);
    }
    const csv = rows.map((row) => row.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kpis-taller-${this.desdeStr}_${this.hastaStr}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  private estadoChipsDe(r: ReporteTallerDashboardDto): EstadoChip[] {
    const order = [
      'REGISTRADA',
      'EN_REVISION',
      'TALLER_ASIGNADO',
      'TECNICO_ASIGNADO',
      'EN_CAMINO',
      'EN_ATENCION',
      'FINALIZADA',
      'CANCELADA',
    ];
    const map = r.solicitudes_por_estado ?? {};
    const labels: Record<string, string> = {
      REGISTRADA: 'Registrada',
      EN_REVISION: 'En revisión',
      TALLER_ASIGNADO: 'Taller asignado',
      TECNICO_ASIGNADO: 'Técnico asignado',
      EN_CAMINO: 'En camino',
      EN_ATENCION: 'En atención',
      FINALIZADA: 'Finalizada',
      CANCELADA: 'Cancelada',
    };
    const entries = Object.entries(map).filter(([, n]) => n > 0);
    entries.sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
    return entries.map(([k, n]) => ({ label: labels[k] ?? k, n }));
  }
}
