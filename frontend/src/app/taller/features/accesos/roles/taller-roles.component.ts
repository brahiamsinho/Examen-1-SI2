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
import { forkJoin } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import type { PermisoDto, RolDto } from '../../../../core/models/admin-api.models';

const ROLES_EDITABLES = new Set(['TECNICO', 'TALLER_RESPONSABLE']);

@Component({
  selector: 'app-taller-roles',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-roles.component.html',
  styleUrl: './taller-roles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerRolesComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  roles: RolDto[] = [];
  permisos: PermisoDto[] = [];
  search = '';
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  modalPerm = false;
  modalView = false;
  selectedRol: RolDto | null = null;
  permIds = new Set<number>();

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    forkJoin({
      roles: this.api.listRoles(),
      permisos: this.api.listPermisos(),
    })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: ({ roles, permisos }) => {
          this.roles = roles;
          this.permisos = permisos;
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudieron cargar los roles.';
          this.cdr.markForCheck();
        },
      });
  }

  get filtered(): RolDto[] {
    const q = this.search.trim().toLowerCase();
    if (!q) return this.roles;
    return this.roles.filter(
      (r) =>
        r.nombre.toLowerCase().includes(q) ||
        (r.descripcion && r.descripcion.toLowerCase().includes(q)),
    );
  }

  puedeEditarPermisos(r: RolDto): boolean {
    return ROLES_EDITABLES.has(r.nombre);
  }

  permisosByModulo(): Record<string, PermisoDto[]> {
    const m: Record<string, PermisoDto[]> = {};
    for (const p of this.permisos) {
      m[p.modulo] = m[p.modulo] || [];
      m[p.modulo].push(p);
    }
    return m;
  }

  openView(r: RolDto): void {
    this.selectedRol = r;
    this.modalView = true;
    this.cdr.markForCheck();
  }

  openPerm(r: RolDto): void {
    if (!this.puedeEditarPermisos(r)) return;
    this.selectedRol = r;
    this.busy = true;
    this.api
      .getRolPermisoIds(r.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (dto) => {
          this.permIds = new Set(dto.permiso_ids);
          this.modalPerm = true;
          this.busy = false;
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudieron cargar los permisos del rol.';
          this.cdr.markForCheck();
        },
      });
  }

  togglePerm(id: number): void {
    if (this.permIds.has(id)) this.permIds.delete(id);
    else this.permIds.add(id);
    this.cdr.markForCheck();
  }

  savePerm(): void {
    if (!this.selectedRol) return;
    this.busy = true;
    this.api
      .setRolPermisos(this.selectedRol.id, [...this.permIds])
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.modalPerm = false;
          this.busy = false;
          this.selectedRol = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudieron guardar los permisos.';
          this.cdr.markForCheck();
        },
      });
  }

  closeModals(): void {
    this.modalPerm = this.modalView = false;
    this.selectedRol = null;
    this.permIds = new Set();
    this.cdr.markForCheck();
  }
}
