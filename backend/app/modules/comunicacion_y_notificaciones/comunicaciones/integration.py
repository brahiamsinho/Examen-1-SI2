"""Tiempo real por solicitud (WebSocket).

Implementado en `comunicacion_y_notificaciones/tiempo_real/`:
- `WS /api/ws/solicitudes/{solicitud_id}?token=<JWT>`
- Bus en memoria + publicación tras `commit` (SQLAlchemy `after_commit`)
- Eventos: estado_incidente, ubicacion_tecnico, mensaje_nuevo, bandeja_actualizada,
  tecnico_asignado, seguimiento_actualizado

Para múltiples réplicas backend en producción: sustituir el bus por Redis Pub/Sub.
"""
