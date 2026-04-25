import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  AsignacionTecnicoDto,
  AsignarTecnicoPayload,
  AsignarTecnicoResultDto,
  BandejaIncidenteBaseDto,
  RechazarBandejaPayload,
  SolicitudBandejaDetalleDto,
  TallerDisponibilidadDto,
  TallerDisponibilidadUpdatePayload,
} from '../models/taller-emergencias.models';

@Injectable({ providedIn: 'root' })
export class TallerEmergenciasApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/portal/taller/emergencias`;

  listBandejaDisponibles(): Observable<BandejaIncidenteBaseDto[]> {
    return this.http.get<BandejaIncidenteBaseDto[]>(`${this.base}/bandeja/disponibles`);
  }

  getBandejaDetalle(bandejaId: number): Observable<SolicitudBandejaDetalleDto> {
    return this.http.get<SolicitudBandejaDetalleDto>(`${this.base}/bandeja/${bandejaId}`);
  }

  aceptarBandeja(bandejaId: number): Observable<SolicitudBandejaDetalleDto> {
    return this.http.post<SolicitudBandejaDetalleDto>(`${this.base}/bandeja/${bandejaId}/aceptar`, {});
  }

  rechazarBandeja(bandejaId: number, body: RechazarBandejaPayload): Observable<SolicitudBandejaDetalleDto> {
    return this.http.post<SolicitudBandejaDetalleDto>(`${this.base}/bandeja/${bandejaId}/rechazar`, body);
  }

  getDisponibilidad(): Observable<TallerDisponibilidadDto> {
    return this.http.get<TallerDisponibilidadDto>(`${this.base}/disponibilidad`);
  }

  putDisponibilidad(body: TallerDisponibilidadUpdatePayload): Observable<TallerDisponibilidadDto> {
    return this.http.put<TallerDisponibilidadDto>(`${this.base}/disponibilidad`, body);
  }

  /** Asignar o reasignar técnico a la solicitud. */
  asignarTecnico(solicitudId: number, body: AsignarTecnicoPayload): Observable<AsignarTecnicoResultDto> {
    return this.http.post<AsignarTecnicoResultDto>(
      `${this.base}/solicitudes/${solicitudId}/asignar-tecnico`,
      body,
    );
  }

  listarAsignacionesTecnico(solicitudId: number): Observable<AsignacionTecnicoDto[]> {
    return this.http.get<AsignacionTecnicoDto[]>(`${this.base}/solicitudes/${solicitudId}/asignaciones`);
  }
}
