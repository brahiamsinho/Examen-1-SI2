# NEXT_STEPS.md
# =========================================================
# Próximos pasos ordenados por prioridad
# Actualizado: 2026-06-05 — CU46 KPIs ✅; verificar E2E Docker
# =========================================================

## HECHO — CU46 Dashboard KPIs (2026-06-05) ✅

- Admin y taller: pantallas dedicadas, export CSV, empty/error states.
- Migración `0023_reportes_kpis_cu46.sql`.
- Sesión: `docs/ai/sessions/2026-06-05-agent-cu46-dashboard-kpis.md`.

## ALTA — Verificar CU46 en Docker

1. `docker compose restart backend` (aplicar migración 0023).
2. `docker compose build frontend && docker compose up -d --no-deps frontend`.
3. Admin → Reportes KPIs; Taller → Reportes KPIs; probar filtros y CSV.

## HECHO — CU44 Consultar ETA reparación (2026-06-05) ✅

- Endpoint dedicado + UI Seguimiento mobile con caché offline.
- Sesión: `docs/ai/sessions/2026-06-05-agent-cu44-consultar-eta-reparacion.md`.

## ALTA — Verificar CU43/CU45 sync offline (E2E)

Sesión: `docs/ai/sessions/2026-06-05-agent-cu43-cu45-sync-offline.md`.

1. Aplicar migración `0022_client_request_id_cu43.sql` (`docker compose restart backend` o bootstrap).
2. Mobile: `flutter pub get` + probar modo avión → wizard → borrador → reconectar → sync.
3. Confirmar idempotencia: replay no duplica solicitud (mismo `client_request_id`).
4. Opcional: pytest integración DB; soporte offline en web (Hive no init en `kIsWeb`).

## HECHO — CU43 + CU45 (2026-06-05) ✅

- CU45: borrador Hive + wizard offline + evidencias persistentes.
- CU43: `SyncOrquestador` + UI Mis solicitudes + `client_request_id` backend.

## DIFERIDO — CU42 Registrar cotización

Recomendaciones UX: `topic_key: examen-si2/cu42-recomendaciones`. Backend + UI base ✅.

## ALTA — CU42 Registrar cotización del servicio (taller web) — HECHO

1. Leer gap en Engram: `topic_key: examen-si2/cu42-registrar-cotizacion`.
2. Backend: endpoint taller PATCH/POST presupuesto (`presupuesto_bob` + detalle); validar tenant, taller, estado, monto; regla presupuesto existente.
3. Frontend: formulario en detalle solicitud taller (`taller-emergencias-incidente-detalle`).
4. Opcional CU41: notificar cliente al registrar cotización (`eventos_servicio`).
5. Definir convivencia con CU39 (técnico ya registra presupuesto al EN_ATENCION).
6. Tras cambios Angular: `docker compose build frontend` + `docker compose up -d --no-deps frontend`.

## DIFERIDO — CU41 Notificaciones (retomar después)

Backlog completo en Engram: `topic_key: examen-si2/cu41-notificaciones-pendiente`.

- Push FCM / Web Push taller web.
- Tests pytest tenant + idempotencia `evento_id`.
- `X-Tenant-Slug` interceptor Angular taller (revisar cobertura).
- Dropdown campana, TRACEABILITY_MATRIX CU41, diagrama comunicación PUDS.
- In-app taller **ya implementado** (campana, inbox, hooks cliente→taller).

## ALTA — Verificar panel taller (2026-06-05)

1. Hard refresh **Ctrl+Shift+R** en `http://localhost/taller/panel` como `luis.rivera@sc-demo.test`.
2. Navegar sidebar: Resumen, Solicitudes, Mis solicitudes, Historial, Mi taller, Técnicos, Roles, Clientes.
3. Si algo sigue en "Cargando…", revisar consola DevTools (Network debe ser 200) y el componente hijo de esa ruta.

## ALTA — Planes y precios + Stripe (2026-06-04)

1. Reiniciar backend: `docker compose up -d --build backend` (migración `0019_pricing_plans.sql`).
2. Admin superadmin → **Comercial → Planes y precios** → editar plan Pro → pegar `stripe_price_id` de Stripe.
3. Configurar `.env`: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`.
4. Landing `#precios` → plan de pago → email → redirect Stripe Checkout.
5. Rebuild frontend si usas Docker: `docker compose up -d --build frontend`.

## ALTA — Login panel admin (verificado 2026-06-04)

