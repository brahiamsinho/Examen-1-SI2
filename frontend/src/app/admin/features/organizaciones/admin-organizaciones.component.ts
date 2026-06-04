import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type {
  PlanTenant,
  TenantCreatePayload,
  TenantDto,
  TenantUpdatePayload,
} from '../../../core/models/admin-api.models';

const TENANT_SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

@Component({
  selector: 'app-admin-organizaciones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-organizaciones.component.html',
  styleUrl: './admin-organizaciones.component.scss',
})
export class AdminOrganizacionesComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  tenants: TenantDto[] = [];
  loading = true;
  error: string | null = null;
  busy = false;
  modalCreate = false;
  modalEdit = false;
  selected: TenantDto | null = null;

  createForm: TenantCreatePayload = {
    slug: '',
    nombre: '',
    plan: 'STARTER',
  };

  editForm: TenantUpdatePayload = {};
  stripeCustomerId = '';

  readonly plans: PlanTenant[] = ['FREE', 'STARTER', 'PRO', 'ENTERPRISE'];

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading = true;
    this.api.listTenants().subscribe({
      next: (rows) => {
        this.tenants = rows;
        this.loading = false;
        this.error = null;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudieron cargar las organizaciones.';
      },
    });
  }

  closeModals(): void {
    this.modalCreate = false;
    this.modalEdit = false;
    this.selected = null;
  }

  openCreate(): void {
    this.createForm = { slug: '', nombre: '', plan: 'STARTER' };
    this.error = null;
    this.modalCreate = true;
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
      return;
    }
    if (!TENANT_SLUG_PATTERN.test(slug)) {
      this.error = 'Slug inválido: usa minúsculas, números y guiones (ej. mi-empresa).';
      return;
    }
    this.busy = true;
    this.error = null;
    const body: TenantCreatePayload = {
      slug,
      nombre,
      plan: this.createForm.plan,
    };
    this.api.createTenant(body).subscribe({
      next: () => {
        this.busy = false;
        this.closeModals();
        this.reload();
      },
      error: (err) => {
        this.busy = false;
        this.error = this.apiErrorMessage(err, 'No se pudo crear la organización.');
      },
    });
  }

  openEdit(t: TenantDto): void {
    this.selected = t;
    this.editForm = {
      nombre: t.nombre,
      estado: t.estado,
      plan: t.plan,
      dominio_custom: t.dominio_custom,
      subscription_status: t.subscription_status,
    };
    this.stripeCustomerId = t.stripe_customer_id ?? '';
    this.modalEdit = true;
  }

  openCheckout(t: TenantDto): void {
    const base = window.location.origin;
    this.api
      .createTenantCheckout(t.id, {
        success_url: `${base}/admin/panel/organizaciones?billing=ok`,
        cancel_url: `${base}/admin/panel/organizaciones?billing=cancel`,
      })
      .subscribe({
        next: (res) => {
          if (res.checkout_url) window.location.href = res.checkout_url;
        },
        error: () => {
          this.error = 'No se pudo abrir checkout Stripe (revisa STRIPE_SAAS_PRICE_STARTER en .env).';
        },
      });
  }

  openBillingPortal(t: TenantDto): void {
    this.api.createTenantBillingPortal(t.id, window.location.href).subscribe({
      next: (res) => {
        if (res.portal_url) window.location.href = res.portal_url;
      },
      error: () => {
        this.error = 'Portal de facturación no disponible (cliente Stripe requerido).';
      },
    });
  }

  submitEdit(): void {
    if (!this.selected) return;
    this.busy = true;
    this.api.updateTenant(this.selected.id, this.editForm).subscribe({
      next: () => {
        if (this.stripeCustomerId.trim()) {
          this.api.linkTenantStripeCustomer(this.selected!.id, this.stripeCustomerId.trim()).subscribe({
            next: () => {
              this.busy = false;
              this.closeModals();
              this.reload();
            },
            error: () => {
              this.busy = false;
              this.error = 'Organización actualizada; falló vincular Stripe.';
              this.reload();
            },
          });
          return;
        }
        this.busy = false;
        this.closeModals();
        this.reload();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo actualizar la organización.';
      },
    });
  }
}
