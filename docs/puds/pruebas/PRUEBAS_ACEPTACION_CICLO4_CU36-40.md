# Pruebas de aceptación — Ciclo 4 (CU36–CU40)

> **Formato examen (tabla Caso de uso / Descripción / Precondiciones):**  
> **`FORMATO_EXAMEN_PRUEBAS_CU36-40.md`** ← copiar esto al Word Sp2.

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Sección PUDS:** 3.1.2.1.1 Ciclo #4  
**Técnica:** Caja negra (partición de equivalencia, valores límite, tablas de decisión, transición de estados)  
**Fuente implementación:** `docs/puds/casos-uso/CICLO4_DETALLE_CASOS_USO.md`, código en `backend/` y `mobile/` / `frontend/`  
**Plantilla académica:** `Prueba caso de uso y Historia de Usuario Sp2.docx`

---

## 1. Estado real vs matriz del examen

En tu tabla del Word los CU aparecen como **Pendiente**; en el **repositorio** el estado funcional es:

| CU | Nombre | Implementado | Dónde probarlo |
|----|--------|--------------|----------------|
| **CU36** | Consultar ubicación del técnico en tiempo real | **Sí** (REST + polling 12 s en móvil; no WebSocket) | App móvil **cliente** |
| **CU37** | Seleccionar taller para realizar el servicio | **Sí** | App móvil **cliente** + API taller bandeja |
| **CU38** | Procesar pago mediante pasarela | **Sí** (Stripe tarjeta si hay claves; resto simulado) | App móvil **cliente** |
| **CU39** | Actualizar estado de atención del servicio | **Sí** | App móvil **técnico** |
| **CU40** | Gestionar tenant o red de talleres | **Sí** | Panel web **admin** `/admin/panel/organizaciones` |

**Conclusión:** no debes *implementar* de cero; debes **ejecutar pruebas de aceptación**, capturar evidencias (capturas, respuestas API) y actualizar la columna **Estado** de tu matriz a **Implementado / Probado** cuando cada paso sea Satisfactorio.

---

## 2. Qué debes hacer (paso a paso)

### A) Preparar entorno

1. `docker compose up -d --build` (y seeds: `docker compose exec backend python -m app.seeds`).
2. Migraciones SaaS si la BD es antigua: `0015`, `0016`, `0017` (ver `docs/ai/NEXT_STEPS.md` 0b–0d).
3. **Mobile** `mobile/.env`: `API_BASE_URL` apuntando al host; `TENANT_SLUG_DEFAULT=demo-sc`.
4. Credenciales demo (Santa Cruz):
   - **Cliente:** `carlos.vega@sc-demo.test` / `scdemo1` — org `demo-sc`
   - **Técnico:** usuario seed técnico del taller demo (ver `identidades_demo_sc.py` o seeds)
   - **Admin plataforma:** `patricio.mendez@sc-demo.test` / `scdemo1` — login en `http://localhost/admin/login`

### B) Ejecutar flujo integrado (recomendado para adjuntos)

Orden sugerido para una sola emergencia de prueba:

1. Cliente: login → crear emergencia (CU11) + ubicación → **CU37** elegir taller  
2. Taller web: aceptar bandeja → asignar técnico (CU28)  
3. Técnico móvil: **CU39** EN_CAMINO → EN_ATENCION + presupuesto BOB → compartir GPS  
4. Cliente móvil: **CU36** ver mapa técnico (esperar ~12 s entre refrescos)  
5. Cliente móvil: **CU38** pago (tarjeta `4242…` si Stripe activo, o efectivo simulado)  
6. Admin web: **CU40** listar/crear/editar organización

### C) Documentar en el Word del examen

Por cada CU, copiar la sección **«Prueba de caso de uso CUxx»** de este archivo:

- Tabla **Paso | Acción | Resultado esperado | Estado**
- Marcar **Satisfactorio** o **Fallido** solo después de ejecutar
- **Adjunto:** capturas como en el ejemplo CU1 (lista + modal / pantalla móvil + Swagger opcional)
- Opcional: exportar respuesta JSON de `GET /docs` o Postman para un paso crítico

