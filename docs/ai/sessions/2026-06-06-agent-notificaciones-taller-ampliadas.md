# Sesión 2026-06-06 — Notificaciones ampliadas al taller

## Problema
El portal taller solo recibía push/in-app al llegar una solicitud nueva (CU37). Faltaban avisos operativos durante el servicio.

## Cambios backend
- Helper `notificar_responsable_taller_por_solicitud` — resuelve taller + `bandeja_id` en FCM.
- **Estado técnico** (`EN_CAMINO`, `EN_ATENCION`, `FINALIZADA`): notifica al responsable.
- **Chat** cliente/técnico: copia de supervisión al responsable.
- **Pago confirmado** (simulado + Stripe): notifica al responsable con monto.
- CU37: `bandeja_id` en payload FCM.
- `GET /app/taller/emergencias/solicitudes/{id}/bandeja-id` para deep-link.

## Cambios frontend
- Campana taller: navega al detalle de bandeja cuando la notificación trae `solicitud_id`.

## Verificación manual
1. `docker compose up -d --build backend`
2. Portal taller con FCM activo (`FCM_ENABLED=true`, permiso navegador).
3. Flujo: asignar técnico → técnico marca en camino / atención / finalizada → chat → pago.
4. Campana debe mostrar cada evento; click abre detalle de solicitud.
