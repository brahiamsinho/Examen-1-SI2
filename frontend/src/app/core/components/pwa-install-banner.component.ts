import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { PwaInstallService } from '../services/pwa-install.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-pwa-install-banner',
  standalone: true,
  template: `
    @if (visible()) {
      <aside class="pwa-install" role="dialog" aria-labelledby="pwa-install-title">
        <div class="pwa-install__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none">
            <path
              d="M12 3v10m0 0l3.5-3.5M12 13l-3.5-3.5M5 15v2a2 2 0 002 2h10a2 2 0 002-2v-2"
              stroke="currentColor"
              stroke-width="1.75"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <div class="pwa-install__body">
          <p id="pwa-install-title" class="pwa-install__title">
            {{ iosMode() ? 'Instalá la app en tu iPhone' : 'Instalá Emergencias Vehiculares' }}
          </p>
          <p class="pwa-install__text">
            @if (iosMode()) {
              En Safari: tocá <strong>Compartir</strong> → <strong>Agregar a pantalla de inicio</strong>.
              Accedé al panel del taller como una app.
            } @else {
              Accedé más rápido al panel del taller: icono en el escritorio o celular, sin barra del
              navegador.
            }
          </p>
          <div class="pwa-install__actions">
            @if (!iosMode()) {
              <button type="button" class="pwa-install__primary" (click)="install()" [disabled]="installing()">
                {{ installing() ? 'Abriendo…' : 'Instalar app' }}
              </button>
            }
            <button type="button" class="pwa-install__secondary" (click)="dismiss()">
              {{ iosMode() ? 'Entendido' : 'Ahora no' }}
            </button>
          </div>
        </div>
        <button type="button" class="pwa-install__close" (click)="dismiss()" aria-label="Cerrar aviso">
          ×
        </button>
      </aside>
    }
  `,
  styles: [
    `
      .pwa-install {
        position: fixed;
        right: 1rem;
        bottom: 1rem;
        z-index: 9999;
        display: flex;
        gap: 0.85rem;
        align-items: flex-start;
        max-width: min(380px, calc(100vw - 2rem));
        padding: 1rem 1rem 1rem 0.95rem;
        border-radius: 16px;
        background: linear-gradient(145deg, #141b2e 0%, #0f1628 100%);
        border: 1px solid #2a3658;
        color: #e2e8f0;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
        animation: pwa-install-in 0.35s ease-out;
      }
      @keyframes pwa-install-in {
        from {
          opacity: 0;
          transform: translateY(12px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      .pwa-install__icon {
        flex-shrink: 0;
        display: grid;
        place-items: center;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
      }
      .pwa-install__body {
        flex: 1;
        min-width: 0;
      }
      .pwa-install__title {
        margin: 0 0 0.35rem;
        font-weight: 700;
        font-size: 0.95rem;
        line-height: 1.3;
      }
      .pwa-install__text {
        margin: 0 0 0.75rem;
        font-size: 0.82rem;
        line-height: 1.45;
        color: #94a3b8;
      }
      .pwa-install__text strong {
        color: #cbd5e1;
        font-weight: 600;
      }
      .pwa-install__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      .pwa-install__primary {
        border: none;
        border-radius: 8px;
        padding: 0.45rem 0.9rem;
        background: #f59e0b;
        color: #0b1020;
        font-weight: 700;
        font-size: 0.85rem;
        cursor: pointer;
      }
      .pwa-install__primary:disabled {
        opacity: 0.75;
        cursor: wait;
      }
      .pwa-install__secondary {
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.45rem 0.9rem;
        background: transparent;
        color: #cbd5e1;
        font-size: 0.85rem;
        cursor: pointer;
      }
      .pwa-install__close {
        position: absolute;
        top: 0.35rem;
        right: 0.45rem;
        border: none;
        background: transparent;
        color: #64748b;
        font-size: 1.35rem;
        line-height: 1;
        cursor: pointer;
        padding: 0.15rem 0.35rem;
      }
      @media (max-width: 480px) {
        .pwa-install {
          left: 1rem;
          right: 1rem;
        }
      }
    `,
  ],
})
export class PwaInstallBannerComponent implements OnInit, OnDestroy {
  private readonly pwaInstall = inject(PwaInstallService);
  private subs = new Subscription();

  readonly visible = signal(false);
  readonly iosMode = signal(false);
  readonly installing = signal(false);

  ngOnInit(): void {
    if (this.pwaInstall.isStandalone()) return;

    this.subs.add(
      this.pwaInstall.installAvailable$.subscribe((available) => {
        if (available) {
          this.iosMode.set(false);
          this.visible.set(true);
        }
      }),
    );

    this.subs.add(
      this.pwaInstall.iosHint$.subscribe((hint) => {
        if (hint && !this.pwaInstall.installAvailable$.value) {
          this.iosMode.set(true);
          this.visible.set(true);
        }
      }),
    );
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  async install(): Promise<void> {
    this.installing.set(true);
    try {
      await this.pwaInstall.promptInstall();
      this.visible.set(false);
    } finally {
      this.installing.set(false);
    }
  }

  dismiss(): void {
    this.pwaInstall.dismiss();
    this.visible.set(false);
  }
}
