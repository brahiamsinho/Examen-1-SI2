import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { TallerAuthService, TallerAuthError } from '../../../../core/services/taller-auth.service';
import {
  PublicApiService,
  PublicTenantOption,
} from '../../../../core/services/public-api.service';
import { TenantSlugService } from '../../../../core/services/tenant-slug.service';

@Component({
  selector: 'app-taller-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './taller-login.component.html',
  styleUrl: './taller-login.component.scss',
})
export class TallerLoginComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(TallerAuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly tenantSlug = inject(TenantSlugService);
  private readonly publicApi = inject(PublicApiService);

  tenants: PublicTenantOption[] = [];
  loadingTenants = true;

  readonly form = this.fb.nonNullable.group({
    orgSlug: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(1)]],
    remember: [false],
  });

  showPassword = false;
  submitting = false;
  errorMsg: string | null = null;

  ngOnInit(): void {
    const org = this.route.snapshot.queryParamMap.get('org');
    const preferred = this.tenantSlug.resolveFromQueryParam(org);
    this.form.controls.orgSlug.disable();

    this.publicApi.listActiveTenants().subscribe({
      next: (tenants) => {
        this.tenants = tenants;
        this.loadingTenants = false;
        const slug = this.resolveOrgSlug(preferred, tenants);
        if (slug) {
          this.form.patchValue({ orgSlug: slug });
        }
        if (tenants.length === 0) {
          this.form.controls.orgSlug.disable();
        } else {
          this.form.controls.orgSlug.enable();
        }
      },
      error: () => {
        this.loadingTenants = false;
        if (preferred) {
          this.form.patchValue({ orgSlug: preferred });
          this.form.controls.orgSlug.enable();
        } else {
          this.form.controls.orgSlug.disable();
        }
      },
    });
  }

  tenantLabel(t: PublicTenantOption): string {
    return `${t.nombre} (${t.slug})`;
  }

  private resolveOrgSlug(
    preferred: string | null,
    tenants: PublicTenantOption[],
  ): string | null {
    if (preferred && tenants.some((t) => t.slug === preferred)) {
      return preferred;
    }
    const stored = this.tenantSlug.get();
    if (stored && tenants.some((t) => t.slug === stored)) {
      return stored;
    }
    if (tenants.length > 0) {
      return tenants[0].slug;
    }
    return preferred ?? stored;
  }

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  submit(): void {
    this.errorMsg = null;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const { email, password, remember, orgSlug } = this.form.getRawValue();
    this.tenantSlug.set(orgSlug);
    this.submitting = true;
    this.auth.login(email.trim(), password, remember, orgSlug).subscribe({
      next: () => {
        this.submitting = false;
        void this.router.navigate(['/taller/panel']);
      },
      error: (err: unknown) => {
        this.submitting = false;
        this.errorMsg = this.formatError(err);
      },
    });
  }

  private formatError(err: unknown): string {
    if (err instanceof TallerAuthError) {
      return err.message;
    }
    if (err instanceof HttpErrorResponse) {
      const d = err.error?.detail;
      if (typeof d === 'string') return d;
      if (Array.isArray(d) && d[0]?.msg) return d.map((x: { msg: string }) => x.msg).join(' ');
    }
    return 'No se pudo iniciar sesión. Intenta de nuevo.';
  }
}