1. ~~Seeds CLIENTE bloqueaban arranque~~ — corregido con `asignar_roles_usuario_seed`.
2. Usar solo **`patricio.mendez@sc-demo.test`** / **`scdemo1`** en `/admin/login`.
3. Tras `docker compose up --build`, migraciones y seeds demo corren solos (entrypoint); login admin sin `alembic stamp` manual.
4. Opcional UX: mensaje distinto si el usuario existe pero no tiene rol ADMIN.

## MEDIA — Admin SaaS organizaciones

1. ~~Fix 422 al crear org (slug mayúsculas)~~ — hecho 2026-06-04.
2. Probar en UI: `/admin/panel/organizaciones` → slug `Mi Empresa` o `Nueva-Org` → debe crear OK; slug `mi-empresa` → 409 con mensaje claro.
3. Si el frontend Docker no refleja cambios: `docker compose up -d --build frontend`.

## MEDIA — Admin SaaS talleres (provision)

1. ~~Formulario único taller + credenciales~~ — hecho 2026-06-04 (`POST /api/talleres/provision`).
2. Probar: crear taller en org `demo-sc` → login `/taller` con slug + email + password del formulario.
3. Opcional: ocultar ruta `/admin/panel/usuarios` o redirigir a talleres.

## MEDIA — PUDS / diagramas (flujos taller)

1. Leer **`docs/ai/FLOWS_PORTAL_TALLER.md`** antes de cambiar registro o login taller.
2. Exportar o sincronizar **`docs/diagrams/uml/sequence-taller-registro-login.puml`** en EA/draw.io si el examen pide secuencia.
3. Opcional: extender registro público con `tenant_id` / slug (ver §7 FLOWS_PORTAL_TALLER).

## MEDIA — Landing (post Paleta A)

1. ~~Paleta A + fases 1–3~~ — hecho 2026-05-28; ver `docs/ai/sessions/2026-05-28-agent-landing-paleta-a-dark.md`.
2. Opcional fase 4–5 del plan: screenshot real panel taller en product frame; acordeón módulos por categoría.
3. QA contraste WCAG y `prefers-reduced-motion` en navegador real.

## ALTA — Entorno listo en 5 min

0. **Subagentes:** … **diagramas** → `@diagrams-modeling` + skill **`uml-c4-puds-diagrams`**; **PUDS** → `puds`; memoria → `docs-memory`.
0a. **Diagramas / PUDS:** leer **`docs/ai/PUDS_GUIDE.md`** y **`docs/diagrams/agent-memory/RULES.md`** (UML **2.5+ obligatorio**). C4 completo en `docs/diagrams/c4/`; abrir draw.io con MCP **`user-drawio`**. Guardar `.drawio` en `docs/diagrams/drawio/`. EA: reset manual `EA_CLEAN_RESET.md` si aplica; recrear D-006 con layout JSON.
0b. **Multi-tenant (BD ya creada):** aplicar `0015_multitenancy_saas.sql` y **`0016_multitenancy_phase2.sql`** con `psql` en contenedor `db`; luego `docker compose exec backend python -m app.seeds` y **volver a iniciar sesión** (JWT con `tenant_id`). PowerShell:  
   `Get-Content backend\migrations\0016_multitenancy_phase2.sql | docker compose exec -T db psql -U emergencias -d emergencias_db`
0c. **Panel admin SaaS:** superadmin plataforma (`ADMIN` sin tenant) → selector «Organización» en la barra superior; gestión en `/admin/panel/organizaciones`.
0d. **Fase 3 BD:** `Get-Content backend\migrations\0017_saas_billing_phase3.sql | docker compose exec -T db psql -U emergencias -d emergencias_db`
0e. **Stripe SaaS (opcional):** `STRIPE_SAAS_PRICE_STARTER`, `STRIPE_SAAS_WEBHOOK_SECRET`, webhook URL `/api/webhooks/stripe-saas`.
0f. **Mobile:** `TENANT_SLUG_DEFAULT=demo-sc` en `mobile/.env`; campo «organización» en login cliente/técnico.
0g. **Stripe pagos CU38 (opcional):** en `.env` raíz `STRIPE_SECRET_KEY` + `STRIPE_PUBLISHABLE_KEY` (test); `docker compose up -d --force-recreate backend`; verificar `stripe_enabled=True` en contenedor; en app cliente pagar con **Tarjeta** y `4242…`.

