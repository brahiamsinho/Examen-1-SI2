# HANDOFF_LATEST.md
# =========================================================
# Handoff para el próximo agente/sesión
# Fecha: 2026-06-05 (Notificaciones + fixes panel taller/admin + optimización main)

## Cambios recientes (2026-06-05) — Notificaciones inmediatas del servicio ✅

- **Paquete:** `comunicacion_y_notificaciones`.
- **Backend:** `eventos_servicio.py`, `tenant_guard.py`, migración `0020`.
- **Eventos:** selección taller → taller; aceptar/rechazar bandeja; asignación técnico; cambio estado.
- **API taller:** `GET/PATCH /api/app/taller/notificaciones`.
- **Frontend:** `/taller/panel/comunicacion/notificaciones`.
- **Mobile técnico:** `/tecnico/app/notificaciones`.
- **Sesión:** `docs/ai/sessions/2026-06-05-agent-notificaciones-reimplementacion.md`.

## Cambios recientes (2026-06-05) — Fix panel taller atascado en "Cargando…" ✅

- **Síntoma:** casi todo el sidebar del panel taller (`/taller/panel/*`) quedaba en "Cargando…" aunque las APIs respondían 200.
- **Causa:** componentes hijos lazy-loaded sin migrar a OnPush + signals + `markForCheck` tras refactor Fase 1 del shell.
- **Fix:** 10 componentes taller → OnPush, `loading` signal, `finalize` + `takeUntilDestroyed`, templates `loading()`.
- **Build:** `docker compose build frontend && docker compose up -d frontend` — OK.
- **Sesión:** `docs/ai/sessions/2026-06-05-agent-fix-taller-panel-loading.md`.

## Cambios recientes (2026-06-05) — Fix organizaciones atascadas en "Cargando…" ✅

- **Síntoma:** `/admin/panel/organizaciones` quedaba en "Cargando…" aunque `GET /api/admin/tenants` respondía 200.
- **Causa:** `admin-organizaciones` no migrado al patrón OnPush + signals + `markForCheck` del refactor Fase 1; peticiones duplicadas shell + página.
- **Fix:** `admin-organizaciones.component` OnPush, signals `loading`/`tenants`, `finalize` + `takeUntilDestroyed`; `AdminApiService.listTenants()` con `shareReplay` + `invalidateTenantsList()`; bootstrap excluye `99_*.sql`.
- **Sesión:** `docs/ai/sessions/2026-06-05-agent-fix-organizaciones-loading.md`.

## Cambios recientes (2026-06-04) — Docker optimización ✅

- **Mailpit** en lugar de Mailhog (imagen ~25 MB); alias `mailhog` en red Docker.
- Initdb: migraciones **0018/0019** + `99_register_sql_migrations.sql` (arranque backend más rápido en BD nueva).
- `frontend` → `depends_on: backend: condition: service_healthy`.
- Stripe env con defaults vacíos; ai-inference multi-stage + `aiuser`.
- Override dev: comentario OneDrive/bind mount.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-docker-optimizacion.md`.

## Cambios recientes (2026-06-04) — Refactor rendimiento Fase 1 ✅

- **Rama:** `feature/optimizando`.
- **Landing:** OnPush, scroll throttled, forkJoin pricing API.
- **Dashboard:** barras precalculadas, formatter money compartido.
- **Listados:** signals/computed en permisos, roles, usuarios, talleres (admin + taller).
- **Shells:** OnPush admin y taller.
- **Utils:** `list-filter.util.ts`, `format-money.util.ts`.
- **Backend:** overview admin en paralelo (`asyncio.gather`); cache planes públicos 5 min; `GET /api/public/pricing/bootstrap`; landing usa bootstrap.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-refactor-performance-fase1.md`.

## Cambios recientes (2026-06-04) — Admin planes y precios + Stripe ✅

- **Pedido:** ocultar Roles/Permisos del sidebar admin; gestionar planes de la landing + pasarela Stripe.
- **Sidebar:** grupo **Comercial → Planes y precios** (superadmin); quitado grupo Acceso del menú.
- **Admin UI:** `/admin/panel/planes-precios` — editar precio, beneficios, CTA, `stripe_price_id`, activo/destacado.
- **Landing:** planes desde API pública; checkout Stripe con modal de email.
- **Backend:** migración `0019_pricing_plans.sql`.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-admin-planes-precios-stripe.md`.

## Cambios recientes (2026-06-04) — Rediseño panel taller + accesos ✅

- **Pedido:** UI/UX del panel taller debe cubrir técnicos **y** usuarios/cuentas clientes, roles y permisos.
- **Shell:** sidebar agrupada (General, Emergencias, Equipo, Accesos y cuentas), iconos, colapsable, mobile drawer, acento verde — patrón admin.
- **Rutas:** `/taller/panel/accesos/usuarios|clientes|roles|permisos` con guards por permiso JWT.
- **Backend:** migración `0018_taller_acceso_permisos.sql`; `GET /clientes` con tenant + datos usuario; dashboard con KPIs usuarios/clientes.
- **Interceptor:** Bearer taller en APIs compartidas cuando la SPA está en `/taller/panel`.
- **Probar:** re-login en `/taller` tras migración para refrescar permisos en JWT.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-taller-panel-accesos-redesign.md`.

## Cambios recientes (2026-06-04) — Login taller: selector de organización ✅

- **Pedido:** en `/taller`, el slug de organización debe ser seleccionable (no texto libre).
- **Implementación:** `PublicApiService` → `GET /api/public/tenants`; `taller-login` carga orgs activas y muestra `<select>` con `nombre (slug)`.
- **Preselección:** query `?org=` → localStorage `ev_tenant_slug` → primera org de la lista.
- **Archivos:** `public-api.service.ts`, `taller-login.component.{ts,html,scss}`.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-taller-login-org-select.md`.

## Cambios recientes (2026-06-04) — Fix provision taller (422 teléfono corto) ✅

- **Síntoma:** al crear taller en admin, error genérico / confuso; logs `POST /api/talleres/provision` → **422**.
- **Causa:** `telefono_contacto` con valor `"123"` (< 5 caracteres exigidos por Pydantic). El email del responsable sí era válido; el contacto del taller no se copió automáticamente.
- **Fix backend:** `TallerProvisionIn` — `@model_validator` rellena `telefono_contacto` / `email_contacto` desde datos del responsable si faltan o son demasiado cortos.
- **Fix frontend:** validación local + `apiErrorMessage()` con mensajes legibles (422/409); hint «mín. 5 dígitos» en el campo teléfono contacto.
- **Nota:** si reintentas con el mismo email tras un intento parcial exitoso, verás **409** «El email ya está registrado» — el taller `Angelica` en org `si2-angelica` ya se creó en prueba API.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-fix-provision-taller-telefono.md`.

