import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TallerComunicacionApiService } from '../../../../core/services/taller-comunicacion-api.service';
import type { NotificacionDto, TipoNotificacion } from '../../../../core/models/comunicacion.models';

@Component({
  selector: 'app-taller-notificaciones',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './taller-notificaciones.component.html',
  styleUrl: './taller-notificaciones.component.scss',
})
export class TallerNotificacionesComponent implements OnInit, OnDestroy {
  private readonly api = inject(TallerComunicacionApiService);
  private readonly router = inject(Router);

  items: NotificacionDto[] = [];
  soloNoLeidas = false;
  loading = true;
  error: string | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.reload();
    this.pollTimer = setInterval(() => this.reload(true), 30_000);
  }

  ngOnDestroy(): void {
    if (this.pollTimer) clearInterval(this.pollTimer);
  }

  toggleFiltro(soloNoLeidas: boolean): void {
    this.soloNoLeidas = soloNoLeidas;
    this.reload();
  }

  reload(silent = false): void {
    if (!silent) {
      this.loading = true;
      this.error = null;
    }
    this.api.listNotificaciones({ soloNoLeidas: this.soloNoLeidas, limit: 100 }).subscribe({
      next: (list) => {
        this.items = list;
        this.loading = false;
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail ?? 'No se pudieron cargar las notificaciones.';
      },
    });
  }

  abrir(notif: NotificacionDto): void {
    if (!notif.leida) {
      this.api.marcarLeida(notif.id).subscribe({
        next: (updated) => {
          notif.leida = updated.leida;
          notif.leida_at = updated.leida_at;
        },
      });
    }
    if (notif.solicitud_id != null) {
      const route =
        notif.tipo === 'SOLICITUD_PENDIENTE_TALLER'
          ? '/taller/panel/emergencias/solicitudes'
          : '/taller/panel/emergencias/mis-solicitudes';
      void this.router.navigate([route], {
        queryParams: { q: String(notif.solicitud_id) },
      });
    }
  }

  tipoLabel(tipo: TipoNotificacion): string {
    const labels: Record<TipoNotificacion, string> = {
      SOLICITUD_CREADA: 'Emergencia registrada',
      ESTADO_ACTUALIZADO: 'Estado / pago',
      TALLER_ASIGNADO: 'Taller asignado',
      TECNICO_ASIGNADO: 'Técnico asignado',
      MENSAJE_NUEVO: 'Mensaje del cliente',
      SOLICITUD_PENDIENTE_TALLER: 'Nueva solicitud',
    };
    return labels[tipo] ?? tipo;
  }
}
