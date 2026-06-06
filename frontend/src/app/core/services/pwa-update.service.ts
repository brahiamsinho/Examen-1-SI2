import { Injectable, inject } from '@angular/core';
import { SwUpdate, VersionReadyEvent } from '@angular/service-worker';
import { filter } from 'rxjs';

/** Detecta nuevas versiones del service worker y ofrece recargar la PWA. */
@Injectable({ providedIn: 'root' })
export class PwaUpdateService {
  private readonly swUpdate = inject(SwUpdate);

  /** Emite cuando hay build nuevo listo para activar (solo prod + SW habilitado). */
  readonly versionReady$ = this.swUpdate.versionUpdates.pipe(
    filter((evt): evt is VersionReadyEvent => evt.type === 'VERSION_READY'),
  );

  get enabled(): boolean {
    return this.swUpdate.isEnabled;
  }

  activateUpdate(): Promise<boolean> {
    return this.swUpdate.activateUpdate();
  }

  checkForUpdate(): Promise<boolean> {
    if (!this.swUpdate.isEnabled) {
      return Promise.resolve(false);
    }
    return this.swUpdate.checkForUpdate();
  }
}