## Cambios recientes (2026-06-04) — Docker entrypoint migraciones + seeds ✅

- **Objetivo:** al `docker compose up --build`, el backend aplica migraciones y seeds sin pasos manuales.
- **Entrypoint:** `backend/Dockerfile` → `python -m app.db.docker_bootstrap` → uvicorn.
- **Migraciones:** Alembic (`stamp head` si initdb ya creó esquema; si no `upgrade head`) + SQL `0002`–`0017` vía tabla `app_sql_migrations`.
- **Seeds:** `app/seeds/runner.py` compartido; en Compose dev `SEED_*_ON_START=true` y `RUN_SEEDS_IN_LIFESPAN=false` (evita doble ejecución con `--reload`).
- **Vars:** `RUN_MIGRATIONS_ON_START`, `RUN_SEEDS_ON_START`, `RUN_SEEDS_IN_LIFESPAN` (ver `.env.example`).
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-docker-migrations-seeds-entrypoint.md`.

## Cambios recientes (2026-06-04) — Fix login panel admin ✅

- **Síntoma:** `/admin/login` → *"Tu cuenta no tiene rol de administrador"* (a veces 502 al reiniciar Docker).
- **Causas:** (1) credencial taller (`luis.rivera@sc-demo.test`) usada en portal admin; (2) seeds `dev_cliente` fallaban 8× al arranque porque `asignar_roles_usuario` bloquea rol `CLIENTE` → backend lento → 502.
- **Fix:** `asignar_roles_usuario_seed()` en `roles/service.py`; seeds `dev_cliente.py` y `dev_stress_visual.py` migrados.
- **Login admin demo:** `patricio.mendez@sc-demo.test` / `scdemo1` (rol `ADMIN`, superadmin plataforma).
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-fix-admin-login-seeds-cliente.md`.

## Cambios recientes (2026-06-04) — Fix crear organización ✅

- **Problema:** `POST /api/admin/tenants` devolvía **422** (validación Pydantic) si el slug tenía mayúsculas o espacios; la UI mostraba *"¿slug duplicado?"* (mensaje engañoso).
- **Causa:** el pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$` se aplicaba **antes** de normalizar; duplicado real sería **409** con `"Slug de tenant ya existe"`.
- **Fix backend:** `tenants/schemas.py` — `normalize_tenant_slug()` + `@field_validator("slug", mode="before")`; `service.py` reutiliza el helper.
- **Fix frontend:** `admin-organizaciones.component.ts/html/scss` — normaliza slug al escribir, validación local, `apiErrorMessage()` distingue 409/422/400.
- **Verificado:** API 201 con body `{"slug":"Nueva-Org-Test",...}` → tenant id 3 slug `nueva-org-test`.
- **Sesión:** `docs/ai/sessions/2026-06-04-agent-fix-crear-organizacion-slug.md`.

## Cambios recientes (2026-06-04) — Admin provision taller ✅

- **`POST /api/talleres/provision`:** usuario ACTIVO + rol `TALLER_RESPONSABLE` + taller con `tenant_id` (atómico).
- **Admin Talleres:** formulario único (datos taller + credenciales login `/taller`); éxito muestra slug + email.
- **Sidebar:** quitado menú **Usuarios**; altas de responsable solo desde Talleres.
- **Docs:** DEC-030, `FLOWS_PORTAL_TALLER.md` §6, sesión `2026-06-04-agent-admin-provision-taller.md`.
- **Probar:** superadmin → Talleres → Nuevo taller → login `/taller` con slug de la org.

## Ciclo 4 — estado implementación (CU36–CU40)

| CU | Estado | Notas rápidas |
|----|--------|----------------|
| CU36 | ✅ REST + polling mobile 12 s | Pendiente opcional: WebSocket |
| CU37 | ✅ UI + API candidatos/seleccionar | Ya no bandeja masiva al crear solicitud |
| CU38 | ✅ Stripe + simulado | Stripe real solo si `STRIPE_*` en `.env` y contenedor backend recreado |
| CU39 | ✅ | PATCH técnico + presupuesto |
| CU40 | ✅ | SaaS fases 1–3 |

**Docs PUDS:** `docs/puds/casos-uso/CICLO4_SEGUIMIENTO_TIEMPO_REAL.md`, `CICLO4_DETALLE_CASOS_USO.md` (actualizados 2026-05-28).  
**Sesión código CU37/CU36:** `docs/ai/sessions/2026-06-02-agent-cu37-cu36-mobile.md`.  
**Probar CU37:** `carlos.vega@sc-demo.test` / `scdemo1`, tenant `demo-sc` → emergencia → Elegir taller.  
**Probar Stripe:** `docker compose up -d --force-recreate backend` tras poner claves; `settings.stripe_enabled` debe ser `True`.

## Documento oficial del examen (fuente académica)

- **Archivo:** `c:\Users\brahi\Downloads\Segundo EXAMEN SI2 2026_Ciclos_4_5.docx`
- **Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares — INF412 — Grupo 39.
- **Ciclo 4 (CU36–CU40):** tiempo real/tracking, selección taller, pago pasarela, estado atención técnico, multi-tenant SaaS.
- **Ciclo 5 (CU41–CU46):** notificaciones, cotización, offline/sync, tiempo reparación, emergencia sin conexión, dashboard KPIs.
- **4.1.5** Modelo general de casos de uso → EA diagrama **26** (solo CU36–CU40 + CU2 include); **Dependency** + `include`/`extend`; actores → **Association**.
- **Repo alineado:** `docs/puds/casos-uso/CICLO4_DETALLE_CASOS_USO.md`, `MODELO_GENERAL_CASOS_USO.md`.
- **Pendiente en el Word:** muchas secciones 4.2–4.5 son índice/placeholder (análisis, diseño secuencia, despliegue, pruebas) — completar artefactos PUDS.
- **4.2.1 Identificación paquetes CU:** EA paquete **11**, diagrama **27**; doc `docs/puds/analisis/IDENTIFICACION_PAQUETES_CU.md`; PlantUML D-004.
- **4.2.2 Relacionar paquete↔CU (`<<trace>>`):** EA diagramas **28–32** (5 diagramas); PlantUML en `docs/diagrams/uml/paquetes-cu/rel-pkg01..05-*.puml`.
- **4.2.1.3 Vista de paquetes / encapsular:** EA diagramas **33–37** (`VISTA-PKG01`…`05`, IDs **34,33,37,35,36**); PlantUML `vista-pkg01..05-*-encapsular.puml`; conectores asoc. **372–387**, extend **375**, **382**.
- **4.2.4 Analizar paquete:** EA diagrama **38** `DIAGRAMA GENERAL DE PAQUETES`; contenedor elementID **191**; deps PKG **388–392**; `docs/puds/analisis/ANALIZAR_PAQUETE_4_2_4.md`; PlantUML `diagrama-general-paquetes-analizar.puml`.
- **4.3.1.1 Diseño físico (despliegue):** EA package **4**, diagrama **9** renombrado `4.3.1.1 Diseño físico - Despliegue Azure`; PlantUML D-006 actualizado (Azure→Ubuntu→Docker→FE/BE/BD/IA/Mailhog); doc `docs/puds/diseño/DISEÑO_FISICO_4_3_1_1_DESPLIEGUE.md`.
- **4.3.1.2 Diseño lógico (paquetes MVC):** EA package **12**, diagrama **39**; PlantUML D-007; doc `docs/puds/diseño/DISEÑO_LOGICO_4_3_1_2_PAQUETES.md`.
- **Diagrama componente principal:** EA package **13**, diagrama **40**; PlantUML D-008; script `scripts/ea-create-componente-principal.ps1`; doc `docs/puds/diseño/DISEÑO_COMPONENTE_PRINCIPAL.md`.
- **MCP EA:** `.cursor/mcp.json` incluye `Enterprise Architect` con `-enableEdit` (reiniciar Cursor para usar MCP en chat).

## Índice documentación — sesión 2026-05-28 (hasta este momento)

| Tema | Documento principal |
|------|---------------------|
| Flujos `/taller` (registro, login, panel) | **`docs/ai/FLOWS_PORTAL_TALLER.md`** |
| Secuencia UML registro→login | `docs/diagrams/uml/sequence-taller-registro-login.puml` |
| Landing rediseño (plan + implementación) | `docs/ai/LANDING_REDESIGN_PLAN.md`, sesión `2026-05-28-agent-landing-paleta-a-dark.md` |
| Admin SaaS usuarios/talleres | `docs/ai/sessions/2026-05-28-agent-saas-admin-usuarios-talleres.md` |
| Consolidación sesión | `docs/ai/sessions/2026-05-28-agent-documentacion-flujos-landing.md` |

**Regla rápida:** crear taller ≠ login; registro en `/taller/registro`; login solo en `/taller`.

## Cambios recientes (2026-05-28) — Documentación flujos portal taller ✅

- Análisis formalizado: registro público, verificación email, login con `X-Tenant-Slug`, panel `require_taller_responsable`, contraste `POST /api/talleres/` admin.
- DEC-029 en `DECISIONS_LOG.md`.

## Cambios recientes (2026-05-28) — Landing Paleta A (Dark Pro Soft) ✅

- Implementado plan **`docs/ai/LANDING_REDESIGN_PLAN.md`** — Paleta A, fases 1–3.
- Archivos: `frontend/src/app/public/pages/landing/landing-page.component.{html,scss,ts}`, fuentes en `frontend/src/index.html` (Outfit + Inter).
- Hero: product frame + filas preview; sección bento `#producto`; pricing/accesos/flujo/módulos/CTA; nav glass oscuro al scroll.
- Ver sesión: `docs/ai/sessions/2026-05-28-agent-landing-paleta-a-dark.md`.
- Probar: `docker compose up -d --build frontend` → `http://localhost/` (Ctrl+Shift+R).

