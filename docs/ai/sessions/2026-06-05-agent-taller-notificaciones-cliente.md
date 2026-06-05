# Sesión 2026-06-05 — Notificaciones web taller desde acciones del cliente

## Objetivo
El panel web del taller debe recibir notificaciones in-app cuando sus clientes interactúan (sin push FCM por ahora).

## Cambios backend
- `eventos_servicio.py`: `_nombre_cliente`, `on_mensaje_cliente`, `on_pago_cliente`; textos con nombre del cliente en `on_solicitud_pendiente_taller`.
- `mensajes_solicitud/service.py`: al enviar mensaje como cliente → notifica también al responsable del taller.
- `pagos/service.py`: al confirmar pago (simulado o Stripe) → notifica al responsable del taller.

## Cambios frontend taller
- `taller-shell`: campana en topbar con contador de no leídas (polling 30s).
- `taller-notificaciones`: etiquetas por tipo; navegación a bandeja o mis solicitudes según tipo.
- Bandeja e historial: aceptan `?q=` para filtrar por ID de solicitud al abrir desde notificación.

## Eventos que llegan al taller (in-app)
| Evento | Tipo |
|--------|------|
| Cliente elige taller | SOLICITUD_PENDIENTE_TALLER |
| Cliente escribe en chat | MENSAJE_NUEVO |
| Cliente confirma pago | ESTADO_ACTUALIZADO |
| Técnico asignado / cambio estado | (ya existía) |

## Pendiente
- Push FCM / Web Push para taller web.
- Tests de integración tenant + mensajes → taller.
