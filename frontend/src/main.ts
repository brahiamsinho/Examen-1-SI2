import { registerLocaleData } from '@angular/common';
import { bootstrapApplication } from '@angular/platform-browser';
import localeEsBo from '@angular/common/locales/es-BO';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

registerLocaleData(localeEsBo);

bootstrapApplication(AppComponent, appConfig).catch((err) => {
  console.error(err);
  const root = document.querySelector('app-root');
  if (root) {
    root.innerHTML =
      '<div style="padding:2rem;font-family:system-ui;color:#f0f6fc;background:#05070a;min-height:100vh">' +
      '<h1 style="color:#fca5a5">Error al iniciar la aplicación</h1>' +
      '<p>Abre la consola del navegador (F12) para más detalle.</p>' +
      '<pre style="margin-top:1rem;padding:1rem;background:#131316;border-radius:8px;overflow:auto;font-size:0.85rem">' +
      String(err) +
      '</pre></div>';
  }
});
