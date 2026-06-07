import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import type { DeferredPwaInstallPrompt } from '../pwa/pwa-install-init';

const DISMISS_KEY = 'ev-pwa-install-dismissed-until';
const DISMISS_DAYS = 7;

@Injectable({ providedIn: 'root' })
export class PwaInstallService {
  private deferredPrompt: DeferredPwaInstallPrompt | null = null;

  readonly installAvailable$ = new BehaviorSubject<boolean>(false);
  readonly iosHint$ = new BehaviorSubject<boolean>(false);

  constructor() {
    if (typeof window === 'undefined') return;
    if (this.isStandalone()) return;
    if (this.isDismissed()) return;

    if (window.__deferredPwaPrompt) {
      this.deferredPrompt = window.__deferredPwaPrompt;
      this.installAvailable$.next(true);
    }

    window.addEventListener('ev-pwa-install-available', () => {
      if (this.isDismissed()) return;
      this.deferredPrompt = window.__deferredPwaPrompt ?? null;
      if (this.deferredPrompt) {
        this.installAvailable$.next(true);
        this.iosHint$.next(false);
      }
    });

    window.addEventListener('beforeinstallprompt', (event: Event) => {
      event.preventDefault();
      this.deferredPrompt = event as unknown as DeferredPwaInstallPrompt;
      window.__deferredPwaPrompt = this.deferredPrompt;
      this.installAvailable$.next(true);
      this.iosHint$.next(false);
    });

    window.addEventListener('appinstalled', () => {
      this.deferredPrompt = null;
      window.__deferredPwaPrompt = null;
      this.installAvailable$.next(false);
      this.iosHint$.next(false);
      localStorage.removeItem(DISMISS_KEY);
    });

    if (this.isIosSafari()) {
      this.iosHint$.next(true);
    }
  }

  isStandalone(): boolean {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as Navigator & { standalone?: boolean }).standalone === true
    );
  }

  isIosSafari(): boolean {
    const ua = window.navigator.userAgent;
    const isAppleMobile = /iPad|iPhone|iPod/.test(ua);
    const isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS/.test(ua);
    return isAppleMobile && isSafari;
  }

  async promptInstall(): Promise<'accepted' | 'dismissed' | 'unavailable'> {
    const prompt = this.deferredPrompt;
    if (!prompt) return 'unavailable';
    await prompt.prompt();
    const { outcome } = await prompt.userChoice;
    this.deferredPrompt = null;
    this.installAvailable$.next(false);
    return outcome;
  }

  dismiss(): void {
    const until = Date.now() + DISMISS_DAYS * 24 * 60 * 60 * 1000;
    localStorage.setItem(DISMISS_KEY, String(until));
    this.installAvailable$.next(false);
    this.iosHint$.next(false);
  }

  private isDismissed(): boolean {
    const raw = localStorage.getItem(DISMISS_KEY);
    if (!raw) return false;
    const until = Number(raw);
    if (!Number.isFinite(until) || Date.now() >= until) {
      localStorage.removeItem(DISMISS_KEY);
      return false;
    }
    return true;
  }
}
