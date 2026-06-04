import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { PricingPlanDto, PricingPlanUpdatePayload } from '../../../core/models/admin-api.models';

@Component({
  selector: 'app-admin-planes-precios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './admin-planes-precios.component.html',
  styleUrl: './admin-planes-precios.component.scss',
})
export class AdminPlanesPreciosComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  plans: PricingPlanDto[] = [];
  loading = true;
  error: string | null = null;
  busy = false;
  modalEdit = false;
  selected: PricingPlanDto | null = null;
  benefitsText = '';
  editForm: PricingPlanUpdatePayload = {};

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading = true;
    this.api.listPricingPlans().subscribe({
      next: (rows) => {
        this.plans = rows.sort((a, b) => a.sort_order - b.sort_order);
        this.loading = false;
        this.error = null;
      },
      error: (err: HttpErrorResponse) => {
        this.loading = false;
        this.error =
          err.status === 403
            ? 'Solo superadmin de plataforma puede gestionar planes y precios.'
            : 'No se pudieron cargar los planes.';
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
  }

  closeModal(): void {
    this.modalEdit = false;
    this.selected = null;
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
    this.api.updatePricingPlan(this.selected.slug, payload).subscribe({
      next: (updated) => {
        this.plans = this.plans.map((p) => (p.slug === updated.slug ? updated : p));
        this.busy = false;
        this.closeModal();
      },
      error: (err: HttpErrorResponse) => {
        this.busy = false;
        this.error =
          typeof err.error?.detail === 'string'
            ? err.error.detail
            : 'No se pudo guardar el plan.';
      },
    });
  }
}
