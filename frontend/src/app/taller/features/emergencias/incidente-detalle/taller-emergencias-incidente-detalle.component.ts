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
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import { TallerApiService } from '../../../../core/services/taller-api.service';
import { TallerAuthService } from '../../../../core/services/taller-auth.service';
import type {
  AsignacionTecnicoDto,
  SolicitudBandejaDetalleDto,
  SolicitudEvidenciaTallerDto,
} from '../../../../core/models/taller-emergencias.models';
import type { TecnicoPortalDto } from '../../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-emergencias-incidente-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './taller-emergencias-incidente-detalle.component.html',
  styleUrl: './taller-emergencias-incidente-detalle.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerEmergenciasIncidenteDetalleComponent implements OnInit {
  private readonly api = inject(TallerEmergenciasApiService);
  private readonly tallerApi = inject(TallerApiService);
  readonly auth = inject(TallerAuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  bandejaId: number | null = null;
  detalle: SolicitudBandejaDetalleDto | null = null;
  readonly loading = signal(true);
  error: string | null = null;
  busy = false;

  successMsg: string | null = null;

  tecnicos: TecnicoPortalDto[] = [];
  asignaciones: AsignacionTecnicoDto[] = [];
  readonly loadingAsignData = signal(false);
  selectedTecnicoId: number | null = null;
  observacionAsignacion = '';
  tiempoEstimadoMin: number | null = null;

  modalAceptar = false;
  modalRechazar = false;
  motivoRechazo = '';

  presupuestoBob: number | null = null;
  presupuestoDetalle = '';
  presupuestoObservaciones = '';

  ngOnInit(): void {
    this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((p) => {
      const id = Number(p.get('bandejaId'));
      this.bandejaId = Number.isFinite(id) && id > 0 ? id : null;
      if (this.bandejaId) this.load();
      else {
        this.loading.set(false);
        this.error = 'Identificador de bandeja inválido.';
        this.cdr.markForCheck();
      }
    });
  }

  load(): void {
    if (!this.bandejaId) return;
    this.loading.set(true);
    this.error = null;
    this.successMsg = null;
    this.tecnicos = [];
    this.asignaciones = [];
    this.selectedTecnicoId = null;
    this.observacionAsignacion = '';
    this.tiempoEstimadoMin = null;
    this.presupuestoBob = null;
    this.presupuestoDetalle = '';
    this.presupuestoObservaciones = '';
    this.api
      .getBandejaDetalle(this.bandejaId)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (d) => {
          this.detalle = d;
          this.cargarDatosAsignacion(d);
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.detalle = null;
          this.error = this.msg(err, 'No se pudo cargar el detalle del incidente.');
          this.cdr.markForCheck();
        },
      });
  }

  private cargarDatosAsignacion(d: SolicitudBandejaDetalleDto): void {
    if (!this.debeMostrarBloqueAsignacion(d)) {
      this.loadingAsignData.set(false);
      return;
    }
    this.loadingAsignData.set(true);
    forkJoin({
      tecnicos: this.tallerApi.listTecnicos(),
      asignaciones: this.api.listarAsignacionesTecnico(d.solicitud_id),
    })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loadingAsignData.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: ({ tecnicos, asignaciones }) => {
          this.tecnicos = tecnicos;
          this.asignaciones = [...asignaciones].sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
          );
          const ultimo = this.asignaciones.find((r) => r.estado === 'ASIGNADO');
          this.selectedTecnicoId = ultimo?.tecnico_id ?? null;
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.error = this.msg(err, 'No se pudieron cargar técnicos o el historial de asignaciones.');
          this.cdr.markForCheck();
        },
      });
  }

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

  aiTieneContenido(d: SolicitudBandejaDetalleDto | null): boolean {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return false;
    const p = d.ai_payload as Record<string, unknown>;
    const rs = p['resumen_estructurado'];
    if (rs && typeof rs === 'object' && 'resumen' in (rs as object)) {
      const t = String((rs as { resumen?: unknown }).resumen ?? '').trim();
      if (t.length > 0) return true;
    }
    if (p['clasificacion'] || p['prioridad']) return true;
    if (Array.isArray(p['hallazgos_vision']) && (p['hallazgos_vision'] as unknown[]).length) return true;
    const tr = p['transcripcion_audio'];
    if (typeof tr === 'string' && tr.trim().length > 0) return true;
    return false;
  }

  aiResumenTexto(d: SolicitudBandejaDetalleDto | null): string {
    if (!d?.ai_payload) return '';
    const p = d.ai_payload as Record<string, unknown>;
    const rs = p['resumen_estructurado'];
    if (rs && typeof rs === 'object' && 'resumen' in (rs as object)) {
      return String((rs as { resumen?: unknown }).resumen ?? '');
    }
    return '';
  }

  aiCategoriaUi(d: SolicitudBandejaDetalleDto | null): string | null {
    const c = this.aiCategoriaRaw(d);
    if (!c) return null;
    const m: Record<string, string> = {
      BATERIA: 'Batería',
      LLANTA: 'Llanta / pinchazo',
      CHOQUE: 'Choque / colisión',
      MOTOR: 'Motor',
      OTROS: 'Otros',
    };
    return m[c] ?? c;
  }

  private aiCategoriaRaw(d: SolicitudBandejaDetalleDto | null): string | null {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return null;
    const c = (d.ai_payload as Record<string, unknown>)['clasificacion'];
    if (!c || typeof c !== 'object') return null;
    const cat = (c as { categoria?: unknown }).categoria;
    return typeof cat === 'string' ? cat : null;
  }

  aiConfianzaClasificacion(d: SolicitudBandejaDetalleDto | null): number | null {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return null;
    const c = (d.ai_payload as Record<string, unknown>)['clasificacion'];
    if (!c || typeof c !== 'object') return null;
    const n = (c as { confianza?: unknown }).confianza;
    return typeof n === 'number' && Number.isFinite(n) ? n : null;
  }

  aiPrioridadUi(d: SolicitudBandejaDetalleDto | null): string | null {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return null;
    const pr = (d.ai_payload as Record<string, unknown>)['prioridad'];
    if (!pr || typeof pr !== 'object') return null;
    const n = (pr as { nivel_prioridad?: unknown }).nivel_prioridad;
    if (typeof n !== 'string') return null;
    const m: Record<string, string> = {
      ALTA: 'Alta',
      MEDIA: 'Media',
      BAJA: 'Baja',
      REVISION_MANUAL: 'Revisión manual',
    };
    return m[n] ?? n;
  }

  aiPrioridadMotivos(d: SolicitudBandejaDetalleDto | null): string[] {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return [];
    const pr = (d.ai_payload as Record<string, unknown>)['prioridad'];
    if (!pr || typeof pr !== 'object') return [];
    const m = (pr as { motivo?: unknown }).motivo;
    if (!Array.isArray(m)) return [];
    return m.filter((x): x is string => typeof x === 'string');
  }

  aiHallazgosVision(d: SolicitudBandejaDetalleDto | null): string[] {
    if (!d?.ai_payload || typeof d.ai_payload !== 'object') return [];
    const h = (d.ai_payload as Record<string, unknown>)['hallazgos_vision'];
    if (!Array.isArray(h)) return [];
    return h.map((x) => String(x));
  }

  evidenciasSafe(d: SolicitudBandejaDetalleDto | null): SolicitudEvidenciaTallerDto[] {
    if (!d?.evidencias?.length) return [];
    return d.evidencias;
  }

  evidenciaSrc(url: string): string {
    if (!url) return '';
    if (url.startsWith('/')) return url;
    try {
      const u = new URL(url);
      if (u.pathname.includes('/media/evidencias/')) {
        return u.pathname + (u.search || '');
      }
    } catch {
      /* no absoluta */
    }
    return url;
  }

  openAceptar(): void {
    this.modalAceptar = true;
    this.cdr.markForCheck();
  }

  openRechazar(): void {
    this.motivoRechazo = '';
    this.modalRechazar = true;
    this.cdr.markForCheck();
  }

  closeModals(): void {
    this.modalAceptar = this.modalRechazar = false;
    this.cdr.markForCheck();
  }

  confirmAceptar(): void {
    if (!this.bandejaId) return;
    this.busy = true;
    this.api
      .aceptarBandeja(this.bandejaId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.closeModals();
          this.successMsg = 'Solicitud aceptada. Podés asignar un técnico a continuación.';
          this.cdr.markForCheck();
          this.load();
        },
        error: (err) => {
          this.busy = false;
          this.error = this.msg(err, 'No se pudo aceptar la solicitud.');
          this.cdr.markForCheck();
        },
      });
  }

  confirmRechazar(): void {
    const m = this.motivoRechazo.trim();
    if (m.length < 3) {
      this.error = 'El motivo de rechazo debe tener al menos 3 caracteres.';
      this.cdr.markForCheck();
      return;
    }
    if (!this.bandejaId) return;
    this.busy = true;
    this.api
      .rechazarBandeja(this.bandejaId, { motivo_rechazo: m })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.closeModals();
          void this.router.navigate(['/taller/panel/emergencias/solicitudes'], { queryParams: { ok: 'rechazada' } });
        },
        error: (err) => {
          this.busy = false;
          this.error = this.msg(err, 'No se pudo rechazar la solicitud.');
          this.cdr.markForCheck();
        },
      });
  }

  confirmarAsignarTecnico(): void {
    const d = this.detalle;
    if (!d || this.selectedTecnicoId == null || this.selectedTecnicoId < 1) {
      this.error = 'Seleccioná un técnico.';
      this.cdr.markForCheck();
      return;
    }
    const obs = this.observacionAsignacion.trim();
    this.busy = true;
    this.error = null;
    this.api
      .asignarTecnico(d.solicitud_id, {
        tecnico_id: this.selectedTecnicoId,
        observacion: obs.length ? obs : null,
        tiempo_estimado_min: this.tiempoEstimadoMin != null && this.tiempoEstimadoMin > 0 ? this.tiempoEstimadoMin : null,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.successMsg = 'Técnico asignado correctamente.';
          this.cdr.markForCheck();
          this.load();
        },
        error: (err) => {
          this.busy = false;
          this.error = this.msg(err, 'No se pudo asignar el técnico.');
          this.cdr.markForCheck();
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

  private readonly estadosCotizacion = new Set([
    'TALLER_ASIGNADO',
    'TECNICO_ASIGNADO',
    'EN_CAMINO',
    'EN_ATENCION',
  ]);

  debeMostrarBloqueCotizacion(d: SolicitudBandejaDetalleDto | null): boolean {
    if (!d || d.estado_bandeja !== 'ACEPTADA') return false;
    return this.estadosCotizacion.has(d.estado_solicitud);
  }

  tieneCotizacion(d: SolicitudBandejaDetalleDto | null): boolean {
    if (!d?.presupuesto_bob || !d.presupuesto_registrado_at) return false;
    const m = Number(d.presupuesto_bob);
    return Number.isFinite(m) && m > 0;
  }

  puedeRegistrarCotizacion(): boolean {
    if (!this.puedeRegistrarCotizacionPermiso()) return false;
    const d = this.detalle;
    return !!d && this.debeMostrarBloqueCotizacion(d) && !this.tieneCotizacion(d);
  }

  private puedeRegistrarCotizacionPermiso(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('presupuestos:registrar');
  }

  montoCotizacionLabel(d: SolicitudBandejaDetalleDto | null): string {
    if (!d?.presupuesto_bob) return '—';
    const n = Number(d.presupuesto_bob);
    return Number.isFinite(n) ? `Bs. ${n.toFixed(2)}` : String(d.presupuesto_bob);
  }

  confirmarRegistrarCotizacion(): void {
    const d = this.detalle;
    if (!d) return;
    const monto = this.presupuestoBob;
    const detalle = this.presupuestoDetalle.trim();
    if (monto == null || monto <= 0) {
      this.error = 'Ingresá un monto válido en BOB (mayor que cero).';
      this.cdr.markForCheck();
      return;
    }
    if (detalle.length < 3) {
      this.error = 'El detalle de la cotización debe tener al menos 3 caracteres.';
      this.cdr.markForCheck();
      return;
    }
    const obs = this.presupuestoObservaciones.trim();
    this.busy = true;
    this.error = null;
    this.api
      .registrarPresupuesto(d.solicitud_id, {
        presupuesto_bob: monto,
        detalle,
        observaciones: obs.length ? obs : null,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy = false;
          this.successMsg = 'Cotización registrada. El cliente podrá revisarla en la app.';
          this.cdr.markForCheck();
          this.load();
        },
        error: (err) => {
          this.busy = false;
          this.error = this.msg(err, 'No se pudo registrar la cotización.');
          this.cdr.markForCheck();
        },
      });
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
