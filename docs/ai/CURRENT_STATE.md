# CURRENT_STATE.md
# =========================================================
# Estado actual del proyecto
# Última actualización: 2026-04-26 — Pago confirmación: reutiliza PagoIniciado + `stripePaymentIntentId` en confirmar-stripe ✅
# =========================================================

## Estado: CICLO 1 base + dominio emergencias (Ciclo 2) + módulo IA completo ✅

### Push técnico + presupuesto BOB (2026-04-25) ✅
- [x] **Asignación técnico:** tras notificar al cliente, el backend notifica al **usuario técnico** (`notificar_tecnico_solicitud_emergencia`) con push/in-app. Si no hay tokens FCM para ese usuario, se registra log `FCM omitido: ... sin tokens`.
- [x] **Presupuesto en sitio:** migración `0014_presupuesto_bob_solicitud.sql` + columnas en modelo `SolicitudEmergencia`; `PATCH` técnico exige `presupuesto_bob` al pasar a `EN_ATENCION`; seguimiento cliente expone `presupuesto_bob` / `presupuesto_registrado_at`; móvil cliente (seguimiento) y técnico (diálogo + lista) actualizados.
- [x] **Fix pago cliente “monto no definido” (2026-04-26):** el endpoint detalle `GET /api/portal/cliente/emergencias/{id}` no exponía `presupuesto_bob` porque `SolicitudEmergenciaRead` no lo incluía; se añadieron `presupuesto_bob` y `presupuesto_registrado_at` al schema base (y por herencia al detalle). En mobile `pago_resumen` se agregó `refresh` manual + pull-to-refresh para recargar el monto fijado por técnico sin reiniciar la app.
- [x] **FCM mismo token:** documentado en sesión: un solo token por fila; cambiar de rol en el mismo teléfono reasigna el token al último login que lo registre.
- [x] **Replay push pendientes al registrar token:** si el usuario registra su primer token FCM (p. ej. técnico inicia sesión después de ser asignado), backend reenvía hasta 10 notificaciones no leídas recientes para evitar “me llegó en historial pero no sonó push”.
- [x] **Hora BOT corregida en mobile:** parser unificado `core/utils/api_datetime.dart` interpreta timestamps API sin zona como UTC (`...Z`) antes de formatear con `BoliviaTime`; evita mostrar `01:38 BOT` cuando corresponde `21:38 BOT`.
- [x] **ETA operativa mínima:** al pasar a `EN_CAMINO`, si no existe `tiempo_estimado_min`, backend asigna fallback `20` min para no dejar tarjeta ETA vacía.
- [x] **Pago cliente prellenado con presupuesto técnico:** pantalla `pago_resumen` carga automáticamente `presupuesto_bob` cuando existe.
- [x] **Pago: monto = presupuesto (regla de negocio):** si existe `presupuesto_bob`, el monto se muestra **bloqueado** en el cliente; backend exige `monto == presupuesto_bob` en `POST /pagos`. **Stripe (PaymentIntent)** solo se crea para método **TARJETA**; efectivo/transferencia/QR dejan de recibir `client_secret` (evita inicializar el SDK con efectivo). Android: `MainActivity` extiende `FlutterFragmentActivity` (requisito `flutter_stripe`). **IA UI:** `damages[]` se parsea como objetos y se listan (label/severidad/motivos), no como `.toString()` del mapa.
- [x] **FCM + go_router (2026-04-26):** `FcmMessageListener` queda **por encima** de `ShadApp.router`, así que `GoRouter.of(context)` no encuentra el router. Se usa `ConsumerStatefulWidget` + `ref.read(goRouterProvider).go(...)` (y la misma instancia para leer ruta técnico/cliente).
- [x] **Pago — confirmar sin duplicar `POST /pagos` (2026-04-26):** `pago_confirmacion_screen.dart` reutiliza `draft.pagoIniciado` cuando coincide solicitud/método/monto (ε 0,02) en lugar de volver a `iniciarPago`; con Stripe, `confirmarStripe` recibe `paymentIntentId` desde `PagoRead.stripePaymentIntentId` (no solo `referencia_externa`), evitando 422 y filas PENDIENTE duplicadas.

