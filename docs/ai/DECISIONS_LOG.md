# DECISIONS_LOG.md
# =========================================================
# Decisiones técnicas tomadas y su justificación
# =========================================================

## DEC-001 — SQLAlchemy async con asyncpg
**Fecha:** 2026-04-11
**Decisión:** Usar SQLAlchemy 2.0 con asyncio + asyncpg (no psycopg2)
**Por qué:** FastAPI es async. Usar un driver síncrono bloquearía el event loop en
cada query, eliminando el beneficio de async. asyncpg es el driver PostgreSQL
async nativo más rápido para Python.

## DEC-002 — JWT con JTI en tabla sesiones
**Fecha:** 2026-04-11
**Decisión:** Almacenar el JTI (JWT ID) de cada refresh token en la tabla `sesiones`
**Por qué:** JWT puro es stateless y no se puede revocar. Al almacenar el JTI en BD
podemos marcar tokens individuales como REVOCADOS sin invalidar toda la sesión del usuario.

## DEC-003 — Soft delete para usuarios
**Fecha:** 2026-04-11
**Decisión:** No eliminar usuarios físicamente — cambiar estado a INACTIVO
**Por qué:** 
1. La bitácora referencia usuarios (FK ON DELETE SET NULL)
2. Los vehículos referencian clientes — eliminar el usuario rompería la cadena
3. El historial de auditoría debe mantenerse intacto

## DEC-004 — init.sql vs Alembic
**Fecha:** 2026-04-11
**Decisión:** Usar `init.sql` en `docker-entrypoint-initdb.d/` para el schema inicial
**Por qué:** Para el Ciclo 1 es más directo. PostgreSQL ejecuta este script solo cuando
el volumen está vacío (primera vez). Para Ciclo 2+, agregar Alembic para migraciones incrementales.

## DEC-005 — Angular standalone (sin NgModules)
**Fecha:** 2026-04-11
**Decisión:** Usar Angular 17 standalone components y functional guards/interceptors
**Por qué:** NgModules son legacy en Angular 17+. Standalone reduce boilerplate,
mejora tree-shaking y es el camino oficial de Angular desde v17.

## DEC-006 — Función centralizada de bitácora
**Fecha:** 2026-04-11
**Decisión:** Crear `bitacora/service.py::registrar_accion()` como único punto de escritura
**Por qué:** Si cada módulo escribe directamente a la tabla, es difícil cambiar
el esquema de auditoría sin tocar todos los módulos. Centralizar facilita
agregar campos, cambiar transporte (ej: a cola de mensajes) o formatear logs.

## DEC-007 — Flutter con Dio (no http)
**Fecha:** 2026-04-11
**Decisión:** Usar Dio sobre el paquete `http` estándar
**Por qué:** Dio tiene interceptors nativos (para JWT), timeout configurable,
FormData, y mejor manejo de errores. Para una app con autenticación,
es la opción estándar de la comunidad Flutter.

## DEC-008 — Config móvil con `.env` (flutter_dotenv) + sesión técnica separada
**Fecha:** 2026-04-19
**Decisión:** Cargar `mobile/.env` en arranque con `flutter_dotenv`; URLs y nombre de app vía `AppEnv` / `ApiConstants`. Segundo cliente HTTP (`TecnicoApiClient`) con claves `tecnico_access_token` / `tecnico_refresh_token` en `flutter_secure_storage` para no mezclar sesión con el flujo cliente.
**Por qué:** Evita hardcodear `API_BASE_URL` y permite probar en dispositivo físico sin recompilar con `--dart-define`. Dos actores en la misma app requieren aislar tokens si el usuario alterna modo sin cerrar sesión global única.

## DEC-009 — Columna `tecnico_asignado_at` en `solicitudes_emergencia` (migraciones Docker)
**Fecha:** 2026-04-22
**Decisión:** Incluir `tecnico_asignado_at TIMESTAMP` (nullable) en el mismo `ALTER` de fase 2 (`0003_ciclo2_fase2_seguimiento.sql`) y además en un parche idempotente `0006_tecnico_asignado_at.sql` montado en `docker-compose` como script `05` (después de comunicaciones) para BDs creadas con un `0003` antiguo sin la columna.
**Por qué:** El ORM y `portal_taller_emergencias` dependen de esa marca de tiempo al asignar técnico; sin columna, cualquier `INSERT`/`SELECT` a la tabla falla y el cliente móvil no puede registrar emergencias. Init de Postgres solo corre en volumen vacío: los entornos existentes requieren `ADD COLUMN IF NOT EXISTS` manual o ejecutar `0006` contra la instancia.