### D) Técnicas de caja negra (cómo defenderlas)

En cada CU, al final de este documento hay un anexo **PE / VL / TD / TE** que puedes citar en oral: «aplicamos partición de equivalencia en…», «probamos transición de estados…».

---

## 3. Prueba de caso de uso CU36: Consultar ubicación del técnico en tiempo real

**Caso de uso:** CU36 Consultar ubicación del técnico en tiempo real  

**Descripción:** Permite al cliente consultar en mapa la última posición GPS compartida por el técnico asignado a su solicitud de emergencia, con actualización periódica mientras permanece en la pantalla.

**Precondiciones:**

- a) Cliente con sesión iniciada (CU2) en app móvil, organización `demo-sc`.
- b) Solicitud con técnico asignado (flujo taller CU28).
- c) El técnico compartió al menos una ubicación (`PATCH .../ubicacion-tecnico` desde app técnico).
- d) Conexión activa con API y backend en ejecución.

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|------|--------|-------------------|--------------------------------|
| 1 | Cliente abre solicitud activa → **Seguimiento** → **Ver ubicación del técnico**. | Se abre pantalla de mapa (OSM) sin error de navegación. | |
| 2 | Observar carga inicial. | `GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico` devuelve 200 con `latitud`, `longitud`, `precision_metros` (si aplica) y timestamp. | |
| 3 | Esperar ~12 s sin salir de la pantalla. | La posición en mapa se actualiza automáticamente (polling) si el técnico envió nueva ubicación. | |
| 4 | Pulsar **Reintentar** / refresh manual. | Nueva consulta al API; mapa y datos se refrescan sin cerrar sesión. | |
| 5 | Caso negativo: abrir CU36 **sin** técnico asignado. | Mensaje informativo (no mapa con coordenadas válidas); no crash de la app. | |
| 6 | Caso negativo: técnico asignado pero **sin** GPS compartido aún. | Mensaje de error recuperable; opción reintentar. | |

**Responsable:** ____________________  

**Resultado de la prueba:** ____________________  

**Adjunto:** Captura pantalla mapa cliente; opcional respuesta JSON `ubicacion-tecnico`; captura técnico compartiendo ubicación.

---

## 4. Prueba de caso de uso CU37: Seleccionar taller para realizar el servicio

**Caso de uso:** CU37 Seleccionar taller para realizar el servicio  

**Descripción:** Tras registrar la emergencia, el cliente visualiza talleres candidatos rankeados y confirma uno; el sistema crea bandeja PENDIENTE solo para ese taller y pasa la solicitud a `EN_REVISION`.

**Precondiciones:**

- a) Cliente con sesión iniciada (CU2), tenant `demo-sc`.
- b) Solicitud creada (CU11) con al menos una ubicación registrada (CU12) — recomendado para ranking.
- c) Existen talleres activos en el tenant con coordenadas en BD.
- d) Backend y móvil operativos.

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|------|--------|-------------------|--------------------------------|
| 1 | Completar wizard de emergencia hasta el paso final. | Botón principal **Elegir taller** visible. | |
| 2 | Pulsar **Elegir taller**. | Pantalla lista candidatos (`emergencia_seleccion_taller_screen`). | |
| 3 | Verificar carga de candidatos. | `GET .../talleres-candidatos` → 200; lista con `taller_id`, nombre, score/distancia (según API). | |
| 4 | Seleccionar un taller y confirmar. | `POST .../seleccionar-taller` → 200; mensaje de éxito en app. | |
| 5 | Verificar estado solicitud (seguimiento o detalle). | Estado **EN_REVISION**; `taller_id` asignado al elegido. | |
| 6 | Ingresar al portal **taller** elegido → bandeja disponible. | La solicitud aparece **solo** en bandeja de ese taller (no en todos los talleres del tenant). | |
| 7 | Caso negativo: intentar candidatos **sin** ubicación en solicitud. | API 422 con mensaje indicando registrar ubicación primero. | |
| 8 | Caso negativo: `taller_id` inválido o de otro tenant en POST. | 404 o 422; no se crea bandeja incorrecta. | |

