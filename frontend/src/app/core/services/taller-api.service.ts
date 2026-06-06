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
  TallerBackupConfigDto,
  TallerBackupConfigUpdatePayload,
  TallerBackupDto,
  TallerBackupRestorePayload,
  QbePayload,
  ReportExecuteResultDto,
  ReportExportFormat,
  ReportNlQueryResultDto,
  ReportVoiceTranscribeResultDto,
  ReportTemplateCreatePayload,
  ReportTemplateDto,
  TallerHorariosDto,
  TallerHorariosUpdatePayload,
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

  getHorarios(): Observable<TallerHorariosDto> {
    return this.http.get<TallerHorariosDto>(`${this.base}/horarios`);
  }

  putHorarios(body: TallerHorariosUpdatePayload): Observable<TallerHorariosDto> {
    return this.http.put<TallerHorariosDto>(`${this.base}/horarios`, body);
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

  desactivarTecnico(id: number): Observable<TecnicoPortalDto> {
    return this.http.post<TecnicoPortalDto>(`${this.base}/tecnicos/${id}/desactivar`, {});
  }

  deleteTecnico(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/tecnicos/${id}`);
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

  listBackups(): Observable<TallerBackupDto[]> {
    return this.http.get<TallerBackupDto[]>(`${this.base}/backups/`);
  }

  createBackup(): Observable<TallerBackupDto> {
    return this.http.post<TallerBackupDto>(`${this.base}/backups/`, {});
  }

  getBackupConfig(): Observable<TallerBackupConfigDto> {
    return this.http.get<TallerBackupConfigDto>(`${this.base}/backups/config`);
  }

  updateBackupConfig(payload: TallerBackupConfigUpdatePayload): Observable<TallerBackupConfigDto> {
    return this.http.patch<TallerBackupConfigDto>(`${this.base}/backups/config`, payload);
  }

  downloadBackup(id: number): Observable<Blob> {
    return this.http.get(`${this.base}/backups/${id}/download`, { responseType: 'blob' });
  }

  restoreBackup(id: number, payload: TallerBackupRestorePayload): Observable<TallerBackupDto> {
    return this.http.post<TallerBackupDto>(`${this.base}/backups/${id}/restore`, payload);
  }

  deleteBackup(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/backups/${id}`);
  }

  listReportTemplates(isSystem?: boolean): Observable<ReportTemplateDto[]> {
    let params = new HttpParams();
    if (isSystem != null) params = params.set('is_system_report', String(isSystem));
    return this.http.get<ReportTemplateDto[]>(`${this.base}/reportes/plantillas`, { params });
  }

  runReportTemplate(id: number): Observable<{ qbe: QbePayload; report: ReportExecuteResultDto }> {
    return this.http.post<{ qbe: QbePayload; report: ReportExecuteResultDto }>(
      `${this.base}/reportes/plantillas/${id}/run`,
      {},
    );
  }

  executeReport(qbe: QbePayload): Observable<ReportExecuteResultDto> {
    return this.http.post<ReportExecuteResultDto>(`${this.base}/reportes/execute`, qbe);
  }

  nlReportQuery(query: string): Observable<ReportNlQueryResultDto> {
    return this.http.post<ReportNlQueryResultDto>(`${this.base}/reportes/nl-query`, { query });
  }

  voiceReportQuery(audio: Blob, filename = 'voice.webm'): Observable<ReportVoiceTranscribeResultDto> {
    const form = new FormData();
    form.append('file', audio, filename);
    return this.http.post<ReportVoiceTranscribeResultDto>(`${this.base}/reportes/voice`, form);
  }

  exportReport(fmt: ReportExportFormat, qbe: QbePayload): Observable<Blob> {
    return this.http.post(`${this.base}/reportes/export/${fmt}`, qbe, { responseType: 'blob' });
  }

  createReportTemplate(body: ReportTemplateCreatePayload): Observable<ReportTemplateDto> {
    return this.http.post<ReportTemplateDto>(`${this.base}/reportes/plantillas`, body);
  }

  deleteReportTemplate(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/reportes/plantillas/${id}`);
  }
}