## Cambios recientes (2026-05-28) — Admin SaaS usuarios/talleres ✅

- Panel **Usuarios:** no lista ni asigna rol `CLIENTE`; alta con `tenant_id` según organización del selector superior; opción “cuenta de plataforma” para superadmin.
- Panel **Talleres / Usuarios:** filtro de organización **en la página** (sincronizado con navbar); modal «Nuevo taller» / «Crear usuario» con selector de organización en el formulario (no obliga usar solo el navbar).
- **Clientes:** solo registro móvil con slug (`X-Tenant-Slug`); ver `docs/ai/sessions/2026-05-28-agent-saas-admin-usuarios-talleres.md`.
- Rebuild: `docker compose up -d --build backend frontend`.

## Cambios recientes (2026-05-29) — Login admin “colgado” con API OK ✅

- **Síntoma:** URL `/admin/panel`, login visible, pero `POST /auth/login 200` y `GET /api/admin/* 200`.
- **Causas UI:** (1) `withViewTransitions()` — quitado; (2) login en ruta hermana `''` de `panel` — **login movido a `/admin/login`**; (3) `router.navigate` dejaba DOM del login — **tras login: `location.assign('/admin/panel')`** (recarga completa).
- **Guards:** `adminGuestGuard` en login; `adminAuthGuard` redirige a `/admin/login`.
- **Bundle nuevo:** `main-AOKVAZW2.js`, `chunk-6BFN7Q7Z.js` (shell). `docker compose build frontend && docker compose up -d frontend`.
- **Credenciales:** `patricio.mendez@sc-demo.test` / `scdemo1`.
- **Probar:** `http://localhost/admin/login` (o `/admin` redirige) → **Ctrl+Shift+R**; tras login debe verse sidebar “Resumen”, no el formulario.

## Cambios recientes (2026-05-28) — Skill UML/C4/PUDS + subagentes sincronizados ✅

- Skill **`.cursor/skills/uml-c4-puds-diagrams/`** — checklist UML 2.5+, C4 4 capas, draw.io, memoria.
- **`docs/ai/SKILLS_REGISTRY.md`** creado.
- Subagentes actualizados: `orchestrator`, `puds`, `docs-memory`, `diagrams-modeling` (MCP `user-drawio`, delegación clara).

## Cambios recientes (2026-05-28) — C4 4 capas + draw.io + UML 2.5 + PUDS ✅

- Modelo **C4 completo** (Context, Container, Component, Code): `docs/diagrams/c4/01`…`04` + índice `c4/README.md`.
- Puente draw.io con notación C4 nativa (`C4Context`, `C4Container`, `C4Component`) en `drawio/mermaid/01`…`04-*-c4.mmd`; abiertos vía MCP **`user-drawio`**.
- **UML 2.5+ obligatorio** reforzado: despliegue = D-006 + `deployment-docker-azure-uml.mmd` (no mezclar C4/Docker).
- **`docs/ai/PUDS_GUIDE.md`** creado — fases PUDS, trazabilidad CU→diagrama→código, cuándo usar C4 vs UML.
- Memoria actualizada: `diagrams/agent-memory/HANDOFF.md`, `LEARNINGS.md`, `RULES.md`, sesión `2026-05-28-agent-c4-drawio-uml25-puds.md`.
- **Pendiente usuario:** guardar `.drawio` en `docs/diagrams/drawio/`; reset EA manual si aplica.

