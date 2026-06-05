import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TallerComunicacionApiService } from '../../../../core/services/taller-comunicacion-api.service';
import type { NotificacionDto } from '../../../../core/models/comunicacion.models';

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
      void this.router.navigate(['/taller/panel/emergencias/solicitudes'], {
        queryParams: { q: String(notif.solicitud_id) },
      });
    }
  }
}
