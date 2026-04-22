import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import type { BandejaIncidenteBaseDto, EstadoSolicitudSeguimiento } from '../../../../core/models/taller-emergencias.models';

@Component({
  selector: 'app-taller-emergencias-bandeja',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './taller-emergencias-bandeja.component.html',
  styleUrl: './taller-emergencias-bandeja.component.scss',
})
export class TallerEmergenciasBandejaComponent implements OnInit {
  private readonly api = inject(TallerEmergenciasApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  rows: BandejaIncidenteBaseDto[] = [];
  search = '';
  estadoSolicitud: EstadoSolicitudSeguimiento | '' = '';
  loading = true;
  error: string | null = null;
  successFlash: string | null = null;

  readonly estados: EstadoSolicitudSeguimiento[] = [
    'REGISTRADA',
    'EN_REVISION',
    'TALLER_ASIGNADO',
    'TECNICO_ASIGNADO',
    'EN_CAMINO',
    'EN_ATENCION',
    'FINALIZADA',
    'CANCELADA',
  ];

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((q) => {
      const ok = q.get('ok');
      if (ok === 'aceptada') {
        this.successFlash = 'Solicitud aceptada correctamente.';
        void this.router.navigate([], { relativeTo: this.route, queryParams: {}, replaceUrl: true });
      } else if (ok === 'rechazada') {
        this.successFlash = 'Solicitud rechazada.';
        void this.router.navigate([], { relativeTo: this.route, queryParams: {}, replaceUrl: true });
      }
    });
    this.reload();
  }

  reload(): void {
    this.loading = true;
    this.error = null;
    this.api.listBandejaDisponibles().subscribe({
      next: (list) => {
        this.rows = list;
        this.loading = false;
      },
      error: (err) => {
        this.loading = false;
        this.error = this.msg(err, 'No se pudo cargar la bandeja de solicitudes.');
      },
    });
  }

  dismissFlash(): void {
    this.successFlash = null;
  }

  get filtered(): BandejaIncidenteBaseDto[] {
    let r = this.rows;
    if (this.estadoSolicitud) {
      r = r.filter((x) => x.estado_solicitud === this.estadoSolicitud);
    }
    const q = this.search.trim().toLowerCase();
    if (!q) return r;
    return r.filter(
      (x) =>
        x.placa.toLowerCase().includes(q) ||
        `${x.nombres} ${x.apellidos}`.toLowerCase().includes(q) ||
        (x.marca && x.marca.toLowerCase().includes(q)) ||
        (x.modelo && x.modelo.toLowerCase().includes(q)) ||
        String(x.solicitud_id).includes(q),
    );
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