## Cambios recientes (2026-05-28) — MCP draw.io + integración EA ✅

- `.cursor/mcp.json` con `npx -y @drawio/mcp` (servidor `drawio`).
- `docs/diagrams/drawio/mermaid/` (C4 context + containers), `DRAWIO_INTEGRATION.md`, `MCP_SETUP.md`.
- Flujo: PlantUML (Git) + EA (modelo) + draw.io (visual). DEC-027.

## Cambios recientes (2026-05-28) — Subagente diagramas + docs/diagrams/ ✅

- Subagente **`diagrams-modeling`**: PlantUML, UML 2.5+, C4, skill `plantuml-ascii`, MCP Enterprise Architect (con EA abierto).
- **`docs/diagrams/`** + memoria **`docs/diagrams/agent-memory/`** (RULES, LEARNINGS, no repetir errores).
- Diagramas iniciales: C4 context/container, UML paquetes backend, secuencia alta emergencia cliente.
- **`docs/ai/DIAGRAMS_GUIDE.md`**, **`PACKAGE_DESIGN.md`**; `orchestrator` y `puds` actualizados; DEC-026.
- Sesión: `docs/ai/sessions/2026-05-28-agent-diagrams-modeling-subagent.md`.

## Cambios recientes (2026-05-24) — SaaS fase 3 ✅

- Migración `0017`, API pública, billing Stripe (checkout/portal/webhook), subdominio Host, tests `test_multitenancy_phase3.py`, mobile/taller org slug, `require_writable_tenant_subscription`.
- Ver `docs/ai/SAAS_PHASE3_PLAN.md`, DEC-025.

## Cambios recientes (2026-05-24) — SaaS multi-tenant fase 2 ✅

- Migración `0016_multitenancy_phase2.sql` (RLS, unicidad por tenant, Stripe en `tenants`), middleware `X-Tenant-Slug`, contexto auth en `get_db`, login/me ampliados, panel Angular organizaciones + selector tenant.
- Sesión: `docs/ai/sessions/2026-05-24-agent-saas-multitenancy-fase2.md`, DEC-024.
- BD existente: aplicar `0016` con `psql` (ver `NEXT_STEPS.md` 0b).

## Cambios recientes (2026-05-24) — SaaS multi-tenant fase 1 ✅

- Migración `0015_multitenancy_saas.sql`, módulo `tenants`, `AuthContext`, JWT `tenant_id`, filtros finanzas/bandeja, seeds `dev_tenant`.
- Skills: `multitenancy`, `multi-tenant-safety-checker`.
- Sesión: `docs/ai/sessions/2026-05-24-agent-saas-multitenancy-fase1.md`, DEC-023.

## Cambios recientes (2026-05-24) — Subagentes ai-inference, qa-testing, security ✅

- Nuevos roles en `.cursor/agents/`:
  - **`ai-inference`** — operación e implementación del stack IA del repo (worker + módulo backend + env Docker); complementa **`ai-researcher`** (investigación previa).
  - **`qa-testing`** — estrategia y ejecución de pruebas (pytest, Flutter, manual, `TESTING_STRATEGY.md`).
  - **`security`** — auditoría JWT/permisos/secretos/Stripe/FCM/uploads.
- **`orchestrator.md`**: clasificación ampliada (ia, qa, seguridad) + tabla de delegación rápida.
- Sesión: `docs/ai/sessions/2026-05-24-agent-subagentes-ia-qa-security.md`.
- Decisión: `DECISIONS_LOG` **DEC-022**.

## Cambios recientes (2026-05-30) — EA CU36 comunicación **lineal MVC** (MCP) ✅

- **`/Model/Comunicacion`** → **`comm CU36 lineal MVC flujo principal`** (diagramID **40**).
- Topología: `Cliente → V.Seguimiento → SeguimientoController → entidades` (sin estrella, sin V.Error en lienzo).
- Mensajes 538–545; Association 533–537 ocultas en diagrama 40.
- Sesión: `docs/ai/sessions/2026-05-30-agent-ea-cu36-lineal-mvc-mcp.md`
- **Manual:** separar etiquetas Cliente–Vista (1.Abrir, 1.1, 1.6).

## Cambios recientes (2026-05-29) — EA arquitectura del sistema (componentes) ✅

- Paquete **`Model/Arquitectura`** (packageID **28**).
- Diagrama oficial **`component Arquitectura del sistema`** (diagramID **31**): hub FastAPI, módulos alineados a `ARCHITECTURE.md`, capas, PostgreSQL, medios, externos, `ai-inference`.
- Guía: `docs/ai/EA_ARCHITECTURE_SYSTEM_GUIDE.md`.
- Sesión: `docs/ai/sessions/2026-05-29-agent-ea-arquitectura-sistema.md`.

## Cambios recientes (2026-05-29) — EA análisis de clases: patrón simplificado ✅

- **Guía obligatoria** para nuevos CUs: `docs/ai/EA_ANALYSIS_CLASS_GUIDE.md` (1 vista, 1–2 controles, 2–4 entidades; sin V.Error ni pantallas de otros CUs).
- **Seleccionar taller:** diagrama oficial ID **26** en `Model/Clase`; obsoleto ID 25.
- **CU36 ubicación:** análisis ID **27**; comunicación ID **22** en `Model/Comunicacion`.
- **Procesar pago pasarela:** análisis ID **28** en `Model/Clase` (2 vistas: Resumen + Pasarela).
- **Actualizar estado atención (técnico):** análisis ID **29** en `Model/Clase`.
- **Gestionar tenant (admin SaaS):** análisis ID **30** — diseño lógico; API tenant aún no en código.
- Guía BCE: máximo **2** boundaries por CU (`EA_ANALYSIS_CLASS_GUIDE.md`).
- Draw.io comunicación: `docs/diagrams/*-comunicacion.drawio` (CU36–CU40).
- Decisión: `DECISIONS_LOG` **DEC-037**, **DEC-038**.

## Cambios recientes (2026-04-26) — Word `pruebas_api_servicio` + Prueba 2 mapeo ✅

- `docs/ai/TESTING_STRATEGY.md` incorpora: nota sobre el `.docx` (no leíble como texto en el IDE), explicación de que **no** hay `POST /servicios` con Spa/horarios, tabla y sección con **Prueba 2** equivalente a `POST /api/app/cliente/emergencias` (201) o `.../bandeja/{id}/aceptar` (200) + `curl` de ejemplo.
- Sesión: `docs/ai/sessions/2026-04-26-pruebas-api-servicio-docx-prueba-2.md`.

## Cambios recientes (2026-04-26) — Documentación pruebas API recurso `servicios` ✅