1. Leer **`AGENTS.md`** (raíz).
2. Copiar **`.env.example` → `.env`** en la raíz del repo y ajustar `SECRET_KEY`, DB si hace falta. **IA:** definir **una sola vez** `AI_ENABLED` y `AI_INFERENCE_BASE_URL` (no duplicar bloques al pegar comentarios). Para Docker con worker en la misma red: `AI_ENABLED=true`, `AI_INFERENCE_BASE_URL=http://ai-inference:8080`.
3. **`mobile/.env`** desde `mobile/.env.example` — `API_BASE_URL` (IP/puerto del host desde el dispositivo).
4. **Docker — solo DB + backend + frontend + Mailpit:**  
   `docker compose up -d --build`  
   (timezone contenedores: `TZ=America/La_Paz`; Postgres además `PGTZ=America/La_Paz`)
   **Docker — incluir worker de inferencia (Whisper + YOLO):**  
   `docker compose --profile ai up -d --build`  
   **Docker — además modelo de clasificación propio** (archivo local `backend/incidentes_emergencias_v1.pt`):  
   `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build`  
   **Si aún falla el build** con `frontend grpc server closed unexpectedly`: el repo ya usa Dockerfiles sin `# syntax=`; en el equipo: reiniciar Docker Desktop, `docker buildx prune`, o variables de sesión `DOCKER_BUILDKIT=0` y `COMPOSE_DOCKER_CLI_BUILD=0` (builder clásico).
5. Luego **`docker compose exec backend python -m app.seeds`** (mismo proyecto; el perfil `ai` no afecta `exec`). Al final: **demo Santa Cruz**, **demo media prioridad** y **stress visual** (catálogo extra + clientes `*.lista.sc-demo.test`; credenciales base en `identidades_demo_sc.py`). Opcional en arranque: `SEED_DEMO_MEDIA_PRIORIDAD_ON_START`, `SEED_STRESS_VISUAL_ON_START`, etc.
6. Probar API: `http://localhost:8000/docs` y health `/health`. Probar IA: `POST /api/ai/images/analyze` con Bearer de un usuario con permiso `ai:inferir` (p. ej. admin tras seeds).
7. **BD ya existente (actualización 2026-04-22):** si aparece `tecnico_asignado_at` inexistente, aplicar el SQL de `backend/migrations/0006_tecnico_asignado_at.sql` (p. ej. con `psql` en el contenedor `db`). Init de Postgres no vuelve a correr en un volumen ya poblado.
8. **BD ya existente (presupuesto BOB, 2026-04-25):** aplicar `backend/migrations/0014_presupuesto_bob_solicitud.sql` con `psql` si la base se creó antes de añadir el archivo al `docker-compose` (nuevos `docker compose up` con volumen virgen montan `14_` automáticamente).
9. **Tras cambiar código de `services/ai-inference/`:** reconstruir el contenedor, p. ej.  
   `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build --force-recreate ai-inference`
10. **Si backend cae al iniciar por `Unknown constraint max_digits`:** usar la versión actual de `backend/app/modules/portal_tecnico_emergencias/schemas.py` (validación monetaria en `model_validator`) y recrear solo backend:  
   `docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml -f docker-compose.override.yml --profile ai up -d --build backend`

## MEDIA — Producto (Ciclo 1 y transversal)

### Angular
- [ ] Auth (login/guard/interceptor) y layout admin
- [ ] Pantallas CRUD alineadas al backend (más allá del portal taller emergencias)
- [x] **Dashboard admin financiero (2026-04-26):** KPIs de comisión plataforma (10%), filtros por fecha, top talleres y serie diaria conectados a `/api/admin/finanzas/resumen|reportes`.
- [x] **Fix de compilación rutas finanzas:** creada vista `features/finanzas/admin-finanzas.component` para resolver import faltante en `admin.routes.ts`.
- [x] **Portal taller emergencias (2026-04-26):** sidebar y rutas **Mis solicitudes**, **Historial de atenciones**, **Servicios asignados**, **Comisiones** (API `historial_atenciones:leer` / `comisiones:leer`); enlaces a detalle vía `bandeja_id` devuelto por backend en historial y listado de comisiones.

### Flutter
- [ ] Tests (unit/widget), refresh token si se expone en API
- [ ] Pulir UX y mensajes de error en red

### Backend
- [ ] Endpoint refresh / recuperación de contraseña real si producto lo exige
- [ ] Paginación y tests pytest ampliados
- [ ] Definir/implementar recurso API `servicios` (rutas, contrato, permisos) para ejecutar la matriz de `docs/ai/TESTING_STRATEGY.md`.

## MEDIA — Dominio emergencias (Ciclo 2; parte ya implementada en repo)

