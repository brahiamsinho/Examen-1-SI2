# Ciclo 4 — Detalle de casos de uso (formato académico)

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares (SaaS multi-tenant)  
**Diagramas PlantUML:** `docs/diagrams/uml/usecases/ciclo4/CUxx-*.puml`  
**Diagramas EA:** paquete `Ciclo 4 - Seguimiento tiempo real` (ver README del folder)  
**Actualizado:** 2026-05-28 — matriz oficial CU36–CU40 (sincronizado con código)

| ID | Caso de uso | Actor | Prioridad | Riesgo |
|----|-------------|-------|-----------|--------|
| CU36 | Consultar ubicación del técnico en tiempo real | Cliente | Alta | Alto |
| CU37 | Seleccionar taller para realizar el servicio | Cliente | Alta | Alta |
| CU38 | Procesar pago mediante pasarela | Cliente | Alta | Alta |
| CU39 | Actualizar estado de atención del servicio | Técnico/Mecánico | Alta | Medio |
| CU40 | Gestionar tenant o red de talleres | Administrador | Alta | Alta |

---

## CU36 — Consultar ubicación del técnico en tiempo real

**Diagrama:** `CU36-consultar-ubicacion-tecnico.puml`

| Campo | Detalle |
|-------|---------|
| **Caso de uso** | CU36 Consultar ubicación del técnico en tiempo real |
| **Propósito** | Permitir al cliente conocer la posición geográfica del técnico asignado durante la atención. |
| **Descripción** | Desde la app móvil, el cliente abre el seguimiento de su solicitud y consulta en mapa la última ubicación compartida por el técnico, con coordenadas, precisión y enlace a navegación externa. |
| **Actores** | Cliente |
| **Actor iniciador** | Cliente |
| **Precondición** | CU2 Iniciar sesión (cliente). CU11 Reportar emergencia. CU28 Asignar mecánico. El técnico debe haber compartido al menos una posición GPS (flujo técnico móvil). |
| **Proceso** | 1. Cliente inicia sesión en la app móvil.<br>2. Selecciona una solicitud activa y abre **Seguimiento**.<br>3. Pulsa **Ver ubicación del técnico**.<br>4. App consulta `GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico`.<br>5. Backend valida propiedad y devuelve última posición (`tecnico_ult_*`).<br>6. App muestra mapa OSM, coordenadas y **Abrir en mapas**.<br>7. Pantalla refresca automáticamente cada **12 s** (polling) y con botón manual **Reintentar**. |
| **Post-condición** | Cliente visualiza la última ubicación conocida del técnico (actualizada periódicamente mientras permanece en la pantalla). |
| **Excepciones** | 1. Sin técnico asignado → mensaje informativo.<br>2. Técnico sin ubicación compartida → error recuperable.<br>3. Sesión expirada → CU2.<br>4. Sin red → error de conexión. |
| **Implementación** | `mobile/lib/cliente/emergencias/presentation/screens/emergencia_ubicacion_tecnico_screen.dart`, `backend/app/modules/incidentes/emergencias/router.py` |
| **Pendiente opcional** | WebSocket o SSE para “tiempo real” estricto sin polling. |

---

## CU37 — Seleccionar taller para realizar el servicio

**Diagrama:** `CU37-seleccionar-taller-servicio.puml`