- Se creó `docs/ai/TESTING_STRATEGY.md` con 10 pruebas funcionales para `GET /servicios/{id}` y `GET /servicios` (existente, inexistente, ID inválido, ID negativo, post-delete, consistencia, post-update, lista completa, lista vacía y alto volumen).
- Se incluyó plantilla `curl`, criterios de aceptación y nota de mapeo: en el backend actual no hay ruta `/servicios` aún.
- Sesión: `docs/ai/sessions/2026-04-26-testing-strategy-servicios-api.md`.

## Cambios recientes (2026-04-26) — Dashboard admin financiero (KPIs comisiones/reportes) ✅

- Se implementó módulo backend `admin_finanzas` (`schemas.py`, `service.py`, `router.py`) para exponer métricas financieras globales desde `comisiones_taller`, `pagos` y `solicitudes_emergencia`: comisión total plataforma (10 %), pagos confirmados, ticket promedio, conversión de finalizadas→pagadas, top talleres y serie diaria.
- Se actualizó `frontend/src/app/admin/features/dashboard/` para mostrar filtros de fecha, tarjetas KPI, top talleres y barras diarias de comisión dentro del panel administrador.
- Fix posterior: `admin.routes.ts` apuntaba a `./features/finanzas/admin-finanzas.component` inexistente y rompía `ng build`; se creó ese componente (wrapper standalone que renderiza `admin-dashboard`) para que compile y mantenga ruta `/admin/panel/finanzas`.
- Sesión: `docs/ai/sessions/2026-04-26-admin-dashboard-finanzas-kpis.md`.

## Cambios recientes (2026-04-26) — Pagos: registrar `comisiones_taller` al confirmar (ganancias dashboard) ✅

- Tras `PAGADO` (Stripe o simulado) ahora se crea fila en `comisiones_taller` (10 % comisión, neto al taller), alineado a `dev_demo_santa_cruz`. Sin esto, el landing/reportes del taller seguían con sumas en 0. Código: `backend/app/modules/pagos_y_comisiones/pagos/repository.py` + `service.py`. Sesión: `docs/ai/sessions/2026-04-26-pagos-comisiones-taller-dashboard.md`.

## Cambios recientes (2026-04-27) — `ai_payload` fijo en “Otros” tras subir foto (re-enriquecer IA) ✅

- Tras **crear** la solicitud el flujo móvil suele añadir **foto/ubicación después**; el `enrich` solo corría al `POST` inicial, así que `fuentes` quedaba `["texto"]` y `OTROS`. Ahora: `enrich` también tras **evidencias**, **ubicación** y **actualizar texto**; lectura local de `uploads/evidencias` para análisis de imagen. Sesión: `docs/ai/sessions/2026-04-27-agent-ia-payload-reenrich-evidencia.md`.

## Cambios recientes (2026-04-26) — YOLO: modelo Colab dejó de “reconocer” (en realidad usaba COCO) ✅

- **Causa:** `.env` tenía `YOLO_MODEL=yolov8n.pt` y por defecto `YOLO_TASK=detect`; el contenedor nunca usaba el clasificador en `backend/incidentes_emergencias_v1.pt` salvo que se uniera `docker-compose.ai-custom-model.yml` y se forzara classify.
- **Ajuste:** `.env` con `YOLO_TASK=classify`, `YOLO_MODEL=/models/incidentes_emergencias_v1.pt`, `YOLO_IMGSZ=224` **y** levantar con **`docker compose -f docker-compose.yml -f docker-compose.ai-custom-model.yml --profile ai up -d --build --force-recreate ai-inference`** (el segundo archivo monta el `.pt` en `/models/...`). Sesión: `docs/ai/sessions/2026-04-26-yolo-custom-model-compose-env.md`.

## Cambios recientes (2026-04-26) — Docker: Postgres `db` healthcheck + primer `up` ✅

- `docker-compose.yml` (`db`): `healthcheck.start_period: 240s`, `retries: 12` — init largo + reinicio post-init ya no debería marcar `unhealthy` por carrera con `pg_isready`. Ver `docs/ai/DOCKER_BUILD_OPTIMIZATION.md`.

## Cambios recientes (2026-04-26) — Docker: contexto `ai-inference` acotado + builds más livianos ✅

- `docker-compose.yml`: build de `ai-inference` con `context: ./services/ai-inference` (no toda la repo). Backend: `COPY --chown` (sin `chown -R`). `.dockerignore` backend/frontend/ai-inference ampliados. Detalle: `docs/ai/DOCKER_BUILD_OPTIMIZATION.md`.

## Cambios recientes (2026-04-26) — `.env` solo en la raíz del repo ✅

- Eliminado `backend/.env.example`; `config.py` solo carga `<repo>/.env`. Plantilla única: `.env.example` raíz. `mobile/.env` intacto. Sesión: `docs/ai/sessions/2026-04-26-env-solo-raiz.md`.
- Compose: `.env.example` documenta `TZ`/`PGTZ`/`YOLO_TASK`/Firebase; YAML mantiene fallbacks seguros para TZ, host Postgres, credenciales Firebase y `BACKEND_UPSTREAM` (evita warnings y valores vacíos con `.env` viejos). Sesión: `docs/ai/sessions/2026-04-26-compose-env-estricto.md`.

## Cambios recientes (2026-04-26) — Panel taller Angular: historial, mis solicitudes, comisiones ✅

- Sidebar y rutas bajo `/taller/panel/emergencias/`: **Mis solicitudes**, **Historial de atenciones**, **Servicios asignados**, **Comisiones**; consumen APIs existentes (`historial-atenciones`, `comisiones`, `comisiones/resumen`). Backend: `bandeja_id` opcional en `HistorialAtencionRead` y `ComisionTallerRead` para enlazar al detalle de bandeja. Sesión: `docs/ai/sessions/2026-04-26-taller-web-sidebar-historial-comisiones.md`.

## Cambios recientes (2026-04-26) — Paquete `comunicacion_y_notificaciones` (4 módulos) ✅

- Movidos `comunicaciones`, `dispositivos_push`, `mensajes_solicitud`, `notificaciones` → `modules/comunicacion_y_notificaciones/`; imports `app.modules.comunicacion_y_notificaciones.*`. `main`, `db_metadata`, `pagos`, `tecnico`, `atencion/taller_emergencias`, seeds. Sesión: `docs/ai/sessions/2026-04-26-backend-comunicacion-y-notificaciones.md`.

## Cambios recientes (2026-04-26) — Paquete `atencion` (`taller_emergencias`) ✅

- `modules/taller_emergencias` → `modules/atencion/taller_emergencias/`; imports `app.modules.atencion.taller_emergencias.*`. `main`, seeds, `incidentes` (solicitudes), `ai/repository`, tests. Sesión: `docs/ai/sessions/2026-04-26-backend-atencion-taller-emergencias.md`.

