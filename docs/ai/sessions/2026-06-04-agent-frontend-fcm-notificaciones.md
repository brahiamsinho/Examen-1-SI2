# Sesión 2026-06-04 — Frontend FCM + notificaciones in-app

## Objetivo
Implementar notificaciones in-app y push FCM en el frontend Angular (portal taller y admin), integrando credenciales Firebase del proyecto `transporte-si2`.

## Hecho
- Copia de credenciales (gitignored): `backend/firebase-credentials.json`, `mobile/android/app/google-services.json`.
- Migración `0027_taller_fcm_notificaciones.sql`.
- Endpoints backend comunicaciones para taller y admin.
- `notificar_responsable_taller` al seleccionar taller (CU37).
- Frontend: servicios, campana, service worker aislado de ngsw, sync env Firebase.

## Activación local
1. En `.env` raíz:
   - `FCM_ENABLED=true`
   - `FIREBASE_WEB_ENABLED=true`
   - Claves `FIREBASE_WEB_*` (ver `.env.example` o `FIREBASE-CREDENTIALS.md` del paquete de credenciales).
2. `cd frontend && npm run env:sync`
3. Reiniciar backend (aplicar migración 0027 si DB ya existía: ejecutar SQL o recrear volúmenes dev).
4. Login en `/taller/panel` o `/admin/panel` → aceptar permiso de notificaciones del navegador.

## Archivos clave
- `frontend/src/app/core/services/fcm.service.ts`
- `frontend/src/app/shared/notifications/notification-bell.component.ts`
- `frontend/public/firebase-cloud-messaging-push-scope/firebase-messaging-sw.js`
- `backend/app/modules/comunicacion_y_notificaciones/comunicaciones/router.py`
