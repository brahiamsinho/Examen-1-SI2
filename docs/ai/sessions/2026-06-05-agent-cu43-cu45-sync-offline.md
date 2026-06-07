# Sesión 2026-06-05 — CU43 + CU45 sync offline mobile

## Objetivo
Implementar en paralelo:
- **CU45:** registrar emergencia offline (borrador local en wizard).
- **CU43:** sincronizar cola al reconectar con idempotencia backend.

## Backend
- Migración `0022_client_request_id_cu43.sql`: columna `client_request_id UUID` + índice único `(cliente_id, client_request_id)`.
- Modelo `SolicitudEmergencia.client_request_id`.
- Schema `SolicitudEmergenciaCreateIn.client_request_id`.
- `crear_solicitud`: si existe mismo `client_request_id` para el cliente → devuelve solicitud existente (replay seguro).
- Test: `backend/tests/test_emergencias_client_request_id.py`.

## Mobile
- Deps: `connectivity_plus`, `hive`, `hive_flutter`, `uuid`.
- `SolicitudDraft` + `SolicitudDraftRepo` (Hive JSON).
- `SyncPendientes` — replay ordenado: create → ubicación → foto → audio → texto.
- `SyncOrquestador` — escucha red, backoff exponencial, pausa en 401.
- Wizard: fallback offline en pasos CU11–15; banner modo sin conexión.
- `EmergenciasMisSolicitudesScreen`: panel sync + lista borradores + botón manual.
- `OfflineSyncBootstrap` en `ClienteAppShell`.

## Verificación local
1. `docker compose exec backend psql ...` o reiniciar backend para migración 0022.
2. `cd mobile && flutter pub get && flutter run`.
3. Modo avión → crear emergencia → completar wizard → ver borrador en Mis solicitudes.
4. Restaurar red → sync automático o «Sincronizar ahora» → solicitud en servidor sin duplicar.

## Pendiente opcional
- Tests integración pytest idempotencia con DB.
- Omitir paso final y marcar `readyToSync` sin texto.
- Web: Hive no inicializado en `kIsWeb` (offline solo nativo por ahora).
