import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { initializeApp, type FirebaseApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, type MessagePayload, type Messaging } from 'firebase/messaging';
import { Subject, firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import type { NotificacionPortal } from '../models/notificacion.models';

const SW_PATH = '/firebase-cloud-messaging-push-scope/firebase-messaging-sw.js';
const SW_SCOPE = '/firebase-cloud-messaging-push-scope/';

@Injectable({ providedIn: 'root' })
export class FcmService {
  private readonly http = inject(HttpClient);

  /** Emite cuando llega un push en primer plano (para refrescar campana). */
  readonly foregroundMessage$ = new Subject<void>();

  private app: FirebaseApp | null = null;
  private messaging: Messaging | null = null;
  private activePortal: NotificacionPortal | null = null;
  private registeredToken: string | null = null;
  private initPromise: Promise<void> | null = null;

  get isEnabled(): boolean {
    return environment.firebase.enabled;
  }

  async activate(portal: NotificacionPortal): Promise<void> {
    if (!this.isEnabled || typeof window === 'undefined') {
      return;
    }
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      return;
    }
    this.activePortal = portal;
    if (!this.initPromise) {
      this.initPromise = this.bootstrapFirebase();
    }
    await this.initPromise;
    await this.registerCurrentToken();
  }

  async deactivate(): Promise<void> {
    if (!this.isEnabled || !this.registeredToken || !this.activePortal) {
      this.registeredToken = null;
      this.activePortal = null;
      return;
    }
    const token = this.registeredToken;
    const portal = this.activePortal;
    this.registeredToken = null;
    this.activePortal = null;
    const url = this.fcmUrl(portal);
    try {
      await firstValueFrom(
        this.http.request('DELETE', url, { body: { token, platform: 'web' } }),
      );
    } catch {
      // Token inválido o sesión ya cerrada.
    }
  }

  private fcmUrl(portal: NotificacionPortal): string {
    return portal === 'taller'
      ? `${environment.apiUrl}/app/taller/dispositivos/fcm`
      : `${environment.apiUrl}/admin/dispositivos/fcm`;
  }

  private async bootstrapFirebase(): Promise<void> {
    const cfg = environment.firebase;
    this.app = initializeApp({
      apiKey: cfg.apiKey,
      authDomain: cfg.authDomain,
      projectId: cfg.projectId,
      storageBucket: cfg.storageBucket,
      messagingSenderId: cfg.messagingSenderId,
      appId: cfg.appId,
      measurementId: cfg.measurementId || undefined,
    });
    this.messaging = getMessaging(this.app);
    onMessage(this.messaging, (payload) => {
      void this.showForegroundNotification(payload);
      this.foregroundMessage$.next();
    });
  }

  private resolveNotificationUrl(data: Record<string, string>, portal: NotificacionPortal | null): string {
    const p = data['portal'] ?? portal ?? '';
    if (p === 'taller') {
      return '/taller/panel/emergencias/solicitudes';
    }
    if (p === 'admin') {
      return '/admin/panel';
    }
    return portal === 'taller' ? '/taller/panel/emergencias/solicitudes' : '/admin/panel';
  }

  private async showForegroundNotification(payload: MessagePayload): Promise<void> {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return;
    }
    if (Notification.permission !== 'granted') {
      return;
    }

    const title = payload.notification?.title ?? 'EmergenciasViales';
    const body = payload.notification?.body ?? '';
    const data = Object.fromEntries(
      Object.entries(payload.data ?? {}).map(([k, v]) => [k, String(v)]),
    ) as Record<string, string>;
    const targetPath = this.resolveNotificationUrl(data, this.activePortal);
    const icon = '/assets/icons/icon-192x192.png';
    const tag = data['tipo'] ?? 'emergencias';

    const onClickNavigate = () => {
      window.focus();
      window.location.assign(targetPath);
    };

    try {
      const registration = await navigator.serviceWorker.getRegistration(SW_SCOPE);
      if (registration) {
        await registration.showNotification(title, {
          body,
          icon,
          tag,
          data: { ...data, targetPath },
        });
        return;
      }
    } catch {
      // fallback abajo
    }

    const notification = new Notification(title, { body, icon, tag, data });
    notification.onclick = () => {
      notification.close();
      onClickNavigate();
    };
  }

  private async registerCurrentToken(): Promise<void> {
    if (!this.messaging || !this.activePortal) {
      return;
    }
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      return;
    }
    const registration = await navigator.serviceWorker.register(SW_PATH, { scope: SW_SCOPE });
    const token = await getToken(this.messaging, {
      vapidKey: environment.firebase.vapidKey,
      serviceWorkerRegistration: registration,
    });
    if (!token || token === this.registeredToken) {
      this.registeredToken = token;
      return;
    }
    await firstValueFrom(
      this.http.post(this.fcmUrl(this.activePortal), { token, platform: 'web' }),
    );
    this.registeredToken = token;
  }
}