### Ajuste de UX/copy (2026-04-25) ✅
- [x] Frontend Angular (admin/taller): removidas etiquetas visibles tipo `Ciclo X`, `fase X`, `CUxx` en login, recover, dashboard, shell, permisos/roles, bandeja y detalle.
- [x] Mobile Flutter (cliente/técnico): removidas etiquetas visibles `CUxx` en wizard/seguimiento/detalle y textos de actor select; comentarios internos y descripciones también normalizados para consistencia.
- [x] **Seguimiento / análisis asistido:** el backend expone en seguimiento `tiene_ubicacion_cliente`, `tiene_evidencia_foto`, `tiene_evidencia_audio`; el móvil los usa en `SolicitudAiResumenCard` (el snapshot `ai_payload.ficha` solía quedar en “no” al crear la solicitud antes de subir medios). Detalle: chips desde `ubicaciones` / `evidencias` reales. Timeline: se eliminan sueltos `(CU##)` de observaciones antiguas.
- [x] **ETA:** al asignar técnico, el portal taller puede enviar `tiempo_estimado_min` (campo en formulario) → se guarda en la solicitud → `EtaLlegadaCard` en el móvil. Sin valor, el mensaje de “aún no hay ETA” es el comportamiento esperado.
- [x] **FCM:** registro de token existente; añadido **foreground** `onMessage` → `SnackBar` (`FcmMessageListener` en `app.dart`). `google-services.json` / `firebase_options.dart` siguen siendo locales (gitignore).
- [x] **Técnico móvil:** fechas/horas visibles normalizadas a **Bolivia Santa Cruz (BOT, UTC-4)** con util común (`core/utils/bolivia_time.dart`) en tarjetas, detalle, ubicación y burbujas de chat.
- [x] **Servicios asignados técnico:** backend `portal_tecnico_emergencias` ahora expone `categoria_incidente` y `nivel_prioridad` (derivados de `ai_payload`) y el mobile los muestra en la lista/detalle con copy de severidad (p. ej. prioridad alta/crítica = grave).
- [x] **Push deep-link:** `FcmMessageListener` agrega `onMessageOpenedApp` + `getInitialMessage`; al tocar push navega directo a chat o detalle (cliente/técnico) usando `solicitud_id` y `tipo`.
- [x] **Push por pago confirmado:** backend `pagos/service.py` envía notificación in-app + push al cliente cuando el pago queda `PAGADO` (pasarela simulada y confirmación Stripe).
- [x] **Push de bienvenida cliente (primer token):** al registrar el primer FCM token del cliente (`comunicaciones/registrar_fcm_token`) se crea notificación/push de cuenta activa.
- [x] **Hora Santa Cruz (BOT) unificada:** mobile reemplaza `.toLocal()` por util común `BoliviaTime` en vistas de cliente/técnico y chat/comunicaciones/pagos; Angular fija `LOCALE_ID='es-BO'` y `DATE_PIPE_DEFAULT_OPTIONS.timezone='-0400'` para que todos los `| date` muestren hora Bolivia por defecto.
- [x] **Docker timezone BOT:** `docker-compose.yml` define `TZ=America/La_Paz` en `db`, `mailhog`, `backend`, `frontend` y `ai-inference`, y `PGTZ=America/La_Paz` en `db` para logs/fechas de contenedor alineadas a Santa Cruz.

### Portal taller emergencias — prioridad y evidencias (2026-04-25) ✅
- [x] **API** `GET /api/portal/taller/emergencias/bandeja/disponibles` y `GET .../bandeja/{id}`: campo `nivel_prioridad` (desde `ai_payload.prioridad.nivel_prioridad`); en detalle, `evidencias[]` (filas de `solicitud_evidencias` para la solicitud).
- [x] **Angular** bandeja: columna **Prioridad** con chips por nivel; detalle: galería de **fotos** y reproductor **audio** (URLs internas reescritas a ruta `/api/media/evidencias/...` bajo el mismo origen).
- [x] **Backend** `rechazar_solicitud`: corregida referencia incorrecta a variable `bandeja` al notificar al cliente.

## Lo que existe