| Campo | Detalle |
|-------|---------|
| **Caso de uso** | CU37 Seleccionar taller para realizar el servicio |
| **Propósito** | Permitir al cliente elegir qué taller atenderá su emergencia entre opciones disponibles. |
| **Descripción** | Tras reportar la emergencia, el cliente visualiza talleres candidatos (rankeados por proximidad, especialidad, carga) y confirma su preferencia; el sistema envía la solicitud a la bandeja del taller elegido. |
| **Actores** | Cliente |
| **Actor iniciador** | Cliente |
| **Precondición** | CU2 Iniciar sesión (cliente). CU11 Reportar emergencia vehicular. CU12 Enviar ubicación (recomendado para ranking). |
| **Proceso** | 1. Cliente completa el reporte (CU11) con ubicación (recomendado para ranking).<br>2. Wizard móvil ofrece **Elegir taller** → `emergencia_seleccion_taller_screen.dart`.<br>3. App llama `GET /api/app/cliente/emergencias/{id}/talleres-candidatos` (ranking IA filtrado por `tenant_id`).<br>4. Cliente elige un taller y confirma.<br>5. App envía `POST /api/app/cliente/emergencias/{id}/seleccionar-taller` con `taller_id`.<br>6. Backend asocia la solicitud al taller, estado → `EN_REVISION`, crea **una** fila bandeja PENDIENTE solo para ese taller (expira pendientes de otros).<br>7. Taller ve la solicitud en bandeja (CU26 aceptación). |
| **Post-condición** | Solicitud vinculada al taller elegido; bandeja PENDIENTE única para ese taller. |
| **Excepciones** | 1. Ningún taller candidato → mensaje al cliente.<br>2. Taller desactivado antes de confirmar → volver a listar candidatos.<br>3. Cliente cancela → solicitud sin taller en bandeja hasta nueva selección. |
| **Implementación** | `service/seleccion_taller.py`, `emergencias/router.py` (endpoints candidatos + seleccionar); `crear_solicitud` **no** inserta bandeja en todos los talleres (seeds demo usan `insert_bandeja_pendiente_por_cada_taller` explícito). |
| **Probar** | Cliente `carlos.vega@sc-demo.test` / `scdemo1`, org `demo-sc`; crear emergencia → Elegir taller → confirmar. |

---

## CU38 — Procesar pago mediante pasarela

**Diagrama:** `CU38-procesar-pago-pasarela.puml`

