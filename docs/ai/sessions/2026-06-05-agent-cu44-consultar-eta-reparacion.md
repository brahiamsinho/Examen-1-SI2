# Sesión 2026-06-05 — CU44 Consultar tiempo estimado de reparación

## Backend
- `GET /api/app/cliente/emergencias/{id}/seguimiento/eta`
- `SeguimientoETAService` → `service/seguimiento_eta.py`
- Schema `SolicitudEtaRead` + `EtaDisponibilidadEnum` (PENDIENTE, DISPONIBLE, NO_APLICABLE, HISTORICO)
- 403 si la solicitud existe pero no pertenece al cliente; 404 si no existe
- Tests: `backend/tests/test_cu44_seguimiento_eta.py`

## Mobile
- `fetchEtaReparacion` + `consultarEtaProvider` con caché `SharedPreferences` offline
- `EtaReparacionCu44Card` en pantalla Seguimiento + pull-to-refresh
- Duración legible: min / h min

## Verificación
1. Taller asigna técnico con `tiempo_estimado_min` o técnico pasa a EN_CAMINO (fallback 20 min).
2. Cliente → Seguimiento → bloque «Tiempo estimado de reparación».
3. Modo avión tras consulta previa → muestra caché con aviso offline.