## Cambios recientes (2026-04-26) — Paquete `talleres_y_tecnicos` (`talleres`, `taller_responsable`, `tecnico`) ✅

- Movidos desde raíz de `modules/`: `acceso_y_administracion/talleres` → `talleres_y_tecnicos/talleres`, `taller_responsable`, `tecnico`. Imports `app.modules.talleres_y_tecnicos.*`; `acceso_y_administracion/__init__.py` actualizado. Sesión: `docs/ai/sessions/2026-04-26-backend-talleres-y-tecnicos-paquete.md`.

## Cambios recientes (2026-04-26) — Paquete `incidentes` (`emergencias` bajo `incidentes/emergencias`) ✅

- Movido `modules/emergencias` → `modules/incidentes/emergencias/`; imports `app.modules.incidentes.emergencias.*`; `main`, `db_metadata`, taller/tecnico/pagos/mensajes/notificaciones/ai/seeds/tests actualizados. URLs sin cambio. Sesión: `docs/ai/sessions/2026-04-26-backend-incidentes-emergencias-paquete.md`.

## Cambios recientes (2026-04-26) — Paquete `clientes_y_vehiculos` (clientes + vehiculos) ✅

- Carpetas movidas a `backend/app/modules/clientes_y_vehiculos/{clientes,vehiculos}/`; imports globales actualizados (regex evita doble `clientes_y_vehiculos`). `main.py`, `db_metadata`, emergencias, pagos, técnico, seeds, etc. Sesión: `docs/ai/sessions/2026-04-26-backend-clientes-y-vehiculos-paquete.md`.

## Cambios recientes (2026-04-26) — Carpeta `acceso_y_administracion` (auth, permisos, roles, usuarios, bitácora, talleres) ✅

- Se movieron esos seis paquetes a `backend/app/modules/acceso_y_administracion/`; se añadió `__init__.py` del padre; `main.py`, `db_metadata.py`, `dependencies.py`, el resto de módulos, seeds y tests quedaron con imports `app.modules.acceso_y_administracion.*`. Verificar en Docker/venv: `python -c "from app.main import app"`. Sesión: `docs/ai/sessions/2026-04-26-backend-acceso-y-administracion-paquete.md`.

## Cambios recientes (2026-04-26) — Módulos backend: auth / roles / permisos + notificaciones / push / mensajes ✅

- El monolito `backend/app/modules/acceso/` se reemplazó por **`auth`**, **`roles`**, **`permisos`** (mismas tablas y prefijos API).
- `comunicaciones` ya no concentra modelos ni un solo `service.py` grande: **`notificaciones`**, **`dispositivos_push`**, **`mensajes_solicitud`**; `comunicaciones/router.py` solo ensambla rutas.
- Imports afectados: seeds, `dependencies.py`, `pagos`, `portal_*`, `db_metadata`. Ver `docs/ai/sessions/2026-04-26-backend-modulos-acceso-comunicaciones.md` y `ARCHITECTURE.md`.

## Cambios recientes (2026-04-26) — Identidades seed (Santa Cruz, cuentas naturales) ✅

- **`identidades_demo_sc.py`:** emails `*.sc-demo.test`, pass `scdemo1`, tel. +591 77010010–014, nombres y talleres con razón social SC; `config.py` importa estos defaults; `docker-compose.yml` deja de usar +57/La Paz en fallbacks.
- Sesión: `docs/ai/sessions/2026-04-26-seed-identidades-santa-cruz.md`.

## Cambios recientes (2026-04-26) — Seed stress visual (catálogo + clientes extra) ✅

- **`dev_stress_visual`:** clientes extra `*.lista.sc-demo.test` + nombres SC; **`identidades_demo_sc.py`** centraliza emails/tel/pass de admin/cliente/taller/técnico/taller2; **`ensure_catalogos_vehiculo_stress_extra`** sin cambios de lógica. `docker-compose.yml` defaults Bolivia (+591, Santa Cruz).

## Cambios recientes (2026-04-26) — AVIF + analyze-batch resiliente ✅

- **`ai-inference`:** `pillow-heif` + `libheif1` en Docker; `register_heif_opener()` en `main.py` para decodificar AVIF/HEIF.
- **`backend` `router.py`:** `POST /api/ai/images/analyze-batch` no hace 502 si una foto falla: esa entrada lleva `resultado` con `hallazgos` de error y `confianza=0`; el resto sigue normal. `POST /api/ai/images/analyze` (una imagen) mantiene 502 ante fallo de inferencia.
- **Docs:** `DECISIONS_LOG` DEC-016; sesión `docs/ai/sessions/2026-04-26-agent-avif-analyze-batch-resilience.md`.

## Cambios recientes (2026-04-26) — Seed demo media prioridad (comunicaciones, IA, multi-taller) ✅

- **`backend/app/seeds/dev_demo_media_prioridad.py`:** notificaciones, chat, `ai_payload` demo, disponibilidad taller SC, segundo taller La Paz + bandeja retroactiva en `[DEMO-SC]`. Se encadena después de `ensure_demo_santa_cruz_datos` en `python -m app.seeds` y en `lifespan` si `SEED_DEMO_MEDIA_PRIORIDAD_ON_START=true`. Variables `SEED_TALLER2_*` documentadas en `.env.example` (raíz del repo).

## Cambios recientes (2026-04-26) — Seed demo Santa Cruz (emergencias + pagos) ✅

- **`backend/app/seeds/dev_demo_santa_cruz.py`:** vehículos y 10 solicitudes demo con contexto Santa Cruz de la Sierra; `python -m app.seeds` las ejecuta al final. Variable opcional `SEED_DEMO_SANTA_CRUZ_ON_START` para lifespan. Defaults `SEED_*_CIUDAD` Santa Cruz en `config` / `.env.example`.

## Cambios recientes (2026-04-26) — Confirmación pago: reusa intent iniciado, PI id correcto

- **Mobile** `pago_confirmacion_screen.dart`: si el paso método ya devolvió `PagoRead` coherente, no se vuelve a `POST /pagos`; `confirmarStripe` usa `stripePaymentIntentId` del modelo.

## Cambios recientes (2026-04-26) — Pago resumen muestra presupuesto técnico real ✅

