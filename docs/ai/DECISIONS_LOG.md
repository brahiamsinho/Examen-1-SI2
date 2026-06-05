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

## DEC-016 — AVIF/HEIF en inferencia y lote resiliente (2026-04-26)

**Fecha:** 2026-04-26  
**Decisión:** En `ai-inference`, añadir `pillow-heif` + dependencia de sistema `libheif1` y `register_heif_opener()` para decodificar AVIF/HEIF antes del pipeline OpenCV/YOLO. En `POST /api/ai/images/analyze-batch`, ante fallo de una imagen devolver un `ImageAnalyzeResponse` sintético (hallazgo con mensaje, confianza 0) en lugar de 502 para todo el lote.  
**Por qué:** Los móviles y navegadores envían cada vez más AVIF; Pillow estándar no lo garantiza. Un archivo malo no debe invalidar el análisis del resto del incidente compuesto.

## DEC-017 — Paquetes `auth` / `roles` / `permisos` y dominio notificaciones/push/mensajes (2026-04-26)

**Fecha:** 2026-04-26  
**Decisión:** Separar el antiguo módulo `acceso` en tres paquetes (`auth`, `roles`, `permisos`) y el antiguo `comunicaciones` (modelo+repo+FCM+servicio) en `notificaciones`, `dispositivos_push`, `mensajes_solicitud`, dejando `comunicaciones` solo como capa de **routers** que delega.  
**Por qué:** Límites de importación claros, coherencia con arquitectura modular por dominio y mantenimiento (cambiar FCM no arrastra el modelo de chat). Las tablas y URLs HTTP se mantienen; el registro de bitácora de asignación de roles pasa a `modulo="roles"`.

## DEC-019 — Healthcheck de Postgres con `start_period` (2026-04-26)

**Fecha:** 2026-04-26  
**Decisión:** En `docker-compose.yml`, el servicio `db` usa `healthcheck.start_period: 240s` y `retries: 12` (antes sin `start_period`, 5 reintentos).  
**Por qué:** En el primer arranque con volumen vacío, `initdb` + múltiples SQL en `docker-entrypoint-initdb.d` y el cierre/reapertura del servidor pueden hacer fallar `pg_isready` durante unos minutos sin que la BD esté “rota”; Docker marcaba **unhealthy** y Compose bloqueaba `backend` (`depends_on: condition: service_healthy`). `start_period` hace que esos fallos iniciales no cuenten hacia unhealthy.

## DEC-018 — Contexto de build Docker acotado + `.dockerignore` (2026-04-26)

**Fecha:** 2026-04-26  
**Decisión:** El servicio `ai-inference` compila con `build.context: ./services/ai-inference` (no la raíz del monorepo). Se amplían `.dockerignore` en backend/frontend/ai-inference y el backend usa `COPY --chown` en lugar de `chown -R` post-copy.  
**Por qué:** Un `context: .` envía mobile, frontend, docs y `.git` al daemon en cada build (transferencia y hashing lentos). `chown -R` sobre todo el árbol de aplicación penaliza cada invalidación de la capa `COPY`. Se mantiene la postura de **DEC-014** (sin `# syntax=` ni `--mount=cache` por defecto en Windows) hasta adoptar BuildKit estable en CI o en dev.

## DEC-020 — YOLO custom: `.env` classify + override que monta el `.pt` (2026-04-26)

**Fecha:** 2026-04-26  
**Decisión:** No fijar en el `docker-compose.yml` base un bind a `backend/incidentes_emergencias_v1.pt` (los clones sin peso local fallarían al hacer `up`). El montaje queda en **`docker-compose.ai-custom-model.yml`**. El `.env` con modelo propio usa `YOLO_TASK=classify`, `YOLO_MODEL=/models/incidentes_emergencias_v1.pt`, `YOLO_IMGSZ=224` y se levanta con **dos** archivos compose.  
**Por qué:** Un `.pt` solo en el host no basta: sin volumen, `/models/...` no existe en el contenedor; con `YOLO_TASK=detect` y `yolov8n.pt` el worker aplica COCO, no el clasificador de Colab.

## DEC-029 — EA: Model Wizard y documentación Sparx antes de implementar (2026-05-28)

