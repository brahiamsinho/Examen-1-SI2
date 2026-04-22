import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import { TallerApiService } from '../../../../core/services/taller-api.service';
import { TallerAuthService } from '../../../../core/services/taller-auth.service';
import type {
  AsignacionTecnicoDto,
  SolicitudBandejaDetalleDto,
} from '../../../../core/models/taller-emergencias.models';
import type { TecnicoPortalDto } from '../../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-emergencias-incidente-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './taller-emergencias-incidente-detalle.component.html',
  styleUrl: './taller-emergencias-incidente-detalle.component.scss',
})
export class TallerEmergenciasIncidenteDetalleComponent implements OnInit {
  private readonly api = inject(TallerEmergenciasApiService);
  private readonly tallerApi = inject(TallerApiService);
  private readonly auth = inject(TallerAuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  bandejaId: number | null = null;
  detalle: SolicitudBandejaDetalleDto | null = null;
  loading = true;
  error: string | null = null;
  busy = false;

  successMsg: string | null = null;

  tecnicos: TecnicoPortalDto[] = [];
  asignaciones: AsignacionTecnicoDto[] = [];
  loadingAsignData = false;
  selectedTecnicoId: number | null = null;
  observacionAsignacion = '';

  modalAceptar = false;
  modalRechazar = false;
  motivoRechazo = '';

  ngOnInit(): void {
    this.route.paramMap.subscribe((p) => {
      const id = Number(p.get('bandejaId'));
      this.bandejaId = Number.isFinite(id) && id > 0 ? id : null;
      if (this.bandejaId) this.load();
      else {
        this.loading = false;
        this.error = 'Identificador de bandeja inválido.';
      }
    });
  }

  load(): void {
    if (!this.bandejaId) return;
    this.loading = true;
    this.error = null;
    this.successMsg = null;
    this.tecnicos = [];
    this.asignaciones = [];
    this.selectedTecnicoId = null;
    this.observacionAsignacion = '';
    this.api.getBandejaDetalle(this.bandejaId).subscribe({
      next: (d) => {
        this.detalle = d;
        this.loading = false;
        this.cargarDatosAsignacion(d);
      },
      error: (err) => {
        this.loading = false;
        this.detalle = null;
        this.error = this.msg(err, 'No se pudo cargar el detalle del incidente.');
      },
    });
  }

  private cargarDatosAsignacion(d: SolicitudBandejaDetalleDto): void {
    if (!this.debeMostrarBloqueAsignacion(d)) {
      this.loadingAsignData = false;
      return;
    }
    this.loadingAsignData = true;
    forkJoin({
      tecnicos: this.tallerApi.listTecnicos(),
      asignaciones: this.api.listarAsignacionesTecnico(d.solicitud_id),
    }).subscribe({
      next: ({ tecnicos, asignaciones }) => {
        this.tecnicos = tecnicos;
        this.asignaciones = [...asignaciones].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        );
        const ultimo = this.asignaciones.find((r) => r.estado === 'ASIGNADO');
        this.selectedTecnicoId = ultimo?.tecnico_id ?? null;
        this.loadingAsignData = false;
      },
      error: (err) => {
        this.loadingAsignData = false;
        this.error = this.msg(err, 'No se pudieron cargar técnicos o el historial de asignaciones.');
      },
    });
  }

  /** Tras aceptar la bandeja: asignar o reasignar técnico. */
  debeMostrarBloqueAsignacion(d: SolicitudBandejaDetalleDto | null): boolean {
    if (!d || d.estado_bandeja !== 'ACEPTADA') return false;
    return d.estado_solicitud === 'TALLER_ASIGNADO' || d.estado_solicitud === 'TECNICO_ASIGNADO';
  }

  tecnicosActivos(): TecnicoPortalDto[] {
    return this.tecnicos.filter((t) => t.estado === 'ACTIVO');
  }

  puedeAsignarTecnico(): boolean {
    if (!this.puedeAsignarTecnicoPermiso()) return false;
    const d = this.detalle;
    return !!d && this.debeMostrarBloqueAsignacion(d);
  }

  private puedeAsignarTecnicoPermiso(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('tecnicos:asignar');
  }

  externalMapLink(): string | null {
    const d = this.detalle;
    if (!d?.latitud || !d?.longitud) return null;
    return `https://www.openstreetmap.org/?mlat=${d.latitud}&mlon=${d.longitud}#map=16/${d.latitud}/${d.longitud}`;
  }

  openAceptar(): void {
    this.modalAceptar = true;
  }

  openRechazar(): void {
    this.motivoRechazo = '';
    this.modalRechazar = true;
  }

  closeModals(): void {
    this.modalAceptar = this.modalRechazar = false;
  }

  confirmAceptar(): void {
    if (!this.bandejaId) return;
    this.busy = true;
    this.api.aceptarBandeja(this.bandejaId).subscribe({
      next: () => {
        this.busy = false;
        this.closeModals();
        this.successMsg = 'Solicitud aceptada. Podés asignar un técnico a continuación.';
        this.load();
      },
      error: (err) => {
        this.busy = false;
        this.error = this.msg(err, 'No se pudo aceptar la solicitud.');
      },
    });
  }

  confirmRechazar(): void {
    const m = this.motivoRechazo.trim();
    if (m.length < 3) {
      this.error = 'El motivo de rechazo debe tener al menos 3 caracteres.';
      return;
    }
    if (!this.bandejaId) return;
    this.busy = true;
    this.api.rechazarBandeja(this.bandejaId, { motivo_rechazo: m }).subscribe({
      next: () => {
        this.busy = false;
        this.closeModals();
        void this.router.navigate(['/taller/panel/emergencias/solicitudes'], { queryParams: { ok: 'rechazada' } });
      },
      error: (err) => {
        this.busy = false;
        this.error = this.msg(err, 'No se pudo rechazar la solicitud.');
      },
    });
  }

  confirmarAsignarTecnico(): void {
    const d = this.detalle;
    if (!d || this.selectedTecnicoId == null || this.selectedTecnicoId < 1) {
      this.error = 'Seleccioná un técnico.';
      return;
    }
    const obs = this.observacionAsignacion.trim();
    this.busy = true;
    this.error = null;
    this.api
      .asignarTecnico(d.solicitud_id, {
        tecnico_id: this.selectedTecnicoId,
        observacion: obs.length ? obs : null,
      })
      .subscribe({
        next: () => {
          this.busy = false;
          this.successMsg = 'Técnico asignado correctamente.';
          this.load();
        },
        error: (err) => {
          this.busy = false;
          this.error = this.msg(err, 'No se pudo asignar el técnico.');
        },
      });
  }

  nombreTecnico(id: number): string {
    const t = this.tecnicos.find((x) => x.id === id);
    return t ? `${t.nombres} ${t.apellidos}`.trim() : `ID ${id}`;
  }

  puedeOperarBandeja(): boolean {
    const d = this.detalle;
    return !!d && d.estado_bandeja === 'PENDIENTE';
  }

  puedeAceptar(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('solicitudes_taller:aceptar');
  }

  puedeRechazar(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('solicitudes_taller:rechazar');
  }

  private msg(err: { error?: { detail?: unknown } }, fallback: string): string {
    const d = err?.error?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d) && d.length && typeof d[0] === 'object' && d[0] !== null && 'msg' in d[0]) {
      return String((d[0] as { msg: string }).msg);
    }
    return fallback;
  }
}