### Backend FastAPI ✅
- [x] `core/` — config, database, security, dependencies
- [x] `modules/acceso`, `usuarios`, `vehiculos`, `talleres`, `bitacora`
- [x] `modules/portal_cliente/` — registro + mi-perfil + mis-vehículos (móvil cliente)
- [x] `modules/portal_taller/` — registro taller, mi-taller, técnicos (responsable)
- [x] `modules/portal_taller_emergencias/` — bandeja PENDIENTE, detalle incidente (CU25), aceptar/rechazar (CU26–27), disponibilidad (CU29), **asignar técnico (CU28)** e historial `solicitud_asignaciones_tecnico`; **CU30–CU31** historial de atenciones y comisiones (`comisiones_taller` + join `pagos`); permisos `solicitudes_taller:*`, `disponibilidad:gestionar`, `tecnicos:asignar`, `historial_atenciones:leer`, `comisiones:leer`; prefijo `/api/portal/taller/emergencias`
- [x] `modules/portal_tecnico_emergencias/` — CU32–CU35 (script 008): servicios asignados, ubicación cliente, actualizar estado (`solicitud_historial_estado`), mensajes vía `comunicaciones.service` + `mensajes_tecnico:*`; prefijo `/api/portal/tecnico/emergencias`
- [x] `modules/ai/` — módulo completo con **6 endpoints validados** (ver tabla abajo); inferencia audio/imagen vía cliente HTTP a **`ai-inference`**, reglas híbridas, prioridad, asignación de taller; permiso `ai:inferir`; límites `AI_MAX_*` en settings
- [x] **Fase 1 incidentes compuestos (multi-foto + multi-daño)**: schemas extendidos con `transcripciones_audio[]` y `hallazgos_vision_por_imagen[]`; salida multi-label `damages[]`; nuevo endpoint `POST /api/ai/images/analyze-batch`; fusionador multimodal v1 (`evidence_fusion.py`) con pesos `imagen=0.45`, `texto=0.30`, `audio=0.25`; bandera `requires_manual_review` para conflictos
- [x] **Mobile IA compuesto (lectura UI):** `SolicitudAiPayloadV1` ahora parsea campos nuevos (`damages`, `requires_manual_review`, `conflict_notes`, `score`, `damages_considerados`, `danos_detectados`, `hallazgos_vision_por_imagen`) y `SolicitudAiResumenCard` los muestra en detalle/seguimiento para reflejar análisis multi-daño en la app.
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
- [x] **Build estable en Windows:** `backend/Dockerfile` y `frontend/Dockerfile` sin `# syntax=docker/dockerfile:1` ni `RUN --mount=type=cache` (mitiga `frontend grpc server closed unexpectedly` con BuildKit/Docker Desktop). Workarounds extra: `docker buildx prune`, reiniciar Docker, o `DOCKER_BUILDKIT=0` + `COMPOSE_DOCKER_CLI_BUILD=0`.
- [x] **Servicio `ai-inference`** (perfil Compose `ai`): imagen en `services/ai-inference/` — STT (Whisper), visión YOLO **detect** (COCO, `yolov8n.pt` por defecto) o **classify** (modelo `.pt` propio). Sin `--profile ai` el worker **no** se levanta; el backend puede quedar con IA deshabilitada o en stub según variables.
- [x] **`docker-compose.ai-custom-model.yml`** (opcional): monta `./backend/incidentes_emergencias_v1.pt` → `/models/incidentes_emergencias_v1.pt`, `YOLO_TASK=classify`, `YOLO_IMGSZ=224`. El archivo `.pt` no va al git (`.gitignore`); se coloca local tras entrenar en Colab.
- [x] **Postgres (init):** `backend/migrations/init.sql` + `0002`–`0014` (incl. `0014_presupuesto_bob_solicitud.sql`) + **`0007_taller_operacion_permisos.sql`** (permisos `solicitudes_taller:*`, `disponibilidad:gestionar`, `tecnicos:asignar`, etc. y `rol_permiso` para `TALLER_RESPONSABLE` / `TECNICO`). Montado como `06_` en `docker-compose`. **BD ya creada:** ejecutar ese SQL a mano o `docker compose exec -i db psql ... < backend/migrations/0007_...sql`. La columna `tecnico_asignado_at` también está en `0003`. Ver `DECISIONS_LOG` **DEC-009**.

### Validación completa módulo IA — 2026-04-23 ✅

Todos los endpoints del módulo `ai/` probados en Swagger (`http://localhost:8000/docs`) con respuestas **200** correctas:

| Endpoint | Tipo | Resultado validado |
|---|---|---|
| `POST /api/ai/audio/transcribe` | Worker (`ai-inference`) | Transcripción + keywords + urgencia |
| `POST /api/ai/images/analyze` | Worker (`ai-inference`) | Hallazgos YOLO + claridad imagen |
| `POST /api/ai/incidents/classify` | Reglas backend | `categoria`, `confianza`, `fuentes` |
| `POST /api/ai/incidents/structured-summary` | Reglas backend | `resumen`, `ficha` estructurada |
| `POST /api/ai/incidents/prioritize` | Reglas backend | `nivel_prioridad`, `motivo[]` |
| `POST /api/ai/assignment/rank` | Reglas + BD | `candidatos[]`, `mejor_taller_id` |

