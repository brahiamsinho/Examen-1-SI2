# Sesión — WebSocket tiempo real

**Fecha:** 2026-06-04  
**Rama:** feature/mobile

## Objetivo

Implementar WebSocket para seguimiento en vivo de solicitudes de emergencia (Ciclo 4 / CU36–CU39).

## Backend

- Nuevo paquete `backend/app/modules/comunicacion_y_notificaciones/tiempo_real/`:
  - `bus.py` — suscriptores por `solicitud_id`
  - `publish.py` — cola en sesión SQLAlchemy + dispatch en `after_commit`
  - `auth_ws.py` — JWT query param + acceso cliente/técnico/taller
  - `router.py` — `WS /api/ws/solicitudes/{solicitud_id}?token=`
- Hooks en: `estado.py`, `ubicaciones.py`, `mensajes_solicitud/service.py`, `bandeja.py`, `asignaciones.py`
- Registrado en `main.py`

## Clientes

- **Mobile:** `web_socket_channel`, `SolicitudRealtimeWsClient`, providers Riverpod; seguimiento + mapa.
- **Angular taller:** `RealtimeWsService`, detalle incidente con badge «En vivo».
- **Infra:** `nginx.conf.template` + `proxy.conf.js` (`ws: true`).

## Pendiente

- Redis Pub/Sub para despliegue con múltiples workers.
- WS en cancelación cuando exista endpoint API.
- Tests integración auth WS con JWT real.

## Ampliación (misma sesión)

- Eventos `taller_seleccionado`, `pago_confirmado`.
- Mobile: chat, lista solicitudes, elegir taller, app técnico, app taller.
- `backend/tests/test_tiempo_real.py`.
