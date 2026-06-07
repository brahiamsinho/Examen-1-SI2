import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../../environments/environment';

export type RealtimeEventType =
  | 'conectado'
  | 'pong'
  | 'estado_incidente'
  | 'ubicacion_tecnico'
  | 'mensaje_nuevo'
  | 'bandeja_actualizada'
  | 'tecnico_asignado'
  | 'seguimiento_actualizado'
  | 'taller_seleccionado'
  | 'pago_confirmado';

export interface RealtimeWsEvent {
  tipo: RealtimeEventType | string;
  solicitud_id: number;
  payload?: Record<string, unknown>;
  occurred_at?: string;
}

export interface SolicitudWsConnection {
  events$: Observable<RealtimeWsEvent>;
  close(): void;
}

@Injectable({ providedIn: 'root' })
export class RealtimeWsService {
  connectSolicitud(opts: {
    solicitudId: number;
    token: string;
    apiUrl?: string;
  }): SolicitudWsConnection {
    const apiBase = (opts.apiUrl ?? environment.apiUrl).replace(/\/$/, '');
    const wsBase = apiBase.replace(/^http/i, 'ws');
    const url = `${wsBase}/ws/solicitudes/${opts.solicitudId}?token=${encodeURIComponent(opts.token)}`;

    const ws = new WebSocket(url);
    const subject = new Subject<RealtimeWsEvent>();
    let pingTimer: ReturnType<typeof setInterval> | undefined;

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(String(ev.data)) as RealtimeWsEvent;
        subject.next(data);
      } catch {
        /* ignore malformed */
      }
    };

    ws.onerror = () => {
      subject.error(new Error('WebSocket error'));
    };

    ws.onclose = () => {
      if (pingTimer) clearInterval(pingTimer);
      subject.complete();
    };

    ws.onopen = () => {
      pingTimer = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) ws.send('ping');
      }, 45000);
    };

    return {
      events$: subject.asObservable(),
      close: () => {
        if (pingTimer) clearInterval(pingTimer);
        ws.close();
        subject.complete();
      },
    };
  }
}
