import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { TallerApiService } from '../../../../core/services/taller-api.service';
import {
  PublicApiService,
  PublicTenantOption,
} from '../../../../core/services/public-api.service';
import { TenantSlugService } from '../../../../core/services/tenant-slug.service';

function passwordsMatch(c: AbstractControl): ValidationErrors | null {
  const p = c.get('password')?.value;
  const c2 = c.get('password2')?.value;
  if (!p || !c2) return null;
  return p === c2 ? null : { mismatch: true };
}

@Component({
  selector: 'app-taller-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './taller-register.component.html',
  styleUrl: './taller-register.component.scss',
})
export class TallerRegisterComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(TallerApiService);
  private readonly publicApi = inject(PublicApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly tenantSlug = inject(TenantSlugService);

  tenants: PublicTenantOption[] = [];
  loadingTenants = true;
  registeredOrgSlug: string | null = null;

  readonly form = this.fb.nonNullable.group(
    {
      orgSlug: ['', Validators.required],
      nombre_comercial: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required, Validators.minLength(5)]],
      direccion: ['', [Validators.required]],
      ciudad: ['', [Validators.required]],
      descripcion: [''],
      responsable_nombre_completo: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(4)]],
      password2: ['', [Validators.required]],
      terms: [false, Validators.requiredTrue],
    },
    { validators: passwordsMatch },
  );

  submitting = false;
  success = false;
  errorMsg: string | null = null;
  showPassword = false;
  pendienteVerificacion = false;
  readonly mailhogWebUrl = environment.mailhogWebUrl;

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
    return tenants.length > 0 ? tenants[0].slug : preferred ?? stored;
  }

  loginQuery(): { org?: string } {
    const slug = this.registeredOrgSlug ?? this.form.controls.orgSlug.value?.trim();
    return slug ? { org: slug } : {};
  }

  submit(): void {
    this.errorMsg = null;
    this.success = false;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    this.tenantSlug.set(v.orgSlug);
    this.submitting = true;
    this.api
      .registro({
        tenant_slug: v.orgSlug.trim().toLowerCase(),
        nombre_comercial: v.nombre_comercial.trim(),
        email: v.email.trim(),
        telefono: v.telefono.trim(),
        direccion: v.direccion.trim(),
        ciudad: v.ciudad.trim(),
        descripcion: v.descripcion?.trim() || null,
        responsable_nombre_completo: v.responsable_nombre_completo.trim(),
        password: v.password,
      })
      .subscribe({
        next: (dto) => {
          this.submitting = false;
          this.success = true;
          this.registeredOrgSlug = v.orgSlug.trim().toLowerCase();
          this.pendienteVerificacion = dto.pendiente_verificacion_email !== false;
        },
        error: (err: unknown) => {
          this.submitting = false;
          if (err instanceof HttpErrorResponse) {
            const d = err.error?.detail;
            if (typeof d === 'string') {
              this.errorMsg = d;
              return;
            }
          }
          this.errorMsg = 'No se pudo completar el registro.';
        },
      });
  }
}