**Ejemplo de respuesta `/incidents/prioritize` (LLANTA en autopista):**
```json
{ "nivel_prioridad": "ALTA", "motivo": ["ubicación o relato sugiere vía rápida / carretera", "lenguaje de alto riesgo"] }
```

**Ejemplo de respuesta `/assignment/rank` (La Paz, categoría LLANTA):**
```json
{ "candidatos": [{ "taller_id": 1, "nombre_comercial": "Taller Demo Emergencias", "score": 0.857, "detalle": { "proximidad": 1, "carga_bandeja": 0, "especialidad": 0.35, "prioridad_peso": 1, "distancia_km": 0 } }], "mejor_taller_id": 1 }
```

### Fase 1 incidentes compuestos — 2026-04-25 ✅

- `POST /api/ai/incidents/classify` ahora soporta evidencia compuesta:
  - `transcripciones_audio[]`
  - `hallazgos_vision_por_imagen[]`
- La clasificación devuelve además:
  - `damages[]` (multi-daño con `confidence`, `severity`, `evidence_support`, `reasons`)
  - `requires_manual_review`
  - `conflict_notes[]`
- `POST /api/ai/incidents/prioritize` ahora incluye:
  - `score` (0..1)
  - `damages_considerados[]`
- `POST /api/ai/incidents/structured-summary` ahora incluye:
  - `danos_detectados[]`
  - resumen enriquecido con daños compuestos detectados
- Nuevo endpoint: `POST /api/ai/images/analyze-batch`
  - recibe `files[]`
  - responde `imagenes[]` + `hallazgos_consolidados` + `claridad_promedio` + `confianza_promedio`

### Incidente resuelto (2026-04-23) — análisis de imagen 502/500 (worker IA) ❌→✅
- **Síntoma:** `POST /api/ai/images/analyze` devolvía **502**; logs de `ai-inference`: **500** en `/internal/vision/analyze`, `AttributeError: 'list' object has no attribute 'cpu'` en `_yolo_classify`.
- **Causa:** en Ultralytics reciente, `probs.top5` y `probs.top5conf` pueden ser **listas**, no tensores; el código llamaba `.cpu().numpy()` sin comprobar tipo.
- **Reparación:** `services/ai-inference/app/main.py` — normalización a listas de int/float. Tras cambiar el worker, **`docker compose ... --build --force-recreate ai-inference`** para que el contenedor use el código nuevo.

### Incidente operativo (2026-04-23) — backend 503 “inferencia deshabilitada”
- **Causa frecuente:** en `.env` raíz, variables `AI_ENABLED` / `AI_INFERENCE_BASE_URL` **duplicadas**; la última aparición suele ganar (`false` o URL vacía) → el backend no llama al worker.
- **Mitigación:** una sola sección `AI_*`; para Docker en la misma red: `AI_ENABLED=true`, `AI_INFERENCE_BASE_URL=http://ai-inference:8080`.

### Incidente resuelto (2026-04-25) — backend crash Pydantic en `presupuesto_bob` ❌→✅
- **Síntoma:** al arrancar backend, traceback en `ActualizarEstadoServicioIn` con `ValueError: Unknown constraint max_digits`.
- **Causa:** compatibilidad del runtime con constraints `max_digits`/`decimal_places` en `Field` sobre `Decimal`.
- **Reparación:** en `portal_tecnico_emergencias/schemas.py`, `presupuesto_bob` mantiene `gt=0` y validación de formato monetario (máx. 12 dígitos y 2 decimales) pasa a `@model_validator`. Resultado: backend inicia y `/health` responde 200.

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
- [x] Módulo IA completo — 6 endpoints validados (audio, imagen, clasificar, resumen, priorizar, rankear talleres)
- [ ] Notificaciones push en tiempo real
- [ ] Geolocalización avanzada / tracking

### Actualización rápida (2026-04-25) — Push “estilo sistema” en app móvil
- [x] `mobile/lib/core/push/fcm_message_listener.dart` cambió de `SnackBar` a notificación local del sistema en foreground usando `flutter_local_notifications`.
- [x] Tap en notificación local ahora navega por deep-link (payload JSON con `target`).
- [x] Canal Android de alta prioridad: `emergencias_high_importance`.
- [x] Backend ahora deja trazas de entrega FCM (`success_count`/`failure_count`) en `backend/app/modules/comunicaciones/fcm_client.py`.
- [x] Dependencia agregada en mobile: `flutter_local_notifications`.