**Responsable:** ____________________  

**Resultado de la prueba:** ____________________  

**Adjunto:** Captura lista talleres móvil; captura bandeja taller web; JSON candidatos/seleccionar.

---

## 5. Prueba de caso de uso CU38: Procesar pago mediante pasarela

**Caso de uso:** CU38 Procesar pago mediante pasarela  

**Descripción:** El cliente paga el servicio de emergencia; con método **Tarjeta** y Stripe configurado usa Payment Sheet; con efectivo/transferencia/QR usa pasarela **SIMULADO**; el monto debe coincidir con `presupuesto_bob` si existe.

**Precondiciones:**

- a) Cliente con sesión iniciada (CU2).
- b) Solicitud con **presupuesto_bob** registrado por técnico (CU39 → EN_ATENCION).
- c) Backend en ejecución; para Stripe real: `STRIPE_SECRET_KEY` y `STRIPE_PUBLISHABLE_KEY` en `.env` y contenedor backend recreado.
- d) Un solo pago **PAGADO** por solicitud (regla de negocio).

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|------|--------|-------------------|--------------------------------|
| 1 | Cliente abre **Pago** desde seguimiento de la solicitud. | Pantalla muestra monto; si hay presupuesto, monto **bloqueado** al valor del técnico. | |
| 2 | Elegir método **Efectivo** (o transferencia/QR). | `POST .../pagos` → 201; estado **PENDIENTE** o flujo simulado; confirmación sin Stripe SDK. | |
| 3 | Confirmar pago simulado hasta **PAGADO**. | Estado PAGADO; comisión en `comisiones_taller`; notificación/push al cliente (si FCM configurado). | |
| 4 | (Opcional) Repetir con método **Tarjeta** y Stripe activo. | Respuesta incluye `stripe_client_secret`; Payment Sheet; `confirmar-stripe` → PAGADO. Tarjeta prueba `4242 4242 4242 4242`. | |
| 5 | Caso negativo: monto distinto al presupuesto. | 422 validación; no se confirma pago incorrecto. | |
| 6 | Caso negativo: segundo pago PAGADO misma solicitud. | Rechazado por índice único / regla un pago exitoso por solicitud. | |
| 7 | Verificar en BD o admin finanzas (opcional). | Fila en `pagos` y `comisiones_taller` coherentes con monto servicio. | |

**Responsable:** ____________________  

**Resultado de la prueba:** ____________________  

**Adjunto:** Capturas flujo pago móvil; comprobante PAGADO; opcional Stripe dashboard test mode.

---

## 6. Prueba de caso de uso CU39: Actualizar estado de atención del servicio

**Caso de uso:** CU39 Actualizar estado de atención del servicio  

**Descripción:** El técnico asignado avanza el servicio por estados operativos y registra presupuesto en BOB al iniciar atención en sitio.

**Precondiciones:**

- a) Técnico con sesión iniciada (CU2) en app móvil.
- b) Servicio asignado al técnico (CU28).
- c) Estados permitidos según máquina: `TECNICO_ASIGNADO` → `EN_CAMINO` → `EN_ATENCION` → `FINALIZADA`.
- d) API operativa.

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|------|--------|-------------------|--------------------------------|
| 1 | Técnico abre **Servicios asignados** y entra al detalle de la solicitud. | Detalle carga datos de solicitud y estado actual. | |
| 2 | Actualizar estado a **En camino** (`EN_CAMINO`). | `PATCH .../estado` → 200; cliente ve cambio en seguimiento/notificación. | |
| 3 | Actualizar a **En atención** (`EN_ATENCION`) **sin** presupuesto. | Error validación; no cambia estado (o mensaje exigiendo presupuesto). | |
| 4 | Actualizar a **En atención** con `presupuesto_bob` > 0 (ej. 150.00). | 200; `presupuesto_bob` y `presupuesto_registrado_at` persistidos; historial de estado registrado. | |
| 5 | Cliente consulta seguimiento/pago. | Presupuesto visible para CU38. | |
| 6 | Técnico comparte ubicación GPS (flujo técnico). | Coordenadas en solicitud; habilita CU36 para cliente. | |
| 7 | Actualizar a **Finalizada** desde EN_ATENCION. | 200; estado FINALIZADA; servicio cerrado operativamente. | |
| 8 | Caso negativo: saltar de TECNICO_ASIGNADO directo a FINALIZADA. | 422 transición no permitida. | |

