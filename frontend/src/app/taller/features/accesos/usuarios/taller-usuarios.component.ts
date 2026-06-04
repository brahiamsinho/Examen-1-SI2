import { Component, inject, OnInit } from '@angular/core';
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

const ROLES_ASIGNABLES = new Set(['TECNICO', 'TALLER_RESPONSABLE']);

@Component({
  selector: 'app-taller-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-usuarios.component.html',
  styleUrl: './taller-usuarios.component.scss',
})
export class TallerUsuariosComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  readonly auth = inject(TallerAuthService);

  usuarios: UsuarioListDto[] = [];
  roles: RolDto[] = [];
  search = '';
  estado: EstadoUsuario | '' = '';
  rolFilter = '';
  loading = true;
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
    this.reload();
  }

  get puedeCrear(): boolean {
    return this.auth.tienePermiso('usuarios:crear');
  }

  get puedeEditar(): boolean {
    return this.auth.tienePermiso('usuarios:actualizar');
  }

  get assignableRoles(): RolDto[] {
    return this.roles.filter((r) => ROLES_ASIGNABLES.has(r.nombre));
  }

  get rolesForFilter(): RolDto[] {
    return this.assignableRoles;
  }

  reload(): void {
    this.loading = true;
    forkJoin({
      usuarios: this.api.listUsuarios(),
      roles: this.api.listRoles(),
    }).subscribe({
      next: ({ usuarios, roles }) => {
        this.usuarios = usuarios;
        this.roles = roles;
        this.loading = false;
        this.error = null;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudieron cargar los usuarios de tu organización.';
      },
    });
  }

  get filtered(): UsuarioListDto[] {
    let rows = this.usuarios;
    if (this.estado) rows = rows.filter((u) => u.estado === this.estado);
    if (this.rolFilter) rows = rows.filter((u) => (u.roles || []).includes(this.rolFilter));
    const q = this.search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (u) =>
          u.email.toLowerCase().includes(q) ||
          u.nombres.toLowerCase().includes(q) ||
          u.apellidos.toLowerCase().includes(q),
      );
    }
    return rows;
  }

  openCreateModal(): void {
    this.error = null;
    this.modalCreate = true;
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
    if (!this.selected || !this.puedeEditar) return;
    this.busy = true;
    this.api.updateUsuario(this.selected.id, this.editForm).subscribe({
      next: (u) => {
        const prevRoles = this.selected?.roles || [];
        this.usuarios = this.usuarios.map((x) =>
          x.id === u.id ? { ...(u as UsuarioListDto), roles: prevRoles } : x,
        );
        this.closeModals();
        this.busy = false;
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo actualizar el usuario.';
      },
    });
  }

  create(): void {
    if (!this.puedeCrear) return;
    if (!this.createForm.password || this.createForm.password.length < 4) {
      this.error = 'La contraseña debe tener al menos 4 caracteres.';
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
      },
      error: () => {
        this.busy = false;
        this.error = 'No se pudo crear el usuario (email o teléfono duplicado).';
      },
    });
  }

  openRoles(u: UsuarioListDto): void {
    if (!this.puedeEditar) return;
    this.selected = u;
    const names = new Set(u.roles || []);
    this.rolIds = new Set(this.assignableRoles.filter((r) => names.has(r.nombre)).map((r) => r.id));
    this.modalRoles = true;
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
      },
    });
  }

  closeModals(): void {
    this.modalCreate = this.modalEdit = this.modalDetail = this.modalRoles = false;
    this.selected = null;
    this.rolIds = new Set();
  }
}
