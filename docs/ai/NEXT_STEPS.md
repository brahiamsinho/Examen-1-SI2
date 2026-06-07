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
# Actualizado: 2026-06-05 — Módulo backups
# =========================================================

# Actualizado: 2026-06-05 — Reportes personalizados QBE
# =========================================================

# Actualizado: 2026-06-04 — Red talleres + horarios
# =========================================================

# Actualizado: 2026-06-04 — FCM web + notificaciones
# =========================================================

# Actualizado: 2026-06-06 — Fix push FCM mobile
# =========================================================

# Actualizado: 2026-06-06 — Notificaciones taller ampliadas
# =========================================================

## ALTA — Probar notificaciones taller ampliadas (2026-06-06)

1. `docker compose up -d --build backend` (aplica cambios de notificaciones).
2. Portal taller: login responsable, campana activa + permiso push navegador.
3. Flujo completo: CU37 → aceptar bandeja → asignar técnico → técnico en camino/atención/finalizada → chat → pago.
4. Verificar campana + push en cada paso; click debe abrir detalle de la solicitud.

## ALTA — Activar rutas por calles OSRM (2026-06-06)

1. `.\scripts\osrm-setup.ps1` (descarga Bolivia OSM + preprocesa; ~10–20 min).
2. `docker compose --profile routing up -d osrm backend`.
3. Mobile cliente → solicitud con técnico en camino → «Ver ubicación del técnico».
4. Verificar tarjeta «Llegada estimada (VRT)» y polyline curva (`proveedor: osrm` en JSON API).

## ALTA — Probar push mobile tras fix (2026-06-06)

1. Backend ya con `FCM_ENABLED=true` y credenciales JSON válidas — reiniciar si hace falta: `docker compose up -d backend`.
2. Mobile: logout/login cliente → aceptar permiso notificaciones Android.
3. Esperar push «Bienvenido a Emergencias Viales» (primer registro token).
4. Logs: `FCM multicast enviado: success=1`.
5. CU37 elige taller → push va al **portal taller** (responsable), no al cliente. Para probar push cliente: mensaje chat, cambio estado, pago simulado.

## ALTA — Activar y probar push web (2026-06-04)

1. `.env` raíz: `FCM_ENABLED=true`, `FIREBASE_WEB_ENABLED=true` + claves `FIREBASE_WEB_*` (proyecto `transporte-si2`).
2. `cd frontend && npm run env:sync` y rebuild frontend.
3. Aplicar migración `0027_taller_fcm_notificaciones.sql` (DB existente: `docker compose exec db psql ...` o reinicio init).
4. Login portal taller → campana notificaciones; aceptar permiso navegador; verificar token en `usuario_fcm_tokens`.
5. Desde mobile cliente: CU37 elegir taller → push + fila in-app en bandeja taller.

## ALTA — Validar red talleres + horarios (2026-06-04)

1. `docker compose up -d --build backend frontend` (migración `0026_taller_horarios.sql`).
2. Seeds: `docker compose exec backend python -m app.seeds`.
3. Verificar **6 talleres** en org `demo-sc` (cada uno con ≥1 técnico) — ver `docs/CREDENCIALES_DEMO.md`.
4. Portal taller → **Horarios** — cambiar franja; probar fuera de horario (ranking mobile + aceptar bandeja).
5. Login móvil técnico: p. ej. `marco.salas@sc-demo.test` / `scdemo1` org `demo-sc`; probar `andres.vargas@` (4to Anillo).

## MEDIA — Validar panel cliente mobile Paleta A (2026-06-05)

1. `cd mobile && flutter run` (o hot reload si ya corre).
2. Login cliente `carlos.vega@sc-demo.test` / `scdemo1` org `demo-sc`.
3. Revisar home, bottom nav, perfil, vehículos, notificaciones, flujo emergencia.
4. Probar chip org (cambia slug persistido; requests usan nuevo `X-Tenant-Slug`).

## ALTA — Reportes portal taller (2026-06-05)

1. `docker compose up -d --build backend frontend` (migración `0025_reportes_modulo.sql` + `openpyxl`/`reportlab`).
2. **Cerrar sesión y volver a entrar** en `/taller` (permisos `reportes:*` en JWT).
3. Ir a **Emergencias → Reportes** (`/taller/panel/reportes`).
4. Probar texto: `comisiones pendientes de este mes en excel y pdf` → vista previa + descargas automáticas.
5. Probar plantilla sistema «Comisiones pendientes» → Ejecutar → export manual Excel/PDF/CSV.
6. Guardar plantilla personalizada y eliminarla.
7. Micrófono: Chrome/Edge; si falla, usar textarea o `POST .../voice` con IA (`AI_ENABLED=true`).

## ALTA — Restore backup taller tras eliminar técnico (2026-06-05)

