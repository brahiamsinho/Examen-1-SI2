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
  serieComisiones: AdminComisionSerieFila[] = [];
  desde = '';
  hasta = '';
  loadingCounts = true;
  loadingFinanzas = true;
  error: string | null = null;
  finanzasError: string | null = null;

  readonly quick = [
    { path: '/admin/panel/usuarios', label: 'Usuarios' },
    { path: '/admin/panel/roles', label: 'Roles' },
    { path: '/admin/panel/permisos', label: 'Permisos' },
    { path: '/admin/panel/talleres', label: 'Talleres' },
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

  totalComisionSerie(): number {
    return this.serieComisiones.reduce(
      (acc, x) => acc + this.toNumber(x.total_comision_plataforma),
      0,
    );
  }

  maxComisionSerie(): number {
    return this.serieComisiones.reduce((max, x) => {
      const value = this.toNumber(x.total_comision_plataforma);
      return value > max ? value : max;
    }, 0);
  }

  barWidthPercent(value: string): number {
    const max = this.maxComisionSerie();
    if (max <= 0) return 0;
    return Math.max(4, Math.round((this.toNumber(value) / max) * 100));
  }

  money(value: string | number | null | undefined): string {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(this.toNumber(value));
  }

  pct(value: string | number | null | undefined): string {
    return `${this.toNumber(value).toFixed(2)}%`;
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
            this.serieComisiones = reportes.serie_diaria ?? [];
          } else {
            this.finanzas = null;
            this.topTalleres = [];
            this.serieComisiones = [];
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

  private toNumber(value: string | number | null | undefined): number {
    if (typeof value === 'number') return value;
    if (!value) return 0;
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }
}
