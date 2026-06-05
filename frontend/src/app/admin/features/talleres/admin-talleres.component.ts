import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  computed,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { distinctUntilChanged, skip } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { AdminAuthService } from '../../../core/services/admin-auth.service';
import { AdminTenantContextService } from '../../../core/services/admin-tenant-context.service';
import type {
  EstadoTaller,
  TenantDto,
  TallerDto,
  TallerProvisionDto,
  TallerProvisionPayload,
  TallerUpdatePayload,
} from '../../../core/models/admin-api.models';
import { filterRowsByQuery } from '../../../core/utils/list-filter.util';

@Component({
  selector: 'app-admin-talleres',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-talleres.component.html',
  styleUrl: './admin-talleres.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminTalleresComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly auth = inject(AdminAuthService);
  readonly tenantCtx = inject(AdminTenantContextService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly talleres = signal<TallerDto[]>([]);
  tenants: TenantDto[] = [];
  createTenantId: number | null = null;
  readonly search = signal('');
  readonly estado = signal<EstadoTaller | ''>('');
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  detail: TallerDto | null = null;
  modalEdit = false;
  modalCreate = false;
  provisionResult: TallerProvisionDto | null = null;
  editId: number | null = null;
  editForm: TallerUpdatePayload = {};
  provisionForm: TallerProvisionPayload = {
    nombre_comercial: '',
    telefono_contacto: '',
    email_contacto: '',
    direccion: '',
    ciudad: '',
    descripcion: '',
    estado: 'ACTIVO',
    responsable_nombre_completo: '',
    responsable_email: '',
    responsable_telefono: '',
    responsable_password: '',
  };
  provisionPassword2 = '';

  readonly estados: EstadoTaller[] = ['PENDIENTE', 'ACTIVO', 'SUSPENDIDO', 'INACTIVO'];

  get createTenantSlug(): string | null {
    const t = this.tenantCtx.tenantById(this.tenants, this.createTenantId);
    return t?.slug ?? null;
  }

  ngOnInit(): void {
    if (this.tenantCtx.isPlatformSuperadmin()) {
      this.api
        .listTenants()
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({ next: (rows) => (this.tenants = rows) });
    }
    this.reload();
    this.tenantCtx.tenantChanges$
      .pipe(skip(1), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.reload());
  }

  onPageTenantFilterChange(id: number | null): void {
    this.tenantCtx.setSelectedTenantId(id);
  }

  readonly filtered = computed(() => {
    let rows = this.talleres();
    const estado = this.estado();
    if (estado) rows = rows.filter((t) => t.estado === estado);
    return filterRowsByQuery(rows, this.search(), (t) => [
      t.nombre_comercial,
      t.ciudad,
      t.email_contacto,
    ]);
  });

  reload(): void {
    this.loading.set(true);
    this.error = null;
    this.cdr.markForCheck();
    const tq = this.tenantCtx.tenantQueryParam();
    this.api
      .listTalleres(tq)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (talleres) => {
          this.talleres.set(talleres);
          this.loading.set(false);
          this.error = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.loading.set(false);
          this.error = 'No se pudieron cargar los talleres.';
          this.cdr.markForCheck();
        },
      });
  }

  private resolveCreateTenantId(): number | null {
    if (!this.tenantCtx.isPlatformSuperadmin()) {
      return this.auth.getMe()?.tenant_id ?? null;
    }
    return this.createTenantId;
  }

  openDetail(t: TallerDto): void {
    this.detail = t;
  }

  openCreateModal(): void {
    this.error = null;
    this.provisionResult = null;
    this.provisionPassword2 = '';
    this.createTenantId = this.tenantCtx.selectedTenantId();
    if (this.tenantCtx.isPlatformSuperadmin() && this.createTenantId == null && this.tenants.length === 1) {
      this.createTenantId = this.tenants[0].id;
    }
    this.provisionForm = {
      nombre_comercial: '',
      telefono_contacto: '',
      email_contacto: '',
      direccion: '',
      ciudad: '',
      descripcion: '',
      estado: 'ACTIVO',
      responsable_nombre_completo: '',
      responsable_email: '',
      responsable_telefono: '',
      responsable_password: '',
    };
    this.modalCreate = true;
    this.cdr.markForCheck();
  }

  copyContactFromResponsable(): void {
    if (this.provisionForm.responsable_email) {
      this.provisionForm.email_contacto = this.provisionForm.responsable_email;
    }
    if (this.provisionForm.responsable_telefono) {
      this.provisionForm.telefono_contacto = this.provisionForm.responsable_telefono;
    }
    this.cdr.markForCheck();
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
        .map((item: { msg?: string; loc?: (string | number)[] }) => {
          const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null;
          const label =
            field === 'telefono_contacto'
              ? 'Teléfono contacto del taller'
              : field === 'responsable_telefono'
                ? 'Teléfono del responsable'
                : field === 'responsable_email'
                  ? 'Email del responsable'
                  : field === 'email_contacto'
                    ? 'Email contacto del taller'
                    : null;
          if (label && item?.msg) {
            return `${label}: ${item.msg}`;
          }
          return item?.msg ?? '';
        })
        .filter((msg): msg is string => Boolean(msg));
      if (msgs.length) {
        return msgs.join(' ');
      }
    }
    if (err.status === 409) {
      return 'Ese email o teléfono ya está registrado en la organización. Usa otros datos o edita el usuario existente.';
    }
    return fallback;
  }

  private normalizeProvisionContact(): void {
    const tel = this.provisionForm.telefono_contacto.trim();
    const rtel = this.provisionForm.responsable_telefono.trim();
    if (tel.length < 5 && rtel.length >= 5) {
      this.provisionForm.telefono_contacto = rtel;
    }
    if (!this.provisionForm.email_contacto.trim() && this.provisionForm.responsable_email.trim()) {
      this.provisionForm.email_contacto = this.provisionForm.responsable_email.trim();
    }
  }

  openEdit(t: TallerDto): void {
    this.editId = t.id;
    this.editForm = {
      nombre_comercial: t.nombre_comercial,
      telefono_contacto: t.telefono_contacto,
      email_contacto: t.email_contacto,
      direccion: t.direccion,
      ciudad: t.ciudad,
      descripcion: t.descripcion ?? '',
      estado: t.estado,
    };
    this.modalEdit = true;
  }

  saveEdit(): void {
    if (this.editId == null) return;
    this.busy = true;
    this.api.updateTaller(this.editId, this.editForm).subscribe({
      next: (t) => {
        this.talleres.update((list) => list.map((x) => (x.id === t.id ? t : x)));
        this.modalEdit = false;
        this.busy = false;
        this.detail = null;
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo actualizar el taller.';
        this.cdr.markForCheck();
      },
    });
  }

  provision(): void {
    const tid = this.resolveCreateTenantId();
    if (tid == null) {
      this.error = 'Selecciona la organización en el formulario.';
      return;
    }
    if (!this.provisionForm.responsable_password || this.provisionForm.responsable_password.length < 4) {
      this.error = 'La contraseña debe tener al menos 4 caracteres.';
      return;
    }
    if (this.provisionForm.responsable_password !== this.provisionPassword2) {
      this.error = 'Las contraseñas no coinciden.';
      return;
    }
    if (!this.provisionForm.nombre_comercial.trim() || !this.provisionForm.responsable_nombre_completo.trim()) {
      this.error = 'Completa nombre del taller y del responsable.';
      return;
    }
    this.normalizeProvisionContact();
    if (this.provisionForm.telefono_contacto.trim().length < 5) {
      this.error = 'El teléfono de contacto del taller debe tener al menos 5 caracteres (o usa el del responsable).';
      return;
    }
    if (this.provisionForm.responsable_telefono.trim().length < 5) {
      this.error = 'El teléfono del responsable debe tener al menos 5 caracteres.';
      return;
    }
    if (!this.provisionForm.responsable_email.trim() || !this.provisionForm.email_contacto.trim()) {
      this.error = 'Completa el email de contacto y el email de login del responsable.';
      return;
    }
    const payload: TallerProvisionPayload = { ...this.provisionForm, tenant_id: tid };
    this.busy = true;
    this.error = null;
    this.api.provisionTaller(payload).subscribe({
      next: (result) => {
        this.talleres.update((list) => [...list, result]);
        this.provisionResult = result;
        this.busy = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.busy = false;
        this.error = this.apiErrorMessage(
          err,
          'No se pudo crear el taller. Revisa organización, datos obligatorios o email/teléfono duplicados.',
        );
        this.cdr.markForCheck();
      },
    });
  }

  setEstado(t: TallerDto, estado: EstadoTaller): void {
    this.busy = true;
    this.api.updateTaller(t.id, { estado }).subscribe({
      next: (u) => {
        this.talleres.update((list) => list.map((x) => (x.id === u.id ? u : x)));
        this.busy = false;
        if (this.detail?.id === u.id) this.detail = u;
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo cambiar el estado.';
        this.cdr.markForCheck();
      },
    });
  }

  closeModals(): void {
    const wasCreate = this.modalCreate;
    this.detail = null;
    this.modalEdit = false;
    this.modalCreate = false;
    this.provisionResult = null;
    this.editId = null;
    if (wasCreate) {
      this.reload();
    }
  }
}
