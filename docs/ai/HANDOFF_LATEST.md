# HANDOFF_LATEST.md
# =========================================================
# Handoff para el próximo agente/sesión
# Fecha: 2026-04-23
# =========================================================

## Normativa

**`AGENTS.md`** (raíz del repo): contrato de agente, PUDS, UI/UX, seguridad y **obligación de mantener `docs/ai/`** tras cambios relevantes.

## Qué es el proyecto

Plataforma de **emergencias vehiculares**: clientes, talleres, técnicos, auditoría. Stack: **FastAPI + PostgreSQL + Angular 17 + Flutter + Docker**.

## Cambios recientes (2026-04-23) — Validación completa módulo IA ✅

Todos los endpoints del módulo `ai/` fueron probados en Swagger con respuestas **200** correctas:

| Endpoint | Tipo | Estado |
|---|---|---|
| `POST /api/ai/audio/transcribe` | Worker `ai-inference` | ✅ |
| `POST /api/ai/images/analyze` | Worker `ai-inference` (YOLO detect/classify) | ✅ |
| `POST /api/ai/incidents/classify` | Reglas backend | ✅ |
| `POST /api/ai/incidents/structured-summary` | Reglas backend | ✅ |
| `POST /api/ai/incidents/prioritize` | Reglas backend | ✅ |
| `POST /api/ai/assignment/rank` | Reglas + consulta BD | ✅ |

- `/incidents/prioritize` detectó correctamente "vía rápida / carretera" y "lenguaje de alto riesgo" para prioridad `ALTA`.
- `/assignment/rank` retornó el taller seed (`Taller Demo Emergencias`, id=1) con score `0.857`.
- El stack completo levantado con: `docker compose --profile ai up -d --build`.
- Con modelo Colab propio: `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build`.

## Cambios recientes (2026-04-23) — IA modular + Docker

- **Backend:** módulo `backend/app/modules/ai/` — rutas bajo `{API_PREFIX}/ai/...` (p. ej. análisis de imagen/audio), cliente HTTP a servicio interno, reglas y prioridad; requiere permiso **`ai:inferir`** para endpoints de inferencia. Variables `AI_ENABLED`, `AI_INFERENCE_BASE_URL`, `AI_INFERENCE_STUB`, timeouts y límites de upload en `.env` raíz (ver `.env.example`).
- **Worker `ai-inference`:** contenedor en `services/ai-inference/` (FastAPI + Uvicorn :8080). Rutas internas p. ej. `POST /internal/vision/analyze`. **Perfil Compose `ai`:** sin `docker compose --profile ai` el servicio no arranca.
- **Modelo custom (Colab → YOLOv8-cls):** archivo local `backend/incidentes_emergencias_v1.pt` (no versionado). Override `docker-compose.ai-custom-model.yml` monta el `.pt` y fija `YOLO_TASK=classify`, `YOLO_IMGSZ=224`.
- **Comando stack completo con IA + modelo propio:**  
  `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build`  
  Tras `down -v --rmi all`, el primer arranque puede tardar varios minutos (build, Postgres healthy, descarga de pesos al volumen de caché del worker).
- **`.env`:** no duplicar `AI_ENABLED` / `AI_INFERENCE_BASE_URL`; la última línea suele prevalecer y deja IA “apagada” → **503** en el backend aunque el worker exista.
- **Bug corregido:** Ultralytics puede exponer `probs.top5` como **lista**; el worker hacía `.cpu()` sobre eso → **500** y **502** aguas arriba. Parche en `services/ai-inference/app/main.py` (`_yolo_classify`). Tras tocar el worker: `--build --force-recreate ai-inference`.
- **Sesión detallada:** `docs/ai/sessions/2026-04-23-agent-ia-docker-worker-env-ultralytics.md`.

## Cambios recientes (2026-04-22) — plan emergencia → taller → técnico

- **Angular — CU28 en portal taller:** `TallerEmergenciasApiService` expone `POST .../solicitudes/{id}/asignar-tecnico` y `GET .../asignaciones`. Pantalla detalle de incidente (`taller-emergencias-incidente-detalle`): tras **aceptar** la solicitud ya no redirige a la bandeja; recarga el detalle y muestra historial de asignaciones + selector de técnico activo (lista desde `TallerApiService.listTecnicos()`). Permiso `tecnicos:asignar`.
- **Docs:** `PROJECT_VISION.md` — Ciclo 2 emergencias como en producto; nota sobre nomenclatura «ciclo 3 fase n» en código. `NEXT_STEPS.md` — checklist emergencias.
- **Flutter cliente:** `EstadoSolicitudBadge` diferencia color **TALLER_ASIGNADO** vs **TECNICO_ASIGNADO**.
- **Postgres (verificación):** columna `tecnico_asignado_at` presente en entornos con init/migraciones al día.

## Cambios recientes (2026-04-22)