- **Backend** `emergencias/schemas.py`: `SolicitudEmergenciaRead` ahora incluye `presupuesto_bob` y `presupuesto_registrado_at`; `SolicitudEmergenciaDetailRead` los hereda y `GET /portal/cliente/emergencias/{id}` los devuelve al mobile.
- **Mobile** `pago_resumen_screen.dart`: se mantiene la regla “cliente no escribe monto”, y se agrega refresco explícito (botón en app bar + pull-to-refresh) para sincronizar de inmediato cuando el técnico registra presupuesto.
- **Causa raíz del bug reportado:** la pantalla de pago leía `emergenciaDetailProvider` (endpoint detalle), pero `presupuesto_bob` solo estaba en seguimiento; por eso podía mostrar “no definido” aunque backend ya tuviera monto.

## Cambios recientes (2026-04-26) — Daños IA en UI, pago = presupuesto, Stripe solo tarjeta, Android `FlutterFragmentActivity` ✅

- **IA (mobile):** `damages` del `ai_payload` son objetos `DamagePrediction` → se parsean como `DanoIaV1` y se muestran en lista legible (no dump del Map).
- **Pagos:** con `presupuesto_bob` el cliente no edita monto; backend valida igualdad. `crear_pago` solo crea PaymentIntent Stripe si `metodo == TARJETA`. `PagoRead.requiereStripePaymentSheet(metodo)` exige tarjeta.
- **Android:** `MainActivity` → `FlutterFragmentActivity` para `flutter_stripe`.
- **FCM / go_router:** `FcmMessageListener` ya no usa `GoRouter.of(context)` (el listener está **encima** del router). Es `ConsumerStatefulWidget` y usa `ref.read(goRouterProvider)` para `go` y ruta actual; evita `No GoRouter found in context` y excepciones al recibir notificación en primer plano.

**Seguridad:** no pegar claves `sk_` en chats; rotar en Stripe si se expusieron.

## Cambios recientes (2026-04-25) — Fase 1 IA incidentes compuestos ✅

- **Objetivo cubierto:** soportar casos reales donde un incidente trae múltiples daños simultáneos (ej. choque + vidrios + llanta) y múltiples fotos.
- **Schemas IA extendidos** (`backend/app/modules/ai/schemas.py`):
  - Inputs multi-evidencia: `transcripciones_audio[]`, `hallazgos_vision_por_imagen[]`.
  - Output multi-daño: `damages[]`, `requires_manual_review`, `conflict_notes`.
- **Fusionador multimodal v1** (`backend/app/modules/ai/services/evidence_fusion.py`):
  - pesos: imagen 0.45, texto 0.30, audio 0.25.
  - agregación por evidencia y detección de conflictos.
  - mapeo a categoría principal (`pick_primary_category`).
- **Router IA**:
  - endpoint nuevo `POST /api/ai/images/analyze-batch` para `files[]` (varias fotos).
  - endpoint existente `POST /api/ai/images/analyze` se mantiene compatible.
- **Prioridad y resumen**:
  - `prioritize` ahora considera daños compuestos (`damages_considerados`, `score`).
  - `structured-summary` ahora devuelve `danos_detectados` y agrega síntesis de daños en `resumen`.
- **Tests backend actualizados** (`backend/tests/test_ai_engines.py`):
  - caso compuesto multi-daño,
  - prioridad con daños múltiples,
  - resumen estructurado con daños compuestos.
- **Mobile (cliente) alineado con payload compuesto**:
  - `mobile/lib/cliente/emergencias/domain/solicitud_ai_payload.dart` parsea nuevos campos del backend IA compuesto.
  - `mobile/lib/cliente/emergencias/presentation/widgets/ai/solicitud_ai_resumen_card.dart` renderiza daños detectados, score, conflictos y revisión manual.

## Cambios recientes (2026-04-25) — Fixes críticos reportados por pruebas reales ✅

- **Push técnico no recibido (aunque aparece en historial):** causa frecuente detectada en pruebas: el técnico registra token FCM *después* del evento (asignación/estado), por lo que no había token en el momento del envío.
  - Fix: `dispositivos_push/service.py` (paquete `comunicacion_y_notificaciones`) en `registrar_fcm_token` reenvía notificaciones no leídas recientes (hasta 10) cuando es el primer token del usuario.
- **Hora BOT incorrecta en mobile (01:38 vs 21:38):**
  - Causa: timestamps API sin zona (`timestamp without time zone`) eran parseados como hora local en Dart.
  - Fix: `mobile/lib/core/utils/api_datetime.dart` + adopción en modelos cliente/técnico/pagos/comunicación para tratar naive timestamps como UTC y luego convertir a BOT en UI.
- **ETA “vacía” en seguimiento:**
  - Fix de fallback en backend (`portal_tecnico_emergencias/service.py`): al pasar a `EN_CAMINO`, si `tiempo_estimado_min` es `NULL`, se setea `20` min.
- **Pago “de adorno” respecto al presupuesto técnico:**
  - Fix UX en mobile (`pago_resumen_screen.dart`): monto se prellena con `presupuesto_bob` y se informa explícitamente al cliente.

# =========================================================

## Normativa

**`AGENTS.md`** (raíz del repo): contrato de agente, PUDS, UI/UX, seguridad y **obligación de mantener `docs/ai/`** tras cambios relevantes.

## Qué es el proyecto

Plataforma de **emergencias vehiculares**: clientes, talleres, técnicos, auditoría. Stack: **FastAPI + PostgreSQL + Angular 17 + Flutter + Docker**.

## Cambios recientes (2026-04-25) — Push técnico + presupuesto BOB ✅

- **Push al asignar técnico:** `comunicaciones/service.py` → `notificar_tecnico_solicitud_emergencia`; invocado desde `portal_taller_emergencias/service.py` en `asignar_tecnico_a_solicitud` después del aviso al cliente.
- **FCM sin tokens:** `_notificar_push` escribe log `INFO` cuando el usuario destino no tiene filas en `usuario_fcm_tokens`.
- **Presupuesto BOB:** migración `backend/migrations/0014_presupuesto_bob_solicitud.sql` + `docker-compose` init `14_...`; `ActualizarEstadoServicioIn` exige `presupuesto_bob` si `nuevo_estado == EN_ATENCION`; seguimiento cliente y PATCH técnico devuelven los campos; Flutter: diálogo de monto (técnico) y tarjeta en seguimiento (cliente).
- **BD existente:** si el volumen de Postgres ya fue inicializado antes, aplicar `0014` a mano con `psql` (el init de Docker no se re-ejecuta).

### Docker build “frontend grpc server closed” (2026-04-25) ✅

