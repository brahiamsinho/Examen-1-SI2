import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import { TallerAuthService } from '../../../../core/services/taller-auth.service';
import type {
  EstadoUsuario,
  RolDto,
  UsuarioCreatePayload,
  UsuarioListDto,
  UsuarioUpdatePayload,
} from '../../../../core/models/admin-api.models';
import { filterRowsByQuery } from '../../../../core/utils/list-filter.util';

const ROLES_ASIGNABLES = new Set(['TECNICO', 'TALLER_RESPONSABLE']);

@Component({
  selector: 'app-taller-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-usuarios.component.html',
  styleUrl: './taller-usuarios.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerUsuariosComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  readonly auth = inject(TallerAuthService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly usuarios = signal<UsuarioListDto[]>([]);
  readonly roles = signal<RolDto[]>([]);
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

  readonly assignableRoles = computed(() =>
    this.roles().filter((r) => ROLES_ASIGNABLES.has(r.nombre)),
  );

  readonly rolesForFilter = this.assignableRoles;

  readonly filtered = computed(() => {
    let rows = this.usuarios();
    const estado = this.estado();
    if (estado) rows = rows.filter((u) => u.estado === estado);
    const rol = this.rolFilter();
    if (rol) rows = rows.filter((u) => (u.roles || []).includes(rol));
    return filterRowsByQuery(rows, this.search(), (u) => [u.email, u.nombres, u.apellidos]);
  });

  ngOnInit(): void {
    this.reload();
  }

  get puedeCrear(): boolean {
    return this.auth.tienePermiso('usuarios:crear');
  }

  get puedeEditar(): boolean {
    return this.auth.tienePermiso('usuarios:actualizar');
  }

  get puedeEliminar(): boolean {
    return this.auth.tienePermiso('usuarios:eliminar');
  }

  esYo(u: UsuarioListDto): boolean {
    return this.auth.getMe()?.id === u.id;
  }

  reload(): void {
    this.loading.set(true);
    forkJoin({
      usuarios: this.api.listUsuarios(),
      roles: this.api.listRoles(),
    }).subscribe({
      next: ({ usuarios, roles }) => {
        this.usuarios.set(usuarios);
        this.roles.set(roles);
        this.loading.set(false);
        this.error = null;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading.set(false);
        this.error = 'No se pudieron cargar los usuarios de tu organización.';
        this.cdr.markForCheck();
      },
    });
  }

  openCreateModal(): void {
    this.error = null;
    this.modalCreate = true;
    this.cdr.markForCheck();
  }

  openDetail(u: UsuarioListDto): void {
    this.selected = u;
    this.modalDetail = true;
    this.cdr.markForCheck();
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
    this.cdr.markForCheck();
  }

  saveEdit(): void {
    if (!this.selected || !this.puedeEditar) return;
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
        this.cdr.markForCheck();
      },
    });
  }

  create(): void {
    if (!this.puedeCrear) return;
    if (!this.createForm.password || this.createForm.password.length < 4) {
      this.error = 'La contraseña debe tener al menos 4 caracteres.';
      this.cdr.markForCheck();
      return;
    }
    this.busy = true;
    this.api.createUsuario({ ...this.createForm }).subscribe({
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
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo crear el usuario (email o teléfono duplicado).';
        this.cdr.markForCheck();
      },
    });
  }

  openRoles(u: UsuarioListDto): void {
    if (!this.puedeEditar) return;
    this.selected = u;
    const names = new Set(u.roles || []);
    this.rolIds = new Set(
      this.assignableRoles().filter((r) => names.has(r.nombre)).map((r) => r.id),
    );
    this.modalRoles = true;
    this.cdr.markForCheck();
  }

  toggleRol(id: number): void {
    if (this.rolIds.has(id)) this.rolIds.delete(id);
    else this.rolIds.add(id);
  }

  saveRoles(): void {
    if (!this.selected || !this.puedeEditar) return;
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
        this.cdr.markForCheck();
      },
    });
  }

  closeModals(): void {
    this.modalCreate = this.modalEdit = this.modalDetail = this.modalRoles = false;
    this.selected = null;
    this.rolIds = new Set();
    this.cdr.markForCheck();
  }

  desactivar(u: UsuarioListDto): void {
    if (!this.puedeEliminar || this.esYo(u)) return;
    if (!confirm(`¿Desactivar la cuenta de ${u.email}? No podrá iniciar sesión.`)) return;
    this.busy = true;
    this.api.desactivarUsuario(u.id).subscribe({
      next: () => {
        this.busy = false;
        this.reload();
        this.closeModals();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.busy = false;
        const msg = err?.error?.detail;
        this.error = typeof msg === 'string' ? msg : 'No se pudo desactivar el usuario.';
        this.cdr.markForCheck();
      },
    });
  }

  activar(u: UsuarioListDto): void {
    if (!this.puedeEditar || this.esYo(u)) return;
    this.busy = true;
    this.api.updateUsuario(u.id, { estado: 'ACTIVO' }).subscribe({
      next: () => {
        this.busy = false;
        this.reload();
        this.closeModals();
        this.cdr.markForCheck();
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo activar el usuario.';
        this.cdr.markForCheck();
      },
    });
  }

  eliminar(u: UsuarioListDto): void {
    if (!this.puedeEliminar || this.esYo(u)) return;
    if (
      !confirm(
        `¿Eliminar permanentemente a ${u.email}? Solo es posible si no es responsable de taller ni tiene atenciones como técnico.`,
      )
    ) {
      return;
    }
    this.busy = true;
    this.api.deleteUsuario(u.id).subscribe({
      next: () => {
        this.busy = false;
        this.reload();
        this.closeModals();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.busy = false;
        const msg = err?.error?.detail;
        this.error =
          typeof msg === 'string'
            ? msg
            : 'No se pudo eliminar el usuario (puede tener historial o ser responsable de taller).';
        this.cdr.markForCheck();
      },
    });
  }
}
