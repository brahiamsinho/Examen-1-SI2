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
import { distinctUntilChanged, skip, timeout } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { AdminTenantContextService } from '../../../core/services/admin-tenant-context.service';
import type {
  AdminComisionSerieFila,
  AdminKpisDto,
  TallerComisionFila,
} from '../../../core/models/admin-api.models';
import { formatMoneyBob, formatPct, toNumber } from '../../../core/utils/format-money.util';

export interface SerieComisionBarRow extends AdminComisionSerieFila {
  barWidthPct: number;
}

interface EstadoChip {
  label: string;
  n: number;
}

@Component({
  selector: 'app-admin-kpis',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-kpis.component.html',
  styleUrl: './admin-kpis.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminKpisComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly tenantCtx = inject(AdminTenantContextService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  kpis: AdminKpisDto | null = null;
  topTalleres: TallerComisionFila[] = [];
  serieComisiones: SerieComisionBarRow[] = [];
  serieComisionTotal = 0;
  estadosOperativos: EstadoChip[] = [];

  desde = '';
  hasta = '';
  loading = true;
  error: string | null = null;
  permisoDenegado = false;

  ngOnInit(): void {
    const now = new Date();
    const prev = new Date();
    prev.setDate(now.getDate() - 30);
    this.desde = this.toDateInput(prev);
    this.hasta = this.toDateInput(now);

    this.cargarKpis();

    this.tenantCtx.tenantChanges$
      .pipe(skip(1), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.cargarKpis());
  }

  recargar(): void {
    this.cargarKpis();
  }

  money(value: string | number | null | undefined): string {
    return formatMoneyBob(value);
  }

  pct(value: string | number | null | undefined): string {
    return formatPct(value);
  }

  tiempoAtencion(min: number | null | undefined): string {
    if (min == null) return '—';
    if (min < 60) return `${min.toFixed(0)} min`;
    const h = Math.floor(min / 60);
    const m = Math.round(min % 60);
    return m > 0 ? `${h} h ${m} min` : `${h} h`;
  }

  pctSla(value: number | null | undefined): string {
    if (value == null) return '—';
    return `${value.toFixed(1)}%`;
  }

  exportarCsv(): void {
    if (!this.kpis) return;
    const rows: string[][] = [
      ['Métrica', 'Valor'],
      ['Total solicitudes', String(this.kpis.total_solicitudes)],
      ['Solicitudes activas', String(this.kpis.solicitudes_activas)],
      ['Solicitudes finalizadas', String(this.kpis.solicitudes_finalizadas)],
      ['Solicitudes canceladas', String(this.kpis.solicitudes_canceladas)],
      ['Pagos confirmados', String(this.kpis.pagos_confirmados)],
      ['Monto pagos BOB', this.kpis.monto_pagos_bob],
      [
        'Tiempo promedio atención (min)',
        this.kpis.tiempo_promedio_atencion_min != null
          ? String(this.kpis.tiempo_promedio_atencion_min)
          : '',
      ],
    ];
    for (const [estado, n] of Object.entries(this.kpis.solicitudes_por_estado ?? {})) {
      rows.push([`Estado ${estado}`, String(n)]);
    }
    const op = this.kpis.analitica_operacional;
    if (op) {
      rows.push([]);
      rows.push(['Analítica operacional §3']);
      rows.push(['Tiempo prom. asignación (min)', op.tiempo_promedio_asignacion_min != null ? String(op.tiempo_promedio_asignacion_min) : '']);
      rows.push(['Tiempo prom. llegada (min)', op.tiempo_promedio_llegada_min != null ? String(op.tiempo_promedio_llegada_min) : '']);
      rows.push(['Casos cancelados', String(op.casos_cancelados)]);
      rows.push(['Casos no atendidos', String(op.casos_no_atendidos)]);
      rows.push([
        'SLA cumplimiento (%)',
        op.sla?.porcentaje_cumplimiento != null ? String(op.sla.porcentaje_cumplimiento) : '',
      ]);
      rows.push([]);
      rows.push(['Incidentes por tipo', 'Total']);
      for (const it of op.incidentes_por_tipo ?? []) {
        rows.push([it.label, String(it.total)]);
      }
      rows.push([]);
      rows.push(['Top talleres eficientes', 'Finalizadas', 'Respuesta (min)', 'Finalización (min)']);
      for (const t of op.talleres_mas_eficientes ?? []) {
        rows.push([
          t.nombre_comercial,
          String(t.solicitudes_finalizadas),
          t.tiempo_respuesta_prom_min != null ? String(t.tiempo_respuesta_prom_min) : '',
          t.tiempo_finalizacion_prom_min != null ? String(t.tiempo_finalizacion_prom_min) : '',
        ]);
      }
      rows.push([]);
      rows.push(['Zonas con más incidentes', 'Total', 'Lat', 'Lng']);
      for (const z of op.zonas_mas_incidentes ?? []) {
        rows.push([
          z.zona,
          String(z.total),
          z.latitud_prom != null ? String(z.latitud_prom) : '',
          z.longitud_prom != null ? String(z.longitud_prom) : '',
        ]);
      }
    }
    rows.push([]);
    rows.push(['Top talleres']);
    rows.push(['Taller', 'Servicios', 'Monto servicio', 'Comisión plataforma', 'Neto taller']);
    for (const t of this.topTalleres) {
      rows.push([
        t.nombre_comercial,
        String(t.n_comisiones),
        t.total_monto_servicio,
        t.total_comision_plataforma,
        t.total_neto_taller,
      ]);
    }
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kpis-admin-${this.desde}_${this.hasta}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  private cargarKpis(): void {
    this.loading = true;
    this.error = null;
    this.permisoDenegado = false;

    const filters = { ...this.dateFilters(), ...this.tenantCtx.tenantQueryParam() };

    this.api
      .getPanelKpis(filters)
      .pipe(timeout(25_000), takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.kpis = data;
          this.topTalleres = data.top_talleres ?? [];
          this.applySerieChart(data.serie_diaria ?? []);
          this.estadosOperativos = this.estadoChipsDe(data.solicitudes_por_estado ?? {});
          this.loading = false;
          this.cdr.markForCheck();
        },
        error: (e: { status?: number }) => {
          this.loading = false;
          if (e?.status === 403) {
            this.permisoDenegado = true;
            this.error =
              'Tu rol no incluye permiso `reportes:leer` para ver el dashboard de KPIs.';
          } else {
            this.error =
              'No se pudieron cargar los KPIs. Revisa la conexión o intenta de nuevo.';
          }
          this.cdr.markForCheck();
        },
      });
  }

  private dateFilters(): { desde?: string; hasta?: string } {
    const filters: { desde?: string; hasta?: string } = {};
    if (this.desde) filters.desde = `${this.desde}T00:00:00`;
    if (this.hasta) filters.hasta = `${this.hasta}T23:59:59`;
    return filters;
  }

  private toDateInput(date: Date): string {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  private applySerieChart(rows: AdminComisionSerieFila[]): void {
    let max = 0;
    let total = 0;
    for (const row of rows) {
      const value = toNumber(row.total_comision_plataforma);
      total += value;
      if (value > max) max = value;
    }
    this.serieComisionTotal = total;
    this.serieComisiones = rows.map((row) => {
      const value = toNumber(row.total_comision_plataforma);
      const barWidthPct = max <= 0 ? 0 : Math.max(4, Math.round((value / max) * 100));
      return { ...row, barWidthPct };
    });
  }

  private estadoChipsDe(map: Record<string, number>): EstadoChip[] {
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