- **Síntoma:** al hacer `docker compose ... up -d --build`, falla `target backend: failed to solve: frontend grpc server closed unexpectedly` (a veces con puntero a `Dockerfile:1` con `# syntax=docker/dockerfile:1`).
- **Causa típica:** inestabilidad de BuildKit / Docker Desktop (comunicación gRPC con el “Dockerfile front” externo o con daemon), no un error lógico del código de la app.
- **Ajuste en repo:** se quitaron `# syntax=docker/dockerfile:1` y `RUN --mount=type=cache` en `backend/Dockerfile` y `frontend/Dockerfile` (instalación pip/npm sin mount de caché; builds un poco más lentos, más estables en Windows). Si aún falla: reiniciar Docker Desktop, `docker buildx prune`, o `set DOCKER_BUILDKIT=0` + `set COMPOSE_DOCKER_CLI_BUILD=0` para forzar el builder clásico.

### Backend startup “Unknown constraint max_digits” (2026-04-25) ✅

- **Síntoma:** backend reiniciando con traceback en import de `portal_tecnico_emergencias/schemas.py`: `ValueError: Unknown constraint max_digits`.
- **Causa:** en este runtime (Pydantic v2 del contenedor), la metadata `max_digits`/`decimal_places` en `Field(...)` para `Decimal` no fue aceptada al construir el schema.
- **Ajuste en repo:** `ActualizarEstadoServicioIn.presupuesto_bob` mantiene `gt=0` y mueve el control de formato monetario (máx. 12 dígitos y 2 decimales) a `@model_validator`, evitando el crash de arranque.

## Cambios recientes (2026-04-23) — Validación completa módulo IA ✅

## Cambios recientes (2026-04-25) — Limpieza de textos UI ✅

- **Frontend Angular:** se removieron referencias internas de planificación en textos visibles (`Ciclo`, `fase`, `CUxx`) en módulos admin/taller para una UX más profesional.
- **Mobile Flutter:** se removieron etiquetas `CUxx` y `ciclo` en textos de pantallas cliente/técnico (wizard, seguimiento, detalle y selector de actor), más normalización de comentarios descriptivos.
- **Verificación:** búsqueda global sin coincidencias de `Ciclo\\d`/`CU\\d` en `frontend/src` y `mobile/lib`.

### Seguimiento móvil, ETA, chips IA, FCM (2026-04-25) ✅

- **Chips "Ubicación / Audio / Imagen":** se alinean a datos reales: detalle móvil cuenta `ubicaciones`/`evidencias`; seguimiento usa flags del API (`tiene_ubicacion_cliente`, etc.). **ETA:** formulario en **portal taller** al asignar técnico (`tiempo_estimado_min` opcional) rellena `solicitud.tiempo_estimado_min` que ya consume el seguimiento móvil.
- **Historial:** `SeguimientoTimeline` elimina `(CU##)` de observaciones heredadas.
- **FCM:** `FirebaseMessaging.onMessage` con app abierta → `SnackBar` (`FcmMessageListener`). Token + backend sin cambio; credenciales Firebase siguen solo en máquina local.
- **Docs:** `CURRENT_STATE` actualizado; sesión en `docs/ai/sessions/2026-04-25-mobile-seguimiento-eta-fcm.md`.

### Técnico móvil: hora BOT + tipo accidente + push routing (2026-04-25) ✅

- **Hora Bolivia (Santa Cruz):** util `mobile/lib/core/utils/bolivia_time.dart` (UTC-4) aplicada en `tecnico_servicio_card`, `tecnico_servicio_detalle_screen`, `tecnico_servicio_ubicacion_screen` y `chat_bubble`.
- **Servicios asignados técnico:** backend `portal_tecnico_emergencias` incluye `categoria_incidente` y `nivel_prioridad` desde `ai_payload`; mobile técnico lo presenta como chips “Tipo” y “Prioridad” en lista y bloque “Incidente” en detalle.
- **Push técnico/cliente:** `FcmMessageListener` añade manejo de tap (`onMessageOpenedApp` + `getInitialMessage`) con deep-link por `solicitud_id`; si `tipo=MENSAJE_NUEVO` abre chat, en otro caso abre detalle/seguimiento.
- **Validación:** `flutter analyze` (mobile) ✅ y `python -m py_compile` para schemas/repository técnico ✅.

### Hora Santa Cruz unificada en sistema (2026-04-25) ✅

- **Angular web:** `app.config.ts` fija `LOCALE_ID='es-BO'` + `DATE_PIPE_DEFAULT_OPTIONS.timezone='-0400'`; `main.ts` registra locale `es-BO`. Resultado: los templates con `| date` muestran BOT.
- **Mobile Flutter:** `BoliviaTime` se usa en timeline/ETA/ubicación técnico/notificaciones/comprobante/listado solicitudes (además de técnico ya implementado) y se elimina dependencia de `.toLocal()`.
- **Convención:** backend mantiene persistencia en UTC/servidor; la capa de presentación fuerza BOT para experiencia consistente.
- **Docker:** `docker-compose.yml` ahora inyecta `TZ=America/La_Paz` en `db/mailhog/backend/frontend/ai-inference` y `PGTZ=America/La_Paz` en `db`.
- **Chequeo:** `docker compose config` válido ✅.

### Push registro + pagos (2026-04-25) ✅

- **Cliente (registro/token):** en `comunicaciones.service.registrar_fcm_token`, si es el primer token del cliente se envía push/notificación de bienvenida.
- **Pago confirmado:** en `pagos.service` se dispara push/notificación cuando `estado -> PAGADO`:
  - flujo simulado/autocomplete (`_aplicar_resultado_pasarela`)
  - confirmación Stripe (`confirmar_pago_stripe`)
- **Stripe env vars:** backend usa `STRIPE_SECRET_KEY` para PaymentIntent/retrieve y expone `STRIPE_PUBLISHABLE_KEY` al mobile en `PagoIniciadoRead`.

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
- **Backend seeds:** defaults en `identidades_demo_sc.py` + `config.py` (p. ej. `carlos.vega@sc-demo.test` / `scdemo1`); `docker-compose.override.yml` activa `SEED_TECNICO_ON_START` en dev.
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

## Handoff puntual (2026-04-25) — UX de push móvil

- Problema reportado: “la notificación se ve como mensaje interno” (SnackBar en foreground).
- Solución aplicada: en `mobile/lib/core/push/fcm_message_listener.dart` se reemplaza el aviso visual por notificación del sistema vía `flutter_local_notifications`.
- Se mantiene deep-link: al tocar la notificación local, la app navega al chat/detalle según `tipo` y `solicitud_id`.
- Backend con mejor observabilidad FCM: `comunicacion_y_notificaciones/dispositivos_push/fcm_client.py` loguea `FCM multicast enviado: success/failure/tokens` y detalle de fallos.
- Verificación mínima completada:
  - `FCM_ENABLED=True` en runtime.
  - `POST /api/portal/cliente/dispositivos/fcm 204` en logs.
  - Inserciones en `notificaciones` para eventos (`TALLER_ASIGNADO`, `TECNICO_ASIGNADO`, etc.).