1. `docker compose up -d --build backend` (fix FK `tecnicos` → `usuarios`).
2. Crear **backup manual nuevo** (los viejos no traen `usuarios.csv`).
3. Eliminar un técnico sin historial → Restaurar el backup nuevo → debe reaparecer técnico + cuenta.
4. Backup antiguo (#9 etc.): restore ya **no falla**, pero no recupera técnicos cuya cuenta fue borrada.

## ALTA — CRUD técnicos y clientes (2026-06-05)

1. Aplicar migración `0023_taller_clientes_crud_permisos.sql` (`docker compose exec db psql ...` o rebuild en volumen nuevo).
2. `docker compose up -d --build backend frontend`.
3. **Cerrar sesión y volver a entrar** en `/taller` (permisos `clientes:crear|actualizar|eliminar` en JWT).
4. Probar **Técnicos**: desactivar / eliminar (409 si tiene atenciones).
5. Probar **Cuentas clientes**: crear, editar, desactivar, eliminar (409 si tiene vehículos/solicitudes/pagos).

## ALTA — Backups portal taller (2026-06-05)

1. `docker compose up -d --build backend backup-scheduler frontend` (migración `0022_taller_backup.sql`).
2. Login `/taller` como responsable → **Equipo y taller → Backups**.
3. Configurar hora **03:00**, activar automático, guardar.
4. Crear backup manual → Descargar / Restaurar (con confirmación).
5. Si 403: cerrar sesión y volver a entrar (permiso `backup_taller:gestionar` en JWT).

## ALTA — Verificar backups plataforma (admin)

1. `docker compose up -d --build backend backup-scheduler frontend` (migración `0021_backup_modulo.sql`).
2. Login admin superadmin `patricio.mendez@sc-demo.test` / `scdemo1` → **Plataforma SaaS → Backups**.
3. Crear backup **Plataforma** → estado `COMPLETADO` → Descargar `.sql.gz`.
4. Verificar contenedor: `docker compose logs backup-scheduler --tail 50` (runner periódico + retención).
5. Opcional: backup **TENANT** eligiendo org `demo-sc`; backup **EVIDENCIAS** si hay archivos en `uploads/evidencias`.

## ALTA — Bitácora portal taller (2026-06-05)

1. `docker compose up -d --build backend frontend` (aplica migración `0020_taller_bitacora_permiso.sql`).
2. Login `/taller` como responsable demo → **Equipo y taller → Bitácora**.
3. Verificar: aparecen login, técnicos, bandeja, suscripción; no aparecen acciones de clientes ni otros talleres.
4. Si el menú no muestra Bitácora: cerrar sesión y volver a entrar (permisos en JWT/`/auth/me`).

## ALTA — Verificar panel taller (2026-06-05)

1. Hard refresh **Ctrl+Shift+R** en `http://localhost/taller/panel` como `luis.rivera@sc-demo.test`.
2. Navegar sidebar: Resumen, Solicitudes, Mis solicitudes, Historial, Mi taller, Técnicos, Roles, Clientes.
3. Si algo sigue en "Cargando…", revisar consola DevTools (Network debe ser 200) y el componente hijo de esa ruta.

## ALTA — Planes y precios + Stripe (2026-06-05)

1. `.env` raíz: `STRIPE_SECRET_KEY=sk_test_...`, `STRIPE_PUBLISHABLE_KEY=pk_test_...` (y opcional `STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true`).
2. `docker compose up -d --build backend` — al arrancar crea/sincroniza `price_...` en Stripe test y en `pricing_plans`.
3. Panel taller → **Planes SaaS** → Upgrade Pro/Max → Stripe Checkout → tarjeta test `4242...` → vuelta con plan actualizado (confirm por `session_id`, sin webhook en local).
4. **Producción:** configurar webhook Stripe → `/api/webhooks/stripe-saas` + `STRIPE_SAAS_WEBHOOK_SECRET`.
5. **Dev alternativo:** `stripe listen --forward-to localhost:8000/api/webhooks/stripe-saas`.
6. Opcional override manual: `STRIPE_SAAS_PRICE_PRO` / `STRIPE_SAAS_PRICE_MAX` o Admin → Planes y precios.

## ALTA — Login panel admin (verificado 2026-06-04)

1. ~~Seeds CLIENTE bloqueaban arranque~~ — corregido con `asignar_roles_usuario_seed`.
2. Usar solo **`patricio.mendez@sc-demo.test`** / **`scdemo1`** en `/admin/login`.
3. Tras `docker compose up --build`, migraciones y seeds demo corren solos (entrypoint); login admin sin `alembic stamp` manual.
4. Opcional UX: mensaje distinto si el usuario existe pero no tiene rol ADMIN.

## MEDIA — Admin SaaS organizaciones

1. ~~Fix 422 al crear org (slug mayúsculas)~~ — hecho 2026-06-04.
2. ~~Dropdown planes comerciales Free / Pro / Max~~ — hecho 2026-06-05 (`saas-plan-tiers.ts`).
3. Probar en UI: crear org con plan **Pro** → en `/taller/panel/suscripcion` debe mostrarse Pro (no enum interno).
4. Revisar en `/admin/panel/planes-precios` que Pro y Max tengan `stripe_price_id` distintos si ambos son de pago.
5. Si el frontend Docker no refleja cambios: `docker compose up -d --build frontend`.

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