**Responsable:** ____________________  

**Resultado de la prueba:** ____________________  

**Adjunto:** Capturas app técnico (estados + presupuesto); captura cliente con presupuesto; historial estado en API si aplica.

---

## 7. Prueba de caso de uso CU40: Gestionar tenant o red de talleres

**Caso de uso:** CU40 Gestionar tenant o red de talleres  

**Descripción:** El administrador de plataforma (superadmin) gestiona organizaciones SaaS: listar, crear y editar tenants; opcionalmente flujo Stripe SaaS; selector de organización filtra datos admin.

**Precondiciones:**

- a) Usuario **ADMIN** plataforma (`tenant_id` NULL) con sesión en panel web.
- b) Permisos `tenants:leer`, `tenants:crear`, `tenants:actualizar`.
- c) Login en `http://localhost/admin/login` (no quedarse en formulario tras login — recarga a `/admin/panel`).
- d) Backend y BD con tabla `tenants` (migración 0015+).

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|------|--------|-------------------|--------------------------------|
| 1 | Acceder a **Organizaciones** (`/admin/panel/organizaciones`). | Tabla/lista de tenants (incluye `demo-sc` seed). | |
| 2 | Crear tenant nuevo: slug único, nombre, plan. | `POST /api/admin/tenants` → 201; aparece en lista. | |
| 3 | Editar tenant (nombre o plan). | `PATCH /api/admin/tenants/{id}` → 200; cambios visibles al refrescar. | |
| 4 | Caso negativo: crear tenant con **slug duplicado**. | Error validación; no duplica fila. | |
| 5 | Usar selector **Organización** en barra superior (superadmin). | Listados usuarios/talleres/finanzas filtran por `tenant_id` seleccionado. | |
| 6 | (Opcional) Stripe SaaS: checkout suscripción tenant. | Redirección Stripe test; webhook actualiza `subscription_status` (si claves configuradas). | |
| 7 | Caso negativo: usuario admin **con** tenant (no superadmin) intenta gestión global tenants. | Acceso denegado o lista vacía según diseño RBAC. | |

**Responsable:** ____________________  

**Resultado de la prueba:** ____________________  

**Adjunto:** Capturas panel organizaciones; formulario crear/editar; selector organización en shell admin.

---

## 8. Anexo — Técnicas de caja negra por CU

### CU36 — Consultar ubicación técnico

| Técnica | Aplicación en este proyecto |
|---------|----------------------------|
| **Partición equivalencia** | **Válido:** técnico asignado + GPS compartido → 200 con coords. **Inválido:** sin técnico; sin GPS; solicitud ajena → 404/403/mensaje UI. |
| **Valores límite** | Coordenadas extremas válidas (-90/90 lat, -180/180 lng); `precision_metros` = 0 vs null; polling intervalo ~12 s (1 ciclo vs 3 ciclos). |
| **Tabla decisión** | Condiciones: ¿técnico_id? ¿tecnico_ult_ubicacion_at? → Salida: mapa / mensaje sin datos / error sesión. |
| **Transición estados** | No aplica al CU en sí; depende de flujo solicitud hasta `TECNICO_ASIGNADO` + acción técnico compartir GPS. |

### CU37 — Seleccionar taller

