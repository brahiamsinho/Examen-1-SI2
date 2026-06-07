# Sesión 2026-06-06 — Fix push FCM mobile

## Problema reportado
Push no llegaba a la app Flutter aunque el token FCM se registraba (`POST /api/app/cliente/dispositivos/fcm` → 204).

## Causas raíz
1. **`FCM_ENABLED=false`** en `.env` raíz → el backend guardaba notificaciones en DB pero **no enviaba** FCM (sin logs `FCM multicast enviado`).
2. **`backend/firebase-credentials.json` era un directorio vacío**, no el JSON de cuenta de servicio → aunque FCM estuviera activo, Firebase Admin no podía inicializarse.

## Correcciones
- Copiado JSON real desde credenciales del usuario → `backend/firebase-credentials.json`.
- `.env`: `FCM_ENABLED=true`.
- Backend `fcm_client.py`: `AndroidConfig` con `channel_id=emergencias_high_importance`.
- Mobile `AndroidManifest.xml`: meta-data canal e icono por defecto FCM.
- Mobile `fcm_message_listener.dart`: inicializar notificaciones locales **antes** de escuchar `onMessage` (evita race).
- Mobile `fcm_registration.dart`: logs debug + `onTokenRefresh` re-registra token.

## QA sugerido
1. `docker compose up -d backend` (recrear contenedor tras cambiar `.env`).
2. Mobile: cerrar sesión → login cliente → aceptar permiso notificaciones.
3. Debe llegar push «Bienvenido a Emergencias Viales» al primer registro de token.
4. Logs backend: `FCM multicast enviado: success=1 failure=0`.
5. **Nota CU37:** elegir taller notifica al **responsable del taller** (web), no al cliente mobile.