## DEC-010 — IA modular: backend + contenedor `ai-inference` opcional
**Fecha:** 2026-04-23  
**Decisión:** La lógica de producto (reglas, prioridad, persistencia de `ai_payload`) vive en **`backend/app/modules/ai/`**. STT y visión pesada (Whisper, Ultralytics YOLO) corren en un **servicio aparte** `ai-inference` en la red Docker, invocado por HTTP desde el backend (`AI_INFERENCE_BASE_URL`). El servicio se declara con **perfil Compose `ai`** para que clones sin GPU no arranquen el worker por defecto si no lo necesitan. Modelo de clasificación entrenado fuera del repo se monta con override **`docker-compose.ai-custom-model.yml`** y peso local `backend/incidentes_emergencias_v1.pt` (ignorado por git).  
**Por qué:** Separa dependencias pesadas (torch, modelos) del ciclo de vida del API principal, permite escalar o sustituir el worker, y mantiene el backend liviano para tests y despliegues sin IA.

## DEC-011 — Clasificación YOLO: `probs.top5` como lista o tensor
**Fecha:** 2026-04-23  
**Decisión:** En `services/ai-inference/app/main.py`, `_yolo_classify` convierte `top5` y `top5conf` a listas de enteros y floats **sin asumir** que sean tensores PyTorch (acepta `list`/`tuple`, tensor, numpy).  
**Por qué:** Versiones recientes de Ultralytics exponen `probs.top5` ya como lista; llamar `.cpu()` rompía la inferencia (500 en el worker, 502 en el gateway del backend).

## DEC-012 — Silero VAD: eliminar parámetro `force_onnx`
**Fecha:** 2026-04-23  
**Decisión:** En `_silero()` de `services/ai-inference/app/main.py`, llamar `torch.hub.load` sin el argumento `force_onnx=False`.  
**Por qué:** La firma actual de `silero_vad` en `snakers4/silero-vad` ya no acepta `force_onnx`; su presencia causaba `TypeError` y el worker no arrancaba.

## DEC-013 — Validación completa de endpoints IA (2026-04-23)
**Fecha:** 2026-04-23  
**Decisión:** Se validaron los 6 endpoints del módulo `ai/` en Swagger con respuestas 200, incluyendo `/assignment/rank` que consulta la BD y retorna score compuesto (proximidad + especialidad + prioridad + carga).  
**Por qué:** Confirma que el diseño híbrido (worker para cómputo pesado + reglas en backend para lógica de producto) es correcto y funcional. Los scores del ranker de talleres son explicables campo a campo, lo que facilita debugging y ajuste de pesos sin reentrenar modelos.

## DEC-014 — Dockerfiles sin `syntax=` ni `RUN --mount=cache` (estabilidad Windows)
**Fecha:** 2026-04-25  
**Decisión:** En `backend/Dockerfile` y `frontend/Dockerfile`, quitar la directiva `# syntax=docker/dockerfile:1` y reemplazar `RUN --mount=type=cache` por `RUN` lineal (pip / npm).  
**Por qué:** En Docker Desktop sobre Windows, BuildKit a veces falla con `failed to solve: frontend grpc server closed unexpectedly` al usar el frontend externo o mounts de caché; el Dockerfile en vanilla BuildKit basta para multi-stage. Coste: builds algo más lentos (sin caché compartida de pip/npm en el mount); beneficio: menos dependencia del daemon y del pull de `docker/dockerfile:1`.

## DEC-015 — Fusión multimodal v1 para incidentes compuestos
**Fecha:** 2026-04-25  
**Decisión:** Para Fase 1, mantener el worker actual por evidencia (`audio/image`) y resolver incidentes compuestos en backend con un **fusionador multimodal por reglas ponderadas** (`backend/app/modules/ai/services/evidence_fusion.py`), soportando múltiples fotos y múltiples transcripciones sin romper endpoints existentes.  
**Por qué:** Permite entregar valor inmediato (multi-daño explicable, prioridad más robusta, conflicto detectable) sin introducir complejidad de entrenamiento/serving adicional en esta iteración. Deja base limpia para fase multi-label entrenada en siguiente ciclo.