- [x] Backend: `emergencias`, `portal_taller_emergencias` (incl. CU28 asignar técnico), `portal_tecnico_emergencias`
- [x] Flutter cliente: flujo reporte / listado / seguimiento
- [x] Portal web taller: bandeja, detalle, aceptar/rechazar, asignar técnico (CU28), disponibilidad
- [x] **Módulo IA completo** — 6 endpoints validados con respuestas 200 correctas (audio, imagen, clasificar, resumen estructurado, priorizar, rankear talleres)
- [x] **Mobile: visualización IA compuesta** — lectura/render de `damages`, `requires_manual_review`, `conflict_notes`, `score`, `damages_considerados`, `danos_detectados`, `hallazgos_vision_por_imagen`.
- [~] Notificaciones push y geolocalización en tiempo real (mejoras)
  - [x] Registro de token FCM + foreground `onMessage`.
  - [x] Deep-link por tap de notificación (`onMessageOpenedApp` + `getInitialMessage`) hacia chat/detalle.
  - [x] Foreground UX migrada a notificación del sistema (no `SnackBar`) con `flutter_local_notifications`.
  - [x] Push de pago confirmado (simulado + Stripe confirm).
  - [x] Push de bienvenida cliente al primer registro de token.
  - [x] Push al técnico cuando el taller lo asigna a una solicitud (mismo pipeline FCM; ver token único por dispositivo).
  - [x] Logging de entrega FCM en backend (`success_count`/`failure_count`).
  - [x] **CU36:** pantalla ubicación técnico con polling 12 s + refresh manual (`emergencia_ubicacion_tecnico_screen.dart`).
  - [ ] Tracking continuo de técnico en mapa en tiempo real (WebSocket/SSE) + background location robusta.
  - [ ] Auditar notificaciones “pendientes” y política de replay por ventana de tiempo (hoy: 10 últimas no leídas al primer token).
- [x] Hora de presentación unificada en BOT (Santa Cruz) para web y mobile.
  - [x] Parse UTC naive en mobile para timestamps API sin zona (`api_datetime.dart`).

## ALTA — Ciclo 4 (CU36–CU40) — validación manual

1. Login cliente `carlos.vega@sc-demo.test` / `scdemo1`, org `demo-sc`.
2. Crear emergencia con ubicación → **Elegir taller** (CU37) → confirmar → verificar bandeja solo en taller elegido.
3. Taller acepta y asigna técnico; técnico comparte GPS → cliente **Ver ubicación del técnico** (CU36): mapa actualiza ~cada 12 s.
4. Técnico presupuesto + `EN_ATENCION` → cliente **Pago** (CU38): tarjeta con Stripe si claves cargadas; si no, simulado.
5. Admin `/admin/panel/organizaciones` (CU40) si aplica defensa SaaS.

## ALTA — Validación funcional post-fix (manual)

1. Crear solicitud con cliente.
2. Aceptar y asignar técnico desde taller.
3. Iniciar sesión técnico y registrar token FCM.
4. Verificar llegada de push pendiente de asignación (replay) y notificaciones de nuevos cambios.
5. Cambiar estado a `EN_CAMINO`; confirmar ETA visible (20 min fallback si no definido por taller).
6. Cliente abre seguimiento: validar hora BOT correcta y pago prellenado con presupuesto si existe.
7. Cliente abre `pago_resumen`: validar que el monto bloqueado coincida con `presupuesto_bob` del técnico; usar botón/gesto de refresco y confirmar que cambia de “no definido” a monto visible sin reiniciar app.
8. IA incidente compuesto: probar en Swagger
   - `POST /api/ai/images/analyze-batch` con 2-3 fotos distintas.
   - `POST /api/ai/incidents/classify` con `transcripciones_audio[]` y `hallazgos_vision_por_imagen[]`.
   - verificar `damages[]` y `requires_manual_review`.
9. Priorización compuesta:
   - `POST /api/ai/incidents/prioritize` y verificar `score` + `damages_considerados[]`.
10. Resumen compuesto:
   - `POST /api/ai/incidents/structured-summary` y verificar `danos_detectados[]`.

## BAJA

- [ ] CI/CD, despliegue documentado

## Obsoleto (ya hecho)

- ~~`flutter create` / `ng new`~~ — proyectos ya inicializados.
- ~~Alembic baseline~~ — configurado; usar `alembic stamp` / `upgrade` según doc del README raíz.
- ~~Remover etiquetas internas `Ciclo` / `CUxx` en frontend/mobile~~ — aplicado en vistas y copys visibles.
