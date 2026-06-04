# Sesión 2026-06-02 — CU37 selección taller + CU36 polling ubicación

## Implementado

### CU37 — Cliente elige taller (backend)
- `GET /api/app/cliente/emergencias/{id}/talleres-candidatos` — ranking IA6 filtrado por `tenant_id`.
- `POST /api/app/cliente/emergencias/{id}/seleccionar-taller` — bandeja PENDIENTE solo para el taller elegido; estado → `EN_REVISION`.
- `crear_solicitud` ya **no** inserta bandeja en todos los talleres (seeds demo siguen usando `insert_bandeja_pendiente_por_cada_taller` explícito).
- Servicio: `backend/app/modules/incidentes/emergencias/service/seleccion_taller.py`.
- Repo: `ensure_bandeja_pendiente_para_taller`, `expirar_todas_bandeja_pendientes`.

### CU37 — Mobile
- Pantalla `emergencia_seleccion_taller_screen.dart`.
- Ruta `/cliente/app/emergencias/solicitudes/:sid/seleccionar-taller`.
- Wizard paso final: CTA principal «Elegir taller».

### CU36 — Mobile
- `emergencia_ubicacion_tecnico_screen.dart`: polling cada 12 s + botón refresh manual.

## Probar
1. Cliente `carlos.vega@sc-demo.test` / `scdemo1`, org `demo-sc`.
2. Crear emergencia con ubicación → «Elegir taller» → confirmar → seguimiento.
3. Tras asignación técnico y compartir GPS: pantalla ubicación técnico debe actualizar sola.

## Pendiente opcional
- WebSocket en lugar de polling (CU36 “tiempo real” estricto).
- Tests pytest integración CU37.

## Documentación PUDS / memoria
- Sincronizado en **2026-05-28** vía `docs/ai/sessions/2026-05-28-agent-memoria-ciclo4-sync.md` (`CICLO4_*`, `CURRENT_STATE`, `HANDOFF`, `NEXT_STEPS`).
