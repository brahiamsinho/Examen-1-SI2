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
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { TenantCreatePayload, TenantDto, TenantUpdatePayload } from '../../../core/models/admin-api.models';
import {
  commercialPlanDisplayName,
  commercialSlugToPlanTenant,
  DEFAULT_COMMERCIAL_PLANS,
  formatPlanPrice,
  planTenantToCommercialSlug,
  type CommercialPlanOption,
  type CommercialPlanSlug,
} from '../../../core/utils/saas-plan-tiers';

const TENANT_SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

@Component({
  selector: 'app-admin-organizaciones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-organizaciones.component.html',
  styleUrl: './admin-organizaciones.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminOrganizacionesComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly tenants = signal<TenantDto[]>([]);
  readonly loading = signal(true);
  readonly commercialPlans = signal<CommercialPlanOption[]>(DEFAULT_COMMERCIAL_PLANS);

  error: string | null = null;
  busy = false;
  modalCreate = false;
  modalEdit = false;
  selected: TenantDto | null = null;

  createForm = {
    slug: '',
    nombre: '',
    commercialPlanSlug: 'free' as CommercialPlanSlug,
  };

  editForm: TenantUpdatePayload = {};
  editCommercialPlanSlug: CommercialPlanSlug = 'free';
  stripeCustomerId = '';

  readonly planDisplayName = commercialPlanDisplayName;

  planDescription(slug: CommercialPlanSlug): string {
    return this.commercialPlans().find((p) => p.slug === slug)?.description ?? '';
  }

  ngOnInit(): void {
    this.loadCommercialPlans();
    this.reload();
  }

  private loadCommercialPlans(): void {
    this.api
      .listPricingPlans()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (rows) => {
          const sorted = [...rows].sort((a, b) => a.sort_order - b.sort_order);
          this.commercialPlans.set(
            sorted.map((p) => ({
              slug: p.slug as CommercialPlanSlug,
              name: p.name,
              priceLabel: formatPlanPrice(Number(p.price_monthly_bob), p.currency),
              description: p.description?.trim() || '',
            })),
          );
          this.cdr.markForCheck();
        },
        error: () => {
          this.commercialPlans.set(DEFAULT_COMMERCIAL_PLANS);
          this.cdr.markForCheck();
        },
      });
  }

  reload(force = false): void {
    if (force) {
      this.api.invalidateTenantsList();
    }
    this.loading.set(true);
    this.api
      .listTenants()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (rows) => {
          this.tenants.set(Array.isArray(rows) ? rows : []);
          this.error = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudieron cargar las organizaciones.';
          this.cdr.markForCheck();
        },
      });
  }

  closeModals(): void {
    this.modalCreate = false;
    this.modalEdit = false;
    this.selected = null;
    this.cdr.markForCheck();
  }

  openCreate(): void {
    this.createForm = { slug: '', nombre: '', commercialPlanSlug: 'free' };
    this.error = null;
    this.modalCreate = true;
    this.cdr.markForCheck();
  }

  private normalizeSlug(raw: string): string {
    return raw
      .trim()
      .toLowerCase()
      .replace(/[\s_]+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  private apiErrorMessage(err: unknown, fallback: string): string {
    if (!(err instanceof HttpErrorResponse)) {
      return fallback;
    }
    const detail = err.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      const msgs = detail
        .map((item: { msg?: string }) => item?.msg)
        .filter((msg): msg is string => Boolean(msg));
      if (msgs.length) {
        return msgs.join(' ');
      }
    }
    if (err.status === 409) {
      return 'Ese slug ya existe. Elige otro identificador único.';
    }
    if (err.status === 422) {
      return 'Revisa el slug: solo minúsculas, números y guiones (ej. mi-empresa).';
    }
    return fallback;
  }

  submitCreate(): void {
    const slug = this.normalizeSlug(this.createForm.slug);
    const nombre = this.createForm.nombre.trim();
    if (!slug || !nombre) {
      this.error = 'Slug y nombre son obligatorios.';
      this.cdr.markForCheck();
      return;
    }
    if (!TENANT_SLUG_PATTERN.test(slug)) {
      this.error = 'Slug inválido: usa minúsculas, números y guiones (ej. mi-empresa).';
      this.cdr.markForCheck();
      return;
    }
    this.busy = true;
    this.error = null;
    const body: TenantCreatePayload = {
      slug,
      nombre,
      plan: commercialSlugToPlanTenant(this.createForm.commercialPlanSlug),
    };
    this.api
      .createTenant(body)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.closeModals();
          this.reload(true);
        },
        error: (err) => {
          this.busy = false;
          this.error = this.apiErrorMessage(err, 'No se pudo crear la organización.');
          this.cdr.markForCheck();
        },
      });
  }

  openEdit(t: TenantDto): void {
    this.selected = t;
    this.editCommercialPlanSlug = planTenantToCommercialSlug(t.plan);
    this.editForm = {
      nombre: t.nombre,
      estado: t.estado,
      dominio_custom: t.dominio_custom,
      subscription_status: t.subscription_status,
    };
    this.stripeCustomerId = t.stripe_customer_id ?? '';
    this.modalEdit = true;
    this.cdr.markForCheck();
  }

  openCheckout(t: TenantDto): void {
    const base = window.location.origin;
    this.api
      .createTenantCheckout(t.id, {
        success_url: `${base}/admin/panel/organizaciones?billing=ok`,
        cancel_url: `${base}/admin/panel/organizaciones?billing=cancel`,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (res.checkout_url) window.location.href = res.checkout_url;
        },
        error: () => {
          this.error =
            'No se pudo abrir checkout Stripe (revisa STRIPE_SAAS_PRICE_STARTER en .env).';
          this.cdr.markForCheck();
        },
      });
  }

  openBillingPortal(t: TenantDto): void {
    this.api
      .createTenantBillingPortal(t.id, window.location.href)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          if (res.portal_url) window.location.href = res.portal_url;
        },
        error: () => {
          this.error = 'Portal de facturación no disponible (cliente Stripe requerido).';
          this.cdr.markForCheck();
        },
      });
  }

  submitEdit(): void {
    if (!this.selected) return;
    this.busy = true;
    const payload: TenantUpdatePayload = {
      ...this.editForm,
      plan: commercialSlugToPlanTenant(this.editCommercialPlanSlug),
    };
    this.api
      .updateTenant(this.selected.id, payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          if (this.stripeCustomerId.trim()) {
            this.api
              .linkTenantStripeCustomer(this.selected!.id, this.stripeCustomerId.trim())
              .pipe(takeUntilDestroyed(this.destroyRef))
              .subscribe({
                next: () => {
                  this.busy = false;
                  this.closeModals();
                  this.reload(true);
                },
                error: () => {
                  this.busy = false;
                  this.error = 'Organización actualizada; falló vincular Stripe.';
                  this.reload(true);
                },
              });
            return;
          }
          this.busy = false;
          this.closeModals();
          this.reload(true);
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo actualizar la organización.';
          this.cdr.markForCheck();
        },
      });
  }
}