| Técnica | Aplicación |
|---------|------------|
| **Partición equivalencia** | Válido: ubicación + taller activo en tenant. Inválido: sin ubicación (422); taller inexistente; otro tenant. |
| **Valores límite** | Lista 0 candidatos vs 1 vs N talleres; confirmar mismo taller dos veces (idempotencia o error). |
| **Tabla decisión** | Ubicación × taller activo × tenant_id → crear bandeja única PENDIENTE + EN_REVISION. |
| **Transición estados** | `REGISTRADA` → (selección) → `EN_REVISION`; bandeja: ninguna → PENDIENTE solo taller elegido. |

### CU38 — Pago pasarela

| Técnica | Aplicación |
|---------|------------|
| **Partición equivalencia** | Métodos: TARJETA (Stripe vs simulado), EFECTIVO, TRANSFERENCIA, QR. Monto = presupuesto vs distinto. |
| **Valores límite** | `presupuesto_bob` = 0.01 vs muy grande; monto ε ±0.02 en mobile; un PAGADO por solicitud (segundo intento falla). |
| **Tabla decisión** | Stripe habilitado × método TARJETA → PaymentIntent; si no → SIMULADO. Presupuesto definido → monto bloqueado. |
| **Transición estados** | Pago: PENDIENTE → PAGADO / FALLIDO / ANULADO. |

### CU39 — Estado atención técnico

| Técnica | Aplicación |
|---------|------------|
| **Partición equivalencia** | Transiciones válidas vs inválidas; presupuesto presente/ausente al entrar EN_ATENCION. |
| **Valores límite** | `presupuesto_bob` mínimo positivo; decimales (2 lugares); solicitud ya FINALIZADA. |
| **Tabla decisión** | Estado actual × nuevo estado × presupuesto → permitir / 422. |
| **Transición estados** | `TECNICO_ASIGNADO` → `EN_CAMINO` → `EN_ATENCION` → `FINALIZADA` (diagrama obligatorio en defensa). |

### CU40 — Gestionar tenant

| Técnica | Aplicación |
|---------|------------|
| **Partición equivalencia** | Superadmin vs admin con tenant; slug único vs duplicado; plan FREE/STARTER/PRO. |
| **Valores límite** | Slug longitud máx; caracteres inválidos en slug; tenant sin talleres vs con red completa. |
| **Tabla decisión** | Rol × permiso tenants × subscription_status → CRUD permitido / solo lectura / bloqueo escritura. |
| **Transición estados** | Tenant: ACTIVO / SUSPENDIDO; suscripción: TRIAL → ACTIVA → PAST_DUE → CANCELADA. |

---

## 9. Matriz resumen para pegar en 3.1.2.1.1

Después de ejecutar pruebas, actualiza tu tabla del Word así:

| ID | Caso de uso | Estado (matriz) | Prioridad | Riesgo | Actor | Ciclo |
|----|-------------|-----------------|-----------|--------|-------|-------|
| CU36 | Consultar ubicación del técnico en tiempo real | **Implementado / Probado** | Alta | Alto | Cliente | C4 |
| CU37 | Seleccionar taller para realizar el servicio | **Implementado / Probado** | Alta | Alta | Cliente | C4 |
| CU38 | Procesar pago mediante pasarela | **Implementado / Probado** | Alta | Alta | Cliente | C4 |
| CU39 | Actualizar estado de atención del servicio | **Implementado / Probado** | Alta | Medio | Técnico | C4 |
| CU40 | Gestionar tenant o red de talleres | **Implementado / Probado** | Alta | Alta | Administrador | C4 |

*(Cambia «Probado» solo cuando todos los pasos críticos de la sección correspondiente estén Satisfactorios con adjunto.)*

---

## 10. Trazabilidad PUDS

```
Requisito Ciclo 4 (Word examen)
  → Caso de uso CU36–CU40 (este documento + CICLO4_DETALLE)
  → Prueba de aceptación (tablas paso a paso)
  → Implementación backend/mobile/frontend (código real)
  → Adjunto evidencia (capturas)
```

**Archivos relacionados:** `docs/puds/casos-uso/CICLO4_SEGUIMIENTO_TIEMPO_REAL.md`, `docs/ai/NEXT_STEPS.md` (sección validación Ciclo 4).