- **Base de datos — `tecnico_asignado_at`:** Alineada con el modelo `SolicitudEmergencia` y el asigna-técnico en portal taller. En **migraciones repo:** `0003` incluye `ADD COLUMN ... tecnico_asignado_at`, `0006` es parche idempotente, `docker-compose` monta `0006` como `05_tecnico_asignado_at.sql`. **Volúmenes ya inicializados:** no re-ejecutan init; correr en Postgres: `backend/migrations/0006_tecnico_asignado_at.sql` o el `ALTER` equivalente. Detalle: `DECISIONS_LOG` **DEC-009** y `CURRENT_STATE` (incidente móvil 500 al registrar emergencia).
- **Nota con scripts manuales:** Puede existir `scripts/007_fase2_asignacion_tecnico.sql` u otros SQL fuera de `docker-entrypoint-initdb.d`; la fuente de verdad para Docker local sigue siendo `backend/migrations/*` mapeada en `docker-compose.yml`.

## Cambios recientes (2026-04-21)

- **Backend ciclo 3 fase 1 (taller):** módulo `backend/app/modules/portal_taller_emergencias/` — bandeja, detalle incidente, aceptar/rechazar, disponibilidad. Router bajo `{API_PREFIX}/portal/taller/emergencias`. Requiere tablas/permisos de `scripts/006_fase1_taller_bandeja_disponibilidad.sql`. Seed `ensure_baseline_rol_permisos` asigna a `TALLER_RESPONSABLE` los códigos `solicitudes_taller:*`, `disponibilidad:gestionar` y `tecnicos:asignar` si existen en `permisos`.
- **Backend ciclo 3 fase 2 (taller, CU28):** `POST .../solicitudes/{id}/asignar-tecnico`, `GET .../solicitudes/{id}/asignaciones`. Requiere `scripts/007_fase2_asignacion_tecnico.sql` y columna `tecnico_asignado_at` en `solicitudes_emergencia`.
- **Backend ciclo 3 fase 3 (técnico):** módulo `portal_tecnico_emergencias` — `GET /servicios-asignados`, `GET /solicitudes/{id}/ubicacion`, `PATCH /solicitudes/{id}/estado`, mensajes en `/{id}/mensajes` (misma URL que antes). Permisos script 008 + `servicios_tecnico:leer` (007). Mensajes técnico migrados desde `comunicaciones.router`. Seed `ensure_baseline_rol_permisos` amplía rol `TECNICO`.
- **Backend ciclo 3 fase 4 (taller):** en `portal_taller_emergencias`: `GET /historial-atenciones`, `GET /comisiones`, `GET /comisiones/resumen`. Requiere `scripts/009_fase4_historial_comisiones.sql`. Modelo `ComisionTaller`.

## Cambios recientes (2026-04-19)

- **Mobile:** módulos renombrados a `lib/cliente/` y `lib/tecnico/` (sin `_ciclo1`). Config por **`mobile/.env`** (`flutter_dotenv`). Flujo técnico: login con validación de roles `TECNICO` / `TALLER_RESPONSABLE`, perfil vía `/auth/me` + portal taller o listado técnicos según rol; sesión técnica con tokens **independientes** del cliente.
- **Backend seeds:** usuario demo **técnico** (`dev_tecnico.py`); credenciales de ejemplo **cortas** en `config.py` y `.env.example` (`cli@test.com`, `taller@test.com`, `tec@test.com`, etc.). `main.py` lifespan incluye `SEED_TECNICO_ON_START`.
- **Docs / README:** `mobile/README.md` y sección móvil del `README.md` raíz actualizados.

## Rutas y archivos clave

| Área | Dónde mirar |
|------|-------------|
| API móvil cliente | `backend/app/modules/portal_cliente/` |
| API portal taller | `backend/app/modules/portal_taller/` |
| API taller emergencias (bandeja / CU25–29) | `backend/app/modules/portal_taller_emergencias/` |
| API técnico emergencias (CU32–35) | `backend/app/modules/portal_tecnico_emergencias/` |
| IA (inferencia + reglas) | `backend/app/modules/ai/`; worker `services/ai-inference/app/main.py` |
| Router Flutter | `mobile/lib/cliente/presentation/router/cliente_go_router.dart` |
| Env móvil | `mobile/.env` + `lib/core/config/app_env.dart` |
| Seeds | `backend/app/seeds/__main__.py`, `dev_*.py` |

## Próximo paso sugerido

1. **Módulo IA ya validado** — no requiere cambios. El stack funciona con `docker compose --profile ai up -d --build`.
2. Continuar con **Angular:** auth completo (guard/interceptor), layout admin, pantallas CRUD.
3. Continuar con **Flutter:** tests unitarios/widget, pulir UX, refresh token.
4. Ampliar **tests pytest** en backend (cobertura endpoints IA + emergencias).
5. Tras un `git pull`, si el backend falla con columna `tecnico_asignado_at` inexistente, aplicar `0006` a la BD.
6. `docker compose exec backend python -m app.seeds` si la BD no tiene usuarios demo.
7. `mobile/.env` con `API_BASE_URL` alcanzable desde el dispositivo → `flutter run` en `mobile/`.

## Docker / .env raíz

Compose carga `.env` del repo; `DATABASE_URL`, `SECRET_KEY`, `SEED_*`, **`AI_*`**. Ver `.env.example` raíz. **No duplicar claves** de IA en el mismo archivo.
