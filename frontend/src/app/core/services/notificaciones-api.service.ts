import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type { NotificacionDto, NotificacionPortal } from '../models/notificacion.models';

@Injectable({ providedIn: 'root' })
export class NotificacionesApiService {
  private readonly http = inject(HttpClient);

  private base(portal: NotificacionPortal): string {
    return portal === 'taller'
      ? `${environment.apiUrl}/app/taller/notificaciones`
      : `${environment.apiUrl}/admin/notificaciones`;
  }

  listar(portal: NotificacionPortal, soloNoLeidas = false, limit = 50): Observable<NotificacionDto[]> {
    let params = new HttpParams().set('limit', String(limit));
    if (soloNoLeidas) {
      params = params.set('no_leidas', 'true');
    }
    return this.http.get<NotificacionDto[]>(this.base(portal), { params });
  }

  marcarLeida(portal: NotificacionPortal, notificacionId: number): Observable<NotificacionDto> {
    return this.http.patch<NotificacionDto>(`${this.base(portal)}/${notificacionId}/leida`, {});
  }
}
