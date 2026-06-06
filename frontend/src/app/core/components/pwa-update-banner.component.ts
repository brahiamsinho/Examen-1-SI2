import { Component, OnInit, inject, signal } from '@angular/core';
import { PwaUpdateService } from '../services/pwa-update.service';

@Component({
  selector: 'app-pwa-update-banner',
  standalone: true,
  template: `
    @if (visible()) {
      <div class="pwa-update" role="status" aria-live="polite">
        <span>Hay una nueva versión de la aplicación.</span>
        <button type="button" class="pwa-update__btn" (click)="reload()" [disabled]="activating()">
          {{ activating() ? 'Actualizando…' : 'Actualizar ahora' }}
        </button>
        <button type="button" class="pwa-update__dismiss" (click)="dismiss()" aria-label="Cerrar aviso">
          ×
        </button>
      </div>
    }
  `,
  styles: [
    `
      .pwa-update {
        position: fixed;
        bottom: 1rem;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
        max-width: min(560px, calc(100vw - 2rem));
        padding: 0.75rem 1rem;
        border-radius: 12px;
        background: #141b2e;
        border: 1px solid #2a3658;
        color: #e2e8f0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
        font-size: 0.9rem;
      }
      .pwa-update__btn {
        border: none;
        border-radius: 8px;
        padding: 0.45rem 0.85rem;
        background: #38bdf8;
        color: #0b1020;
        font-weight: 600;
        cursor: pointer;
      }
      .pwa-update__btn:disabled {
        opacity: 0.7;
        cursor: wait;
      }
      .pwa-update__dismiss {
        margin-left: auto;
        border: none;
        background: transparent;
        color: #94a3b8;
        font-size: 1.25rem;
        line-height: 1;
        cursor: pointer;
        padding: 0 0.25rem;
      }
    `,
  ],
})
export class PwaUpdateBannerComponent implements OnInit {
  private readonly pwa = inject(PwaUpdateService);

  readonly visible = signal(false);
  readonly activating = signal(false);

  ngOnInit(): void {
    if (!this.pwa.enabled) return;
    this.pwa.versionReady$.subscribe(() => this.visible.set(true));
    void this.pwa.checkForUpdate();
  }

  async reload(): Promise<void> {
    this.activating.set(true);
    try {
      await this.pwa.activateUpdate();
      document.location.reload();
    } catch {
      this.activating.set(false);
    }
  }

  dismiss(): void {
    this.visible.set(false);
  }
}