**Fecha:** 2026-05-28  
**Decisión:** Antes de crear o editar diagramas en Enterprise Architect (MCP o manual), el agente debe (1) revisar **Model Wizard** (`Ctrl+Shift+M`, pestaña Diagram o Model Patterns), (2) leer la descripción del patrón y la **documentación oficial Sparx** del tipo de diagrama (secuencia BCE, despliegue, etc.), (3) solo entonces ajustar con MCP. Runbook: `docs/diagrams/agent-memory/EA_MODEL_WIZARD_WORKFLOW.md`.  
**Por qué:** Implementar solo con MCP generó lifelines genéricos y diagramas duplicados (login ID 11 vs 12); los patrones Wizard y la guía BCE de Sparx alinean el modelo al estilo académico del curso.

## DEC-028 — UML 2.5+ obligatorio + C4 4 capas + PUDS_GUIDE (2026-05-28)

**Fecha:** 2026-05-28  
**Decisión:** (1) **UML 2.5+** es obligatorio para paquetes, secuencia, clases y despliegue académico — no sustituir despliegue por C4 Container ni diagramas Docker genéricos. (2) Modelo **C4 en 4 capas** (D-001…D-004c) como vista de arquitectura del producto. (3) Crear **`docs/ai/PUDS_GUIDE.md`** enlazando fases PUDS, artefactos y trazabilidad CU→diagrama→código. (4) draw.io vía MCP **`user-drawio`** con Mermaid C4 nativo; PlantUML sigue siendo fuente Git.  
**Por qué:** Defensa académica exige notación UML 2.5 en despliegue y diseño; C4 y UML cumplen roles distintos; memoria persistente evita repetir errores (mezclar notaciones, entregar solo Git sin draw.io).

## DEC-027 — MCP draw.io + integración EA / PlantUML (2026-05-28)

**Fecha:** 2026-05-28  
**Decisión:** Configurar MCP oficial **`@drawio/mcp`** en `.cursor/mcp.json` (clave `drawio`). Añadir carpeta `docs/diagrams/drawio/` con Mermaid puente (`mermaid/*.mmd`) hacia el editor; documentar flujo triple PlantUML (Git) + EA (modelo académico) + draw.io (edición visual) en `DRAWIO_INTEGRATION.md` y `MCP_SETUP.md`.  
**Por qué:** Permite abrir diagramas editables en el navegador desde Cursor, importar Mermaid alineado a C4 existente, y complementar EA sin reemplazar `.puml` ni el `.eapx` del curso.

## DEC-026 — Subagente diagrams-modeling + memoria `docs/diagrams/` (2026-05-28)

**Fecha:** 2026-05-28  
**Decisión:** Crear subagente **`diagrams-modeling`** (PlantUML, UML 2.5+, C4, ASCII vía skill `plantuml-ascii`, integración MCP **Enterprise Architect** cuando EA está abierto). Fuente versionada en `docs/diagrams/`; memoria exclusiva del agente en `docs/diagrams/agent-memory/` (RULES, LEARNINGS, HANDOFF, etc.). Artefactos PUDS enlazados: `docs/ai/DIAGRAMS_GUIDE.md`, `PACKAGE_DESIGN.md`. El agente **`puds`** delega la generación de diagramas y conserva trazabilidad RF/CU.  
**Por qué:** Separar modelado visual/académico del análisis textual PUDS; evitar errores repetidos (nombres inventados, `/servicios` inexistente, EA timeout) con memoria que “aprende”; mantener diagramas en Git alineados al código real.

## DEC-025 — SaaS fase 3: billing Stripe, API pública, subdominio, mobile (2026-05-24)

**Fecha:** 2026-05-24  
**Decisión:** Módulo `billing` con webhook `stripe-saas`; endpoints públicos de descubrimiento de tenant; resolución de slug por `Host`; registro y login con `X-Tenant-Slug`; `require_writable_tenant_subscription` en alta de emergencias; tests unitarios sin BD.  
**Por qué:** Completar el roadmap SaaS B2B (cobro plataforma, UX por organización, defensa en profundidad operativa).

## DEC-024 — SaaS multi-tenant fase 2: RLS, unicidad por tenant, panel organizaciones (2026-05-24)

