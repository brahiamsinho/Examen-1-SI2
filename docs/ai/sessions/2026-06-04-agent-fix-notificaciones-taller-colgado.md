# Sesión 2026-06-04 — Fix página Notificaciones taller colgada

## Problema reportado
- Ruta `/taller/panel/comunicacion/notificaciones` permanecía en «Cargando…».
- La campana del header (`NotificationBellComponent`) sí mostraba notificaciones.

## Diagnóstico
- Mismo endpoint backend (`GET /api/app/taller/notificaciones`).
- La página usaba `TallerComunicacionApiService` con polling `setInterval` propio y **sin** `ChangeDetectionStrategy.OnPush` + `markForCheck`, patrón estándar en el resto del portal taller.
- Posible race: múltiples `reload()` concurrentes sin `switchMap`.

## Cambios
- `taller-notificaciones.component.ts`: OnPush, signal `loading`, `Subject` + `switchMap`, `NotificacionesApiService`, refresh vía FCM foreground e intervalo 60s (alineado a campana).
- Navegación al abrir notificación: `resolveBandejaId` como en la campana.
- `notificacion.models.ts`: añadido tipo `SOLICITUD_PENDIENTE_TALLER`.

## Verificación pendiente
- Rebuild frontend Docker y probar filtros Todas/No leídas + clic en fila.