| Campo | Detalle |
|-------|---------|
| **Caso de uso** | CU38 Procesar pago mediante pasarela |
| **Propósito** | Cobrar al cliente el servicio de emergencia usando una pasarela de pago segura (Stripe u otros métodos). |
| **Descripción** | El cliente elige método de pago, inicia el cobro en backend y confirma el resultado (tarjeta vía Stripe Payment Sheet, o métodos simulados efectivo/transferencia/QR según configuración). |
| **Actores** | Cliente |
| **Actor iniciador** | Cliente |
| **Precondición** | CU2 Iniciar sesión (cliente). Solicitud con servicio atendible. Presupuesto registrado (`presupuesto_bob`) si aplica regla de negocio. CU20 Realizar pago del servicio (Ciclo 2, base funcional). |
| **Proceso** | 1. Cliente abre **Pago** desde seguimiento o detalle de solicitud.<br>2. App muestra monto (bloqueado si hay presupuesto técnico).<br>3. Cliente elige método (`pago_metodo_screen`).<br>4. App envía `POST /api/app/cliente/.../pagos` (iniciar pago).<br>5. Si método **TARJETA**, backend crea PaymentIntent Stripe y devuelve `client_secret`.<br>6. App presenta Stripe Payment Sheet (`flutter_stripe`) y confirma.<br>7. App llama confirmación backend (`confirmarStripe` / completar simulado).<br>8. Backend marca pago PAGADO, registra comisión taller y notifica al cliente. |
| **Post-condición** | Pago en estado PAGADO (o PENDIENTE/FALLIDO según resultado); comisión registrada; cliente ve comprobante. |
| **Excepciones** | 1. Monto ≠ presupuesto → 422 validación.<br>2. Stripe no configurado en Docker (`STRIPE_SECRET_KEY` vacía) → método **TARJETA** cae en pasarela **SIMULADO** (`PENDIENTE`); efectivo/transferencia/QR siempre simulados.<br>3. Pago cancelado en pasarela → estado FALLIDO/ANULADO.<br>4. Duplicar POST pago → reutilizar intent coherente (mobile `draft.pagoIniciado`). |
| **Implementación** | `mobile/lib/cliente/pagos/`, `backend/app/modules/pagos_y_comisiones/pagos/`, `stripe_client.py`; variables raíz `.env` → `docker-compose.yml` (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`). Clave publicable también la devuelve el API en `POST /pagos` (no hace falta en `mobile/.env`). |
| **Verificar Stripe** | `docker compose exec backend python -c "from app.core.config import settings; print(settings.stripe_enabled)"` → debe ser `True`; tarjeta prueba `4242 4242 4242 4242`. |

---

## CU39 — Actualizar estado de atención del servicio

**Diagrama:** `CU39-actualizar-estado-atencion.puml`

| Campo | Detalle |
|-------|---------|
| **Caso de uso** | CU39 Actualizar estado de atención del servicio |
| **Propósito** | Permitir al técnico avanzar el servicio en sitio y registrar presupuesto al iniciar atención. |
| **Descripción** | El técnico cambia estados operativos (en camino, en atención, finalizado) desde la app móvil; al pasar a **En atención** registra presupuesto en BOB. |
| **Actores** | Técnico / Mecánico |
| **Actor iniciador** | Técnico / Mecánico |
| **Precondición** | CU2 Iniciar sesión (técnico). CU32 Visualizar servicios asignados. Técnico asignado a la solicitud. |
| **Proceso** | 1. Técnico abre servicio asignado.<br>2. Selecciona **Actualizar estado**.<br>3. Elige estado permitido (EN_CAMINO → EN_ATENCION → FINALIZADA).<br>4. Si EN_ATENCION, ingresa **presupuesto BOB**.<br>5. `PATCH /api/app/tecnico/emergencias/solicitudes/{id}/estado`.<br>6. Backend valida, persiste historial y notifica cliente.<br>7. App confirma y vuelve al detalle. |
| **Post-condición** | Nuevo estado e historial persistidos; presupuesto disponible para CU38. |
| **Excepciones** | 1. Transición inválida → error validación.<br>2. EN_ATENCION sin presupuesto → bloqueo.<br>3. Solicitud cerrada → 409. |
| **Implementación** | `tecnico_servicio_actualizar_estado_screen.dart`, `tecnico/router.py` |

---

## CU40 — Gestionar tenant o red de talleres

**Diagrama:** `CU40-gestionar-tenant-red-talleres.puml`

| Campo | Detalle |
|-------|---------|
| **Caso de uso** | CU40 Gestionar tenant o red de talleres |
| **Propósito** | Administrar organizaciones (tenants) de la plataforma SaaS: alta, edición, plan, suscripción y aislamiento de datos por organización. |
| **Descripción** | El administrador de plataforma crea y mantiene tenants (slug, nombre, plan), gestiona suscripción Stripe SaaS, y opera el contexto multi-tenant que agrupa talleres y usuarios por organización. |
| **Actores** | Administrador |
| **Actor iniciador** | Administrador |
| **Precondición** | CU2 Iniciar sesión con rol **ADMIN** plataforma (`tenant_id` NULL = superadmin). Permisos de gestión de tenants. |
| **Proceso** | 1. Admin ingresa al panel web `/admin/panel/organizaciones`.<br>2. Lista tenants (`GET /api/admin/tenants`).<br>3. **Crear:** formulario slug, nombre, plan → `POST /api/admin/tenants`.<br>4. **Editar:** actualizar nombre, plan, estado suscripción → `PATCH /api/admin/tenants/{id}`.<br>5. (Opcional) Vincular cliente Stripe SaaS / checkout suscripción (`billing/`).<br>6. Selector de organización en shell admin filtra usuarios, talleres y finanzas por `tenant_id`.<br>7. Sistema aplica RLS y JWT `tenant_id` en operaciones posteriores. |
| **Post-condición** | Tenant persistido; red de talleres/usuarios operable bajo aislamiento del tenant. |
| **Excepciones** | 1. Slug duplicado → error validación.<br>2. Suscripción vencida → escritura bloqueada (`require_writable_tenant_subscription`).<br>3. Admin sin superadmin → no accede a gestión global de tenants. |
| **Implementación** | `admin-organizaciones.component.ts`, `tenants/router.py`, migraciones `0015`–`0017`, `TenantSlugMiddleware` |

---

## Diagramas obsoletos (versión anterior Ciclo 4)

Los archivos `CU41`–`CU44` y diagramas EA **18–21** corresponden a la matriz anterior y quedan **archivados**; no forman parte del Ciclo 4 actual.
