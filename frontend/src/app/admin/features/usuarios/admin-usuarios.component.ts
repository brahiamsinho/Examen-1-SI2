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
import { FormsModule } from '@angular/forms';
import { distinctUntilChanged, forkJoin, skip } from 'rxjs';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { AdminTenantContextService } from '../../../core/services/admin-tenant-context.service';
import type {
  EstadoUsuario,
  RolDto,
  TenantDto,
  UsuarioCreatePayload,
  UsuarioListDto,
  UsuarioUpdatePayload,
} from '../../../core/models/admin-api.models';
import { filterRowsByQuery } from '../../../core/utils/list-filter.util';

@Component({
  selector: 'app-admin-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-usuarios.component.html',
  styleUrl: './admin-usuarios.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminUsuariosComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  readonly tenantCtx = inject(AdminTenantContextService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly usuarios = signal<UsuarioListDto[]>([]);
  readonly roles = signal<RolDto[]>([]);
  tenants: TenantDto[] = [];
  /** Organización en modal crear (superadmin, si no es cuenta plataforma). */
  createTenantId: number | null = null;
  /** Solo superadmin: alta sin tenant_id (admin global de plataforma). */
  createPlatformAccount = false;
  readonly search = signal('');
  readonly estado = signal<EstadoUsuario | ''>('');
  readonly rolFilter = signal('');
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  modalCreate = false;
  modalEdit = false;
  modalDetail = false;
  modalRoles = false;
  selected: UsuarioListDto | null = null;
  rolIds = new Set<number>();

  createForm: UsuarioCreatePayload = {
    nombres: '',
    apellidos: '',
    email: '',
    telefono: '',
    password: '',
    username: '',
    estado: 'ACTIVO',
  };

  editForm: UsuarioUpdatePayload = {};

  readonly estados: EstadoUsuario[] = ['ACTIVO', 'INACTIVO', 'BLOQUEADO', 'PENDIENTE'];

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

  readonly assignableRoles = computed(() =>
    this.roles().filter((r) => r.nombre !== 'CLIENTE'),
  );

  readonly rolesForFilter = this.assignableRoles;

  readonly filtered = computed(() => {
    let rows = this.usuarios();
    const estado = this.estado();
    if (estado) rows = rows.filter((u) => u.estado === estado);
    const rol = this.rolFilter();
    if (rol) rows = rows.filter((u) => (u.roles || []).includes(rol));
    return filterRowsByQuery(rows, this.search(), (u) => [
      u.email,
      u.nombres,
      u.apellidos,
      u.username,
    ]);
  });

  onPageTenantFilterChange(id: number | null): void {
    this.tenantCtx.setSelectedTenantId(id);
  }

  openCreateModal(): void {
    this.error = null;
    this.createTenantId = this.tenantCtx.selectedTenantId();
    if (this.tenantCtx.isPlatformSuperadmin() && this.createTenantId == null && this.tenants.length === 1) {
      this.createTenantId = this.tenants[0].id;
    }
    this.modalCreate = true;
  }

  reload(): void {
    this.loading.set(true);
    forkJoin({
      usuarios: this.api.listUsuarios(this.tenantCtx.tenantQueryParam()),
      roles: this.api.listRoles(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ usuarios, roles }) => {
          this.usuarios.set(usuarios);
          this.roles.set(roles);
          this.loading.set(false);
          this.error = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.loading.set(false);
          this.error = 'No se pudieron cargar los usuarios.';
          this.cdr.markForCheck();
        },
      });
  }

  openDetail(u: UsuarioListDto): void {
    this.selected = u;
    this.modalDetail = true;
  }

  openEdit(u: UsuarioListDto): void {
    this.selected = u;
    this.editForm = {
      nombres: u.nombres,
      apellidos: u.apellidos,
      telefono: u.telefono,
      username: u.username,
      estado: u.estado,
    };
    this.modalEdit = true;
  }

  saveEdit(): void {
    if (!this.selected) return;
    this.busy = true;
    this.api.updateUsuario(this.selected.id, this.editForm).subscribe({
      next: (u) => {
        const prevRoles = this.selected?.roles || [];
        this.usuarios.update((list) =>
          list.map((x) =>
            x.id === u.id ? { ...(u as UsuarioListDto), roles: prevRoles } : x,
          ),
        );
        this.closeModals();
        this.busy = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo actualizar el usuario.';
      },
    });
  }

  create(): void {
    if (!this.createForm.password || this.createForm.password.length < 4) {
      this.error = 'La contraseña debe tener al menos 4 caracteres.';
      return;
    }
    const body: UsuarioCreatePayload = { ...this.createForm };
    if (this.tenantCtx.isPlatformSuperadmin()) {
      if (this.createPlatformAccount) {
        delete body.tenant_id;
      } else {
        if (this.createTenantId == null) {
          this.error =
            'Selecciona la organización en el formulario o marca "Cuenta de plataforma (sin organización)".';
          return;
        }
        body.tenant_id = this.createTenantId;
      }
    }
    this.busy = true;
    this.api.createUsuario(body).subscribe({
      next: () => {
        this.modalCreate = false;
        this.busy = false;
        this.reload();
        this.createForm = {
          nombres: '',
          apellidos: '',
          email: '',
          telefono: '',
          password: '',
          username: '',
          estado: 'ACTIVO',
        };
        this.createPlatformAccount = false;
        this.createTenantId = null;
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo crear el usuario (email o teléfono duplicado).';
      },
    });
  }

  openRoles(u: UsuarioListDto): void {
    this.selected = u;
    const names = new Set(u.roles || []);
    this.rolIds = new Set(
      this.assignableRoles().filter((r) => names.has(r.nombre)).map((r) => r.id),
    );
    this.modalRoles = true;
  }

  toggleRol(id: number): void {
    if (this.rolIds.has(id)) this.rolIds.delete(id);
    else this.rolIds.add(id);
  }

  saveRoles(): void {
    if (!this.selected) return;
    this.busy = true;
    this.api.assignRoles(this.selected.id, [...this.rolIds]).subscribe({
      next: () => {
        this.modalRoles = false;
        this.busy = false;
        this.reload();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudieron asignar roles.';
      },
    });
  }

  setEstado(u: UsuarioListDto, estado: EstadoUsuario): void {
    this.busy = true;
    this.api.updateUsuario(u.id, { estado }).subscribe({
      next: (x) => {
        this.usuarios.update((list) =>
          list.map((row) => (row.id === x.id ? { ...x, roles: row.roles } : row)),
        );
        this.busy = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo cambiar el estado.';
      },
    });
  }

  deactivate(u: UsuarioListDto): void {
    if (!confirm(`¿Desactivar a ${u.email}?`)) return;
    this.busy = true;
    this.api.deleteUsuario(u.id).subscribe({
      next: () => {
        this.usuarios.update((list) => list.filter((x) => x.id !== u.id));
        this.busy = false;
        this.closeModals();
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo desactivar.';
      },
    });
  }

  closeModals(): void {
    this.modalCreate = this.modalEdit = this.modalDetail = this.modalRoles = false;
    this.selected = null;
    this.rolIds = new Set();
  }
}
