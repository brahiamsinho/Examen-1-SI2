# CURRENT_STATE.md
# =========================================================
# Estado actual del proyecto
# Última actualización: 2026-04-22 (CU28 Angular taller + docs Ciclo 2 + badge móvil)
# =========================================================

## Estado: CICLO 1 base + dominio emergencias (Ciclo 2) operativo en dev ✅

## Lo que existe

### Backend FastAPI ✅
- [x] `core/` — config, database, security, dependencies
- [x] `modules/acceso`, `usuarios`, `vehiculos`, `talleres`, `bitacora`
- [x] `modules/portal_cliente/` — registro + mi-perfil + mis-vehículos (móvil cliente)
- [x] `modules/portal_taller/` — registro taller, mi-taller, técnicos (responsable)
- [x] `modules/portal_taller_emergencias/` — bandeja PENDIENTE, detalle incidente (CU25), aceptar/rechazar (CU26–27), disponibilidad (CU29), **asignar técnico (CU28)** e historial `solicitud_asignaciones_tecnico`; **CU30–CU31** historial de atenciones y comisiones (`comisiones_taller` + join `pagos`); permisos `solicitudes_taller:*`, `disponibilidad:gestionar`, `tecnicos:asignar`, `historial_atenciones:leer`, `comisiones:leer`; prefijo `/api/portal/taller/emergencias`
- [x] `modules/portal_tecnico_emergencias/` — CU32–CU35 (script 008): servicios asignados, ubicación cliente, actualizar estado (`solicitud_historial_estado`), mensajes vía `comunicaciones.service` + `mensajes_tecnico:*`; prefijo `/api/portal/tecnico/emergencias`
- [x] `main.py` — routers bajo `API_PREFIX` (p. ej. `/api`)
- [x] `migrations/init.sql` + seeds: `app/seeds/` — admin, cliente, taller, **técnico** (`python -m app.seeds`); vars `SEED_*` en `.env` raíz; credenciales cortas por defecto en `config.py` / `.env.example` (ej. `cli@test.com`, `taller@test.com`, `tec@test.com`)
- [x] Alembic baseline + `alembic stamp` tras init

### Frontend Angular ✅
- [x] Docker + nginx + proxy; environments; rutas lazy; landing; estilos globales oscuros
- [x] Portal **taller** — emergencias: bandeja, detalle incidente, aceptar/rechazar; **CU28** en UI: `TallerEmergenciasApiService` (`asignarTecnico`, `listarAsignacionesTecnico`) + bloque asignación en `taller-emergencias-incidente-detalle` (tras aceptar permanece en detalle y lista historial de asignaciones). Ver `frontend/src/app/core/services/taller-emergencias-api.service.ts`

### Mobile Flutter ✅
- [x] `mobile/.env` + **flutter_dotenv** (asset); `lib/core/config/app_env.dart` — `API_BASE_URL`, `APP_NAME`, timeouts opcionales
- [x] `lib/cliente/` — auth portal (login/registro/recuperar), shell, home, vehículos, perfil; Riverpod + go_router (`cliente/presentation/router/cliente_go_router.dart` registra también rutas globales)
- [x] `lib/tecnico/` — emergencias (servicios asignados, detalle, chat, etc.); splash, login, recuperar, shell; **tokens JWT en secure storage separados** (`tecnico_access_token` vía `core/network/tecnico_api_client.dart`)
- [x] Badge de estado cliente: colores distintos **Taller asignado** vs **Técnico asignado** (`estado_solicitud_badge.dart`)
- [x] `core/network/api_error.dart` compartido; `api_constants` con `portal/taller/mi-taller`, `tecnicos`, etc.

### Docker ✅
- [x] `docker-compose.yml` + override; `.env` raíz como fuente principal
- [x] **Postgres (init):** `backend/migrations/init.sql` + `0002`–`0004` + `0006` + **`0007_taller_operacion_permisos.sql`** (permisos `solicitudes_taller:*`, `disponibilidad:gestionar`, `tecnicos:asignar`, etc. y `rol_permiso` para `TALLER_RESPONSABLE` / `TECNICO`). Montado como `06_` en `docker-compose`. **BD ya creada:** ejecutar ese SQL a mano o `docker compose exec -i db psql ... < backend/migrations/0007_...sql`. La columna `tecnico_asignado_at` también está en `0003`. Ver `DECISIONS_LOG` **DEC-009**.

### Incidente resuelto (2026-04-22) — registro de emergencia (móvil) ❌→✅
- **Síntoma:** al crear o listar emergencias, el backend devolvía 500: `column "tecnico_asignado_at" of relation "solicitudes_emergencia" does not exist`.
- **Causa:** el modelo SQLAlchemy (`SolicitudEmergencia` en `emergencias/models.py`) y el portal taller asignan leen/escriben `tecnico_asignado_at`, pero en las migraciones SQL de fase 2 no se había añadido esa columna (solo `taller_id`, `tecnico_id`, `tiempo_estimado_min`, `finalizada_at`).
- **Reparación en repo:** columna añadida al `ALTER` de `0003`; parche idempotente `0006_tecnico_asignado_at.sql`; volumen de compose extendido. **Bases ya creadas** (volumen `postgres_data` no re-ejecuta init): aplicar una vez `ALTER TABLE solicitudes_emergencia ADD COLUMN IF NOT EXISTS tecnico_asignado_at TIMESTAMP;` o ejecutar el contenido de `0006`.

### Docs ✅
- [x] `AGENTS.md` (raíz)
- [x] `docs/ai/*` — visión, arquitectura, estado, handoff, próximos pasos, decisiones
- [x] `mobile/README.md` — `.env`, estructura `lib/cliente` / `lib/tecnico`, usuarios demo

## Lo que falta (priorizado)

### Inmediato
- [ ] Angular: auth completo, layout admin, CRUD/features sobre el lienzo
- [ ] Flutter: tests; registro cliente / flujos edge; refresh token si aplica
- [ ] Tests backend (pytest) ampliados

### Ciclo 2 (resto)
- [x] Flujo principal emergencias (cliente → taller → técnico) — ver `PROJECT_VISION.md` y `NEXT_STEPS.md`
- [ ] Notificaciones push en tiempo real
- [ ] Geolocalización avanzada / tracking
