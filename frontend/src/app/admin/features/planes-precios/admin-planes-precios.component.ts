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
import { RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { PricingPlanDto, PricingPlanUpdatePayload } from '../../../core/models/admin-api.models';

@Component({
  selector: 'app-admin-planes-precios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-planes-precios.component.html',
  styleUrl: './admin-planes-precios.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminPlanesPreciosComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly plans = signal<PricingPlanDto[]>([]);
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;
  modalEdit = false;
  selected: PricingPlanDto | null = null;
  benefitsText = '';
  editForm: PricingPlanUpdatePayload = {};

  ngOnInit(): void {
    this.reload();
  }

  reload(force = false): void {
    if (force) {
      this.api.invalidatePricingPlansList();
    }
    this.loading.set(true);
    this.api
      .listPricingPlans()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (rows) => {
          const sorted = (Array.isArray(rows) ? rows : []).sort((a, b) => a.sort_order - b.sort_order);
          this.plans.set(sorted);
          this.error = null;
          this.cdr.markForCheck();
        },
        error: (err: HttpErrorResponse) => {
          this.error =
            err.status === 403
              ? 'Solo superadmin de plataforma puede gestionar planes y precios.'
              : 'No se pudieron cargar los planes.';
          this.cdr.markForCheck();
        },
      });
  }

  stripeStatus(plan: PricingPlanDto): 'free' | 'ready' | 'missing' {
    if (!plan.price_monthly_bob || plan.price_monthly_bob <= 0) return 'free';
    return plan.stripe_price_id?.trim() ? 'ready' : 'missing';
  }

  openEdit(plan: PricingPlanDto): void {
    this.selected = plan;
    this.benefitsText = plan.benefits.join('\n');
    this.editForm = {
      name: plan.name,
      description: plan.description,
      price_monthly_bob: plan.price_monthly_bob,
      currency: plan.currency,
      featured: plan.featured,
      badge: plan.badge,
      cta_label: plan.cta_label,
      cta_router_link: plan.cta_router_link,
      cta_href: plan.cta_href,
      stripe_price_id: plan.stripe_price_id,
      sort_order: plan.sort_order,
      active: plan.active,
    };
    this.modalEdit = true;
    this.error = null;
    this.cdr.markForCheck();
  }

  closeModal(): void {
    this.modalEdit = false;
    this.selected = null;
    this.cdr.markForCheck();
  }

  save(): void {
    if (!this.selected || this.busy) return;
    const payload: PricingPlanUpdatePayload = {
      ...this.editForm,
      benefits: this.benefitsText
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean),
    };
    this.busy = true;
    this.api
      .updatePricingPlan(this.selected.slug, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          this.plans.update((list) =>
            list.map((p) => (p.slug === updated.slug ? updated : p)).sort((a, b) => a.sort_order - b.sort_order),
          );
          this.busy = false;
          this.closeModal();
          this.cdr.markForCheck();
        },
        error: (err: HttpErrorResponse) => {
          this.busy = false;
          this.error =
            typeof err.error?.detail === 'string'
              ? err.error.detail
              : 'No se pudo guardar el plan.';
          this.cdr.markForCheck();
        },
      });
  }
}