**Fecha:** 2026-05-24  
**Decisión:** Migración `0016_multitenancy_phase2.sql`: índices únicos `(tenant_id, email)` / placa, columnas Stripe en `tenants`, RLS en 5 tablas con `app.tenant_id` y `app.bypass_rls`; middleware `X-Tenant-Slug`; `get_auth_context` / `get_current_user` publican `AuthContext` para `get_db`; login con bypass RLS; Angular: selector de organización para superadmin, ruta `/admin/panel/organizaciones`, finanzas/usuarios/talleres con `?tenant_id=`.  
**Por qué:** Refuerzo en BD del aislamiento (defensa en profundidad), preparación billing SaaS y UX de operador de plataforma sin mezclar datos entre tenants.

## DEC-023 — SaaS multi-tenant: shared schema + `tenant_id` (2026-05-24)

**Fecha:** 2026-05-24  
**Decisión:** Introducir tabla `tenants` y columna `tenant_id` en entidades operativas; JWT incluye `tenant_id`; superadmin plataforma = rol `ADMIN` con `usuarios.tenant_id` NULL; API `/api/admin/tenants` para alta/gestión de organizaciones; finanzas y bandeja filtran por tenant salvo superadmin. Migración `0015_multitenancy_saas.sql`. Skills instaladas: `multitenancy`, `multi-tenant-safety-checker`.  
**Por qué:** Preparar el producto para varios clientes B2B aislados sin desplegar una instancia por cliente; alinea con PUDS y operación SaaS real manteniendo un solo stack FastAPI/Postgres.

## DEC-022 — Subagentes especializados ai-inference, qa-testing, security (2026-05-24)

**Fecha:** 2026-05-24  
**Decisión:** Añadir tres subagentes en `.cursor/agents/` además del roster existente: **`ai-inference`** (implementación/depuración del pipeline IA del repo), **`qa-testing`** (pruebas automatizadas y manuales alineadas a `TESTING_STRATEGY.md`) y **`security`** (auth, secretos, Stripe, FCM, hardening). Actualizar **`orchestrator.md`** con tabla de delegación y distinguir **`ai-inference`** (operar lo existente) de **`ai-researcher`** (investigar tecnologías nuevas).  
**Por qué:** El dominio IA es transversal (worker Docker, backend, mobile, env) y no encaja solo en backend; las pruebas y la seguridad tienen entregables distintos a reviewer/backend. Evita agent sprawl manteniendo roles acotados y documentados en el repo.

## DEC-021 — Re-ejecutar enriquecimiento IA al agregar evidencia/ubicación (2026-04-27)

**Fecha:** 2026-04-27  
**Decisión:** Tras insertar `solicitud_evidencias` (URL o archivo), tras insertar `solicitud_ubicaciones` y tras actualizar `descripcion_texto` en `REGISTRADA`, se llama de nuevo a `enrich_solicitud_ai_after_create` para recalcular `ai_payload`. Para enviar la imagen al worker se usa `load_evidencia_bytes` (lectura bajo `uploads/evidencias/` cuando el path de la URL es `/.../media/evidencias/<file>`) antes de `GET` HTTP.  
**Por qué:** En el flujo real el cliente no siempre sube imagen al crear; si la IA solo corre en el `POST` inicial, queda `clasificacion.fuentes: ["texto"]` aun con foto posterior, y además un `httpx` a una URL pública con IP de LAN del teléfono es frágil dentro de Docker.

## DEC-025 — UML casos de uso: Include/Extend explícitos en EA y PUDS (2026-05-29)

**Fecha:** 2026-05-29  
**Decisión:** Documentar en `docs/diagrams/agent-memory/USE_CASE_INCLUDE_EXTEND_GUIDE.md` la notación UML 2.5: actor→CU con `Association` sólida; entre CUs solo `Include` (base→incluido) o `Extend` (extensión→base) con línea discontinua y estereotipo. En EA MCP usar `type: Include` / `type: Extend`, no `Association`. Diagrama general Ciclo 4 (CU36–CU40) en EA diagramID **26**, conectores **316–320**.  
**Por qué:** Entrega académica 4.1.5 y plantilla de examen exigen distinguir `«include»` y `«extend»`; asociaciones genéricas entre CUs no son defendibles en PUDS.

## DEC-029 — Portal taller: registro público separado del login (2026-05-28)

