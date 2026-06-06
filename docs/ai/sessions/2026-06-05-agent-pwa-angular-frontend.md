# Sesión 2026-06-05 — PWA Angular frontend

## Implementado
- `@angular/pwa` + `@angular/service-worker` en `frontend/`.
- `src/manifest.webmanifest` — branding dark (#0B1020), `start_url` `/taller/panel`, shortcuts bandeja/reportes.
- `ngsw-config.json` — prefetch assets; cache freshness solo `/api/public/**`.
- `provideServiceWorker` en `app.config.ts` (solo producción).
- Iconos PWA en `src/assets/icons/`.
- `PwaUpdateService` + banner «Actualizar ahora» en `AppComponent`.
- `nginx.conf.template` — sin cache largo en `ngsw-worker.js`, `ngsw.json`, `manifest.webmanifest`.

## Probar
1. `docker compose up -d --build frontend` (build prod incluye SW).
2. Chrome → `http://localhost/taller/panel` → menú ⋮ → **Instalar aplicación**.
3. DevTools → Application → Manifest / Service Workers.
4. `ng serve` **no** registra SW (`isDevMode()`); usar build prod o `ng serve --configuration=production`.

## Pendiente
- HTTPS en staging/prod (recomendado para push web futuro).
- Push web PWA (FCM web) — fase 2.
