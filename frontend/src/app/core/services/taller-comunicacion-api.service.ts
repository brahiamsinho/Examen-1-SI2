import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type { NotificacionDto } from '../models/comunicacion.models';

@Injectable({ providedIn: 'root' })
export class TallerComunicacionApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/app/taller`;

  listNotificaciones(opts?: { soloNoLeidas?: boolean; limit?: number }): Observable<NotificacionDto[]> {
    let params = new HttpParams();
    if (opts?.soloNoLeidas) params = params.set('no_leidas', 'true');
    if (opts?.limit != null) params = params.set('limit', String(opts.limit));
    return this.http.get<NotificacionDto[]>(`${this.base}/notificaciones`, { params });
  }

  marcarLeida(id: number): Observable<NotificacionDto> {
    return this.http.patch<NotificacionDto>(`${this.base}/notificaciones/${id}/leida`, {});
  }
}
