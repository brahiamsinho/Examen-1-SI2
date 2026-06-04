import { ErrorHandler, Injectable, inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';

/** Muestra errores de Angular en pantalla (evita “pantalla negra” sin pista). */
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private readonly doc = inject(DOCUMENT);

  handleError(error: unknown): void {
    console.error('[App Error]', error);

    const root = this.doc.querySelector('app-root');
    if (!root || root.querySelector('.app-fatal-error')) {
      return;
    }

    const msg =
      error instanceof Error
        ? `${error.name}: ${error.message}`
        : String(error);

    const box = this.doc.createElement('div');
    box.className = 'app-fatal-error';
    box.setAttribute('role', 'alert');
    box.innerHTML = `
      <h1>Error en la aplicación</h1>
      <p>Ocurrió un fallo al cargar esta vista. Abre F12 → Consola para más detalle.</p>
      <pre></pre>
      <p><a href="/admin/login">Volver al login admin</a> · <a href="/">Inicio</a></p>
    `;
    const pre = box.querySelector('pre');
    if (pre) {
      pre.textContent = msg;
    }
    root.appendChild(box);
  }
}