**Fecha:** 2026-05-28  
**Decisión:** El alta de taller + responsable ocurre solo en `POST /api/app/taller/registro` (ruta Angular `/taller/registro`), sin JWT. El login en `/taller` solo autentica (`POST /api/auth/login` + `GET /auth/me`) y exige rol `TALLER_RESPONSABLE`. Un usuario responsable tiene como máximo un taller (`talleres.usuario_responsable_id` UNIQUE). El panel opera el taller existente (`GET/PUT mi-taller`, técnicos, emergencias); no crea un segundo taller.  
**Por qué:** Evita confusión producto/SaaS (“¿entro y se crea el taller?”) y alinea responsabilidades con PUDS (CU registrar vs iniciar sesión). Documentado en `docs/ai/FLOWS_PORTAL_TALLER.md` y `docs/diagrams/uml/sequence-taller-registro-login.puml`.  
**Nota SaaS:** el registro público actual no asigna `tenant_id`; el login sí valida `X-Tenant-Slug` cuando el usuario ya tiene tenant.

## DEC-026 — CU37: bandeja solo tras elección explícita del cliente (2026-06-02)

**Fecha:** 2026-06-02  
**Decisión:** `crear_solicitud` deja de insertar filas `solicitud_taller_bandeja` PENDIENTE para todos los talleres del tenant. El cliente elige taller vía `GET/POST .../talleres-candidatos` y `.../seleccionar-taller`; el backend crea una sola bandeja PENDIENTE y expira pendientes previas. Seeds demo que necesiten multi-taller siguen llamando `insert_bandeja_pendiente_por_cada_taller` de forma explícita.  
**Por qué:** Alinea el flujo con CU37 (elección del cliente) y evita que varios talleres vean la misma emergencia antes de la decisión. Documentado en `CICLO4_DETALLE_CASOS_USO.md` y memoria `docs/ai` (2026-05-28).

## DEC-030 — Admin SaaS: provision atómica taller + responsable (2026-06-04)

**Fecha:** 2026-06-04  
**Decisión:** Nuevo endpoint `POST /api/talleres/provision` crea en una transacción: usuario `ACTIVO` con `tenant_id`, rol `TALLER_RESPONSABLE` y taller (estado configurable, default `ACTIVO`). Sin email de verificación. UI admin: formulario único en `/admin/panel/talleres`; menú **Usuarios** retirado del sidebar (ruta legacy conservada). Se mantiene `POST /api/talleres/` con `usuario_responsable_id` por compatibilidad API.  
**Por qué:** Reduce el flujo admin de Organizaciones → Usuarios → Talleres a Organizaciones → Talleres con credenciales listas para login en `/taller` con `X-Tenant-Slug`. Documentado en `FLOWS_PORTAL_TALLER.md` §6 y sesión `2026-06-04-agent-admin-provision-taller.md`.

## DEC-031 — Docker entrypoint: migraciones + seeds antes de uvicorn (2026-06-04)

**Fecha:** 2026-06-04  
**Decisión:** El contenedor `backend` usa ENTRYPOINT en `Dockerfile` → `python -m app.db.docker_bootstrap` → uvicorn. Migraciones: Alembic (`stamp head` si initdb ya creó esquema; si no `upgrade head`) + SQL incremental vía tabla `app_sql_migrations`. Seeds compartidos en `app/seeds/runner.py`; en Compose `RUN_SEEDS_IN_LIFESPAN=false` y seeds vía flags `SEED_*` en entrypoint (override dev).  
**Por qué:** Elimina pasos manuales (`alembic stamp`, `python -m app.seeds`) tras `docker compose up`; aplica SQL 0007–0017 en volúmenes antiguos; evita doble seed con `--reload`. Producción: `RUN_MIGRATIONS_ON_START=true`, seeds off salvo control explícito.

## DEC-032 — Bitácora portal taller: endpoint dedicado + permiso acotado (2026-06-05)

**Fecha:** 2026-06-05  
**Decisión:** No reutilizar `GET /api/bitacora/` para el taller. Nuevo `GET /api/app/taller/bitacora` con permiso `bitacora_taller:leer`, filtro obligatorio por `tenant_id`, actores (responsable + técnicos del `taller_id`) y whitelist de módulos operativos. Respuesta sin `ip_address`.  
**Por qué:** El endpoint admin filtra solo por tenant y expondría acciones de clientes u otros talleres de la misma organización. Tres capas (tenant + equipo + módulo) garantizan aislamiento sin `tenant_id` en la tabla `bitacora`.
