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
import { TallerApiService } from '../../../core/services/taller-api.service';
import type {
  EspecialidadDto,
  EstadoTecnico,
  TecnicoPortalCreatePayload,
  TecnicoPortalDto,
  TecnicoPortalUpdatePayload,
} from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-tecnicos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-tecnicos.component.html',
  styleUrl: './taller-tecnicos.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerTecnicosComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  tecnicos: TecnicoPortalDto[] = [];
  especialidades: EspecialidadDto[] = [];
  search = '';
  estado: EstadoTecnico | '' = '';
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  modalCreate = false;
  modalEdit = false;
  modalDetail = false;
  selected: TecnicoPortalDto | null = null;

  createForm: TecnicoPortalCreatePayload = {
    nombre_completo: '',
    email: '',
    telefono: '',
    password: '',
    documento: '',
    especialidad_id: null,
    disponibilidad: '',
    estado: 'ACTIVO',
  };

  editNombre = '';
  editEmail = '';
  editTelefono = '';
  editDocumento = '';
  editEsp: number | null = null;
  editDisp = '';
  editEstado: EstadoTecnico = 'ACTIVO';

  readonly estados: EstadoTecnico[] = ['ACTIVO', 'INACTIVO'];

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    forkJoin({ tecnicos: this.api.listTecnicos(), esp: this.api.listEspecialidades() })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: ({ tecnicos, esp }) => {
          this.tecnicos = tecnicos;
          this.especialidades = esp;
          this.error = null;
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudieron cargar los técnicos.';
          this.cdr.markForCheck();
        },
      });
  }

  get filtered(): TecnicoPortalDto[] {
    let rows = this.tecnicos;
    if (this.estado) rows = rows.filter((t) => t.estado === this.estado);
    const q = this.search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (t) =>
          `${t.nombres} ${t.apellidos}`.toLowerCase().includes(q) ||
          t.email.toLowerCase().includes(q) ||
          t.telefono.includes(q) ||
          (t.especialidad_nombre && t.especialidad_nombre.toLowerCase().includes(q)),
      );
    }
    return rows;
  }

  openDetail(t: TecnicoPortalDto): void {
    this.selected = t;
    this.modalDetail = true;
    this.cdr.markForCheck();
  }

  openEditFromDetail(): void {
    const t = this.selected;
    if (!t) return;
    this.modalDetail = false;
    this.openEdit(t);
  }

  openCreate(): void {
    this.createForm = {
      nombre_completo: '',
      email: '',
      telefono: '',
      password: '',
      documento: '',
      especialidad_id: this.especialidades[0]?.id ?? null,
      disponibilidad: '',
      estado: 'ACTIVO',
    };
    this.modalCreate = true;
    this.cdr.markForCheck();
  }

  create(): void {
    if (!this.createForm.password || this.createForm.password.length < 4) {
      this.error = 'La contraseña del técnico debe tener al menos 4 caracteres.';
      this.cdr.markForCheck();
      return;
    }
    this.busy = true;
    this.api
      .createTecnico(this.createForm)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.modalCreate = false;
          this.busy = false;
          this.cdr.markForCheck();
          this.reload();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo registrar el técnico (email o teléfono duplicado).';
          this.cdr.markForCheck();
        },
      });
  }

  openEdit(t: TecnicoPortalDto): void {
    this.selected = t;
    this.editNombre = `${t.nombres} ${t.apellidos}`.trim();
    this.editEmail = t.email;
    this.editTelefono = t.telefono;
    this.editDocumento = t.documento ?? '';
    this.editEsp = t.especialidad_id;
    this.editDisp = t.disponibilidad ?? '';
    this.editEstado = t.estado;
    this.modalEdit = true;
    this.cdr.markForCheck();
  }

  saveEdit(): void {
    if (!this.selected) return;
    const body: TecnicoPortalUpdatePayload = {
      nombre_completo: this.editNombre,
      email: this.editEmail,
      telefono: this.editTelefono,
      documento: this.editDocumento || null,
      especialidad_id: this.editEsp,
      disponibilidad: this.editDisp || null,
      estado: this.editEstado,
    };
    this.busy = true;
    this.api
      .updateTecnico(this.selected.id, body)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.modalEdit = false;
          this.busy = false;
          this.cdr.markForCheck();
          this.reload();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo actualizar el técnico.';
          this.cdr.markForCheck();
        },
      });
  }

  setEstado(t: TecnicoPortalDto, e: EstadoTecnico): void {
    this.busy = true;
    this.api
      .updateTecnico(t.id, { estado: e })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.cdr.markForCheck();
          this.reload();
          this.closeModals();
        },
        error: () => {
          this.busy = false;
          this.error = 'No se pudo cambiar el estado.';
          this.cdr.markForCheck();
        },
      });
  }

  closeModals(): void {
    this.modalCreate = this.modalEdit = this.modalDetail = false;
    this.selected = null;
    this.cdr.markForCheck();
  }
}
