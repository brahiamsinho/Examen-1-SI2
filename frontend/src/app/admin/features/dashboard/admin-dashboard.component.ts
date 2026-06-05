import {
  booleanAttribute,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  input,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { of } from 'rxjs';
import { catchError, distinctUntilChanged, skip, timeout } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { AdminTenantContextService } from '../../../core/services/admin-tenant-context.service';
import type {
  AdminComisionSerieFila,
  AdminFinanzasResumen,
  BitacoraDto,
  TallerComisionFila,
} from '../../../core/models/admin-api.models';
import { formatMoneyBob, formatPct, toNumber } from '../../../core/utils/format-money.util';

export interface SerieComisionBarRow extends AdminComisionSerieFila {
  barWidthPct: number;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminDashboardComponent implements OnInit {
  /** Solo métricas financieras (ruta /admin/panel/finanzas); evita 4 APIs del resumen. */
  readonly finanzasOnly = input(false, { transform: booleanAttribute });

  private readonly api = inject(AdminApiService);
  private readonly tenantCtx = inject(AdminTenantContextService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  totalUsuarios = 0;
  totalTalleres = 0;
  totalRoles = 0;
  actividad: BitacoraDto[] = [];
  finanzas: AdminFinanzasResumen | null = null;
  topTalleres: TallerComisionFila[] = [];
  serieComisiones: SerieComisionBarRow[] = [];
  serieComisionTotal = 0;
  desde = '';
  hasta = '';
  loadingCounts = true;
  loadingFinanzas = true;
  error: string | null = null;
  finanzasError: string | null = null;

  readonly quick = [
    { path: '/admin/panel/talleres', label: 'Talleres' },
    { path: '/admin/panel/planes-precios', label: 'Planes y precios' },
    { path: '/admin/panel/organizaciones', label: 'Organizaciones' },
    { path: '/admin/panel/bitacora', label: 'Bitácora' },
  ] as const;

  ngOnInit(): void {
    const now = new Date();
    const prev = new Date();
    prev.setDate(now.getDate() - 30);
    this.desde = this.toDateInput(prev);
    this.hasta = this.toDateInput(now);

    if (this.finanzasOnly()) {
      this.loadingCounts = false;
      this.loadFinanzas();
    } else {
      this.loadPanelCounts();
    }

    this.tenantCtx.tenantChanges$
      .pipe(
        skip(1),
        distinctUntilChanged(),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe(() => {
        if (this.finanzasOnly()) {
          this.loadFinanzas();
        } else {
          this.loadPanelCounts();
        }
      });

    setTimeout(() => {
      if (this.loadingCounts) {
        this.loadingCounts = false;
        if (!this.error) {
          this.error = 'La carga de conteos tardó demasiado. Revisa Docker y recarga la página.';
        }
        this.cdr.markForCheck();
      }
    }, 25_000);
  }

  recargarFinanzas(): void {
    this.loadFinanzas();
  }

  money(value: string | number | null | undefined): string {
    return formatMoneyBob(value);
  }

  pct(value: string | number | null | undefined): string {
    return formatPct(value);
  }

  /** Conteos primero (rápido); finanzas después para que el usuario vea tarjetas sin esperar SQL pesado. */
  private loadPanelCounts(): void {
    this.loadingCounts = true;
    this.error = null;

    const tenant = this.tenantCtx.tenantQueryParam();
    this.api
      .getPanelOverview(tenant)
      .pipe(timeout(10_000), takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (overview) => {
          this.totalUsuarios = overview.total_usuarios;
          this.totalTalleres = overview.total_talleres;
          this.totalRoles = overview.total_roles;
          this.actividad = overview.actividad_reciente ?? [];
          this.loadingCounts = false;
          this.cdr.markForCheck();
          this.loadFinanzas();
        },
        error: () => {
          this.error =
            'No se pudieron cargar los conteos. ¿Reconstruiste el backend? (docker compose up -d --build backend)';
          this.loadingCounts = false;
          this.cdr.markForCheck();
          this.loadFinanzas();
        },
      });
  }

  private loadFinanzas(): void {
    this.loadingFinanzas = true;
    this.finanzasError = null;
    const filters = { ...this.dateFilters(), ...this.tenantCtx.tenantQueryParam() };

    this.api
      .getFinanzasReportes(filters)
      .pipe(timeout(20_000), catchError(() => of(null)), takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (reportes) => {
          if (reportes?.resumen) {
            this.finanzas = reportes.resumen;
            this.topTalleres = reportes.top_talleres ?? [];
            this.applySerieChart(reportes.serie_diaria ?? []);
          } else {
            this.finanzas = null;
            this.topTalleres = [];
            this.applySerieChart([]);
            this.finanzasError = 'No se pudieron cargar las métricas financieras.';
          }
          this.loadingFinanzas = false;
          this.cdr.markForCheck();
        },
        error: () => {
          this.finanzasError = 'No se pudieron cargar las métricas financieras.';
          this.loadingFinanzas = false;
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
      const barWidthPct =
        max <= 0 ? 0 : Math.max(4, Math.round((value / max) * 100));
      return { ...row, barWidthPct };
    });
  }
}
