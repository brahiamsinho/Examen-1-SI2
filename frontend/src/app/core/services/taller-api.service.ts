import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  EspecialidadDto,
  MiTallerDto,
  MiTallerUpdatePayload,
  RegistroTallerPayload,
  TallerDashboardDto,
  TallerSuscripcionCheckoutPayload,
  TallerSuscripcionCheckoutResponse,
  TallerSuscripcionConfirmPayload,
  TallerSuscripcionDto,
  TecnicoPortalCreatePayload,
  TecnicoPortalDto,
  TecnicoPortalUpdatePayload,
  TallerBitacoraDto,
  TallerBitacoraListParams,
} from '../models/taller-api.models';

@Injectable({ providedIn: 'root' })
export class TallerApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/app/taller`;

  registro(body: RegistroTallerPayload): Observable<MiTallerDto> {
    return this.http.post<MiTallerDto>(`${this.base}/registro`, body);
  }

  getDashboard(): Observable<TallerDashboardDto> {
    return this.http.get<TallerDashboardDto>(`${this.base}/dashboard`);
  }

  getMiTaller(): Observable<MiTallerDto> {
    return this.http.get<MiTallerDto>(`${this.base}/mi-taller`);
  }

  updateMiTaller(body: MiTallerUpdatePayload): Observable<MiTallerDto> {
    return this.http.put<MiTallerDto>(`${this.base}/mi-taller`, body);
  }

  listTecnicos(): Observable<TecnicoPortalDto[]> {
    return this.http.get<TecnicoPortalDto[]>(`${this.base}/tecnicos`);
  }

  getTecnico(id: number): Observable<TecnicoPortalDto> {
    return this.http.get<TecnicoPortalDto>(`${this.base}/tecnicos/${id}`);
  }

  createTecnico(body: TecnicoPortalCreatePayload): Observable<TecnicoPortalDto> {
    return this.http.post<TecnicoPortalDto>(`${this.base}/tecnicos`, body);
  }

  updateTecnico(id: number, body: TecnicoPortalUpdatePayload): Observable<TecnicoPortalDto> {
    return this.http.put<TecnicoPortalDto>(`${this.base}/tecnicos/${id}`, body);
  }

  listEspecialidades(): Observable<EspecialidadDto[]> {
    return this.http.get<EspecialidadDto[]>(`${environment.apiUrl}/especialidades`);
  }

  getSuscripcion(): Observable<TallerSuscripcionDto> {
    return this.http.get<TallerSuscripcionDto>(`${this.base}/suscripcion`);
  }

  createSuscripcionCheckout(body: TallerSuscripcionCheckoutPayload): Observable<TallerSuscripcionCheckoutResponse> {
    return this.http.post<TallerSuscripcionCheckoutResponse>(`${this.base}/suscripcion/checkout`, body);
  }

  confirmSuscripcionCheckout(body: TallerSuscripcionConfirmPayload): Observable<TallerSuscripcionDto> {
    return this.http.post<TallerSuscripcionDto>(`${this.base}/suscripcion/confirm`, body);
  }

  listBitacora(params: TallerBitacoraListParams = {}): Observable<TallerBitacoraDto[]> {
    let httpParams = new HttpParams();
    if (params.usuario_id != null) httpParams = httpParams.set('usuario_id', String(params.usuario_id));
    if (params.modulo) httpParams = httpParams.set('modulo', params.modulo);
    if (params.accion) httpParams = httpParams.set('accion', params.accion);
    if (params.desde) httpParams = httpParams.set('desde', params.desde);
    if (params.hasta) httpParams = httpParams.set('hasta', params.hasta);
    if (params.limit != null) httpParams = httpParams.set('limit', String(params.limit));
    if (params.offset != null) httpParams = httpParams.set('offset', String(params.offset));
    return this.http.get<TallerBitacoraDto[]>(`${this.base}/bitacora`, { params: httpParams });
  }
}
