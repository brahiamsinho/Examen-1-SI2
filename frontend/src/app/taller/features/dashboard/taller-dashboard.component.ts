import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TallerApiService } from '../../../core/services/taller-api.service';
import { TallerAuthService } from '../../../core/services/taller-auth.service';
import type { TallerDashboardDto } from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './taller-dashboard.component.html',
  styleUrl: './taller-dashboard.component.scss',
})
export class TallerDashboardComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  readonly auth = inject(TallerAuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  data: TallerDashboardDto | null = null;
  loading = true;
  error: string | null = null;
  permisoDenegado: string | null = null;

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((q) => {
      if (q.get('denegado') === '1') {
        this.permisoDenegado =
          'No tenés permiso para acceder a esa sección. Si necesitás emergencias en el panel, pedí que te asignen los permisos correspondientes.';
        void this.router.navigate([], { relativeTo: this.route, queryParams: {}, replaceUrl: true });
      }
    });
    this.api.getDashboard().subscribe({
      next: (d) => {
        this.data = d;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudo cargar el resumen del taller.';
      },
    });
  }

  /** Misma regla que `TallerShellComponent.nav`: sin lista de permisos → se muestran todos los enlaces. */
  puedeVerSolicitudesEmergencias(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('solicitudes_taller:leer');
  }

  puedeGestionarDisponibilidadEmergencias(): boolean {
    const p = this.auth.getMe()?.permisos;
    if (!p?.length) return true;
    return p.includes('disponibilidad:gestionar');
  }
}
