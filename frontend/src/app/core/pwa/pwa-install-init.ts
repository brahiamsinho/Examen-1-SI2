/** Captura `beforeinstallprompt` antes del bootstrap de Angular (el evento puede dispararse muy pronto). */
export interface DeferredPwaInstallPrompt {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

declare global {
  interface Window {
    __deferredPwaPrompt?: DeferredPwaInstallPrompt | null;
  }
}

export function initPwaInstallCapture(): void {
  if (typeof window === 'undefined') return;
  window.__deferredPwaPrompt = null;

  window.addEventListener('beforeinstallprompt', (event: Event) => {
    event.preventDefault();
    window.__deferredPwaPrompt = event as unknown as DeferredPwaInstallPrompt;
    window.dispatchEvent(new CustomEvent('ev-pwa-install-available'));
  });

  window.addEventListener('appinstalled', () => {
    window.__deferredPwaPrompt = null;
  });
}
