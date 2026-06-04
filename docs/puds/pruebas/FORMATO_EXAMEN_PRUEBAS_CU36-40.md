# EJEMPLO DE CASO DE PRUEBA — Formato examen Sp2

**(Pruebas de aceptación)**

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Sección:** 3.1.2.1.1 Ciclo #4  
**Técnica:** Caja negra  

> Copia cada bloque tal cual a tu Word. La columna derecha de la primera tabla es el contenido; la tabla de pasos va debajo.

---

# Prueba de caso de uso CU36: Consultar ubicación del técnico en tiempo real

| | |
|:---|:---|
| **Caso de uso 1** | CU36 Consultar ubicación del técnico en tiempo real |
| **Descripción** | Este caso de uso permite al **cliente** consultar en la aplicación móvil la última posición GPS compartida por el **técnico mecánico** asignado a su solicitud de emergencia vehicular. Se muestra un mapa con coordenadas, precisión y opción de abrir navegación externa; la pantalla actualiza la ubicación de forma periódica (cada 12 segundos) mientras el cliente permanece en la vista. |
| **Precondiciones** | a) El cliente debe tener sesión iniciada (CU2) en la app móvil, organización **demo-sc**.<br>b) Debe existir una solicitud de emergencia con técnico asignado (CU28 Asignar mecánico).<br>c) El técnico debe haber compartido al menos una ubicación desde su app (CU37 flujo técnico — compartir GPS).<br>d) Debe existir conexión activa con el backend (`GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico`). |

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|:---:|:---|:---|:---:|
| 1 | Iniciar sesión como cliente (`carlos.vega@sc-demo.test` / `scdemo1`) y abrir una solicitud activa con técnico asignado. | Se muestra el detalle o seguimiento de la solicitud sin error. | |
| 2 | Pulsar **Ver ubicación del técnico** (o equivalente en seguimiento). | Se abre la pantalla de mapa (`emergencia_ubicacion_tecnico_screen.dart`). | |
| 3 | Observar la carga inicial del mapa. | Se visualizan latitud, longitud y marcador del técnico; respuesta HTTP 200 del API. | |
| 4 | Permanecer en la pantalla al menos 12 segundos sin cerrarla. | El mapa se actualiza automáticamente (polling) si el técnico envió nueva posición. | |
| 5 | Pulsar el botón de **Reintentar** o actualizar manualmente. | Se vuelve a consultar el API y se refresca la ubicación sin cerrar sesión. | |
| 6 | (Negativo) Abrir la misma función en una solicitud **sin** técnico asignado. | Se muestra mensaje informativo; la app no falla. | |

| | |
|:---|:---|
| **Responsable** | |
| **Resultado de la prueba** | |
| **Adjunto (Interfaz, consultas, reportes, otros)** | Captura pantalla mapa en app cliente; captura técnico compartiendo ubicación; opcional JSON de `ubicacion-tecnico`. |

---

# Prueba de caso de uso CU37: Seleccionar taller para realizar el servicio

| | |
|:---|:---|
| **Caso de uso 1** | CU37 Seleccionar taller para realizar el servicio |
| **Descripción** | Este caso de uso permite al **cliente** elegir qué **taller mecánico** atenderá su emergencia. Tras reportar la solicitud (CU11) y registrar ubicación (CU12), el sistema muestra talleres candidatos ordenados por proximidad, carga y criterios de IA; al confirmar, la solicitud queda en estado **EN_REVISION** y solo el taller elegido recibe la solicitud en su bandeja de atención. |
| **Precondiciones** | a) El cliente debe tener sesión iniciada (CU2) en la app móvil, tenant **demo-sc**.<br>b) Debe existir una solicitud de emergencia creada (CU11).<br>c) La solicitud debe tener al menos una ubicación registrada (CU12) — requerido para listar candidatos.<br>d) Debe haber talleres activos en el tenant con datos en base de datos.<br>e) Backend y app móvil en ejecución. |

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|:---:|:---|:---|:---:|
| 1 | Crear una emergencia desde el wizard móvil (texto, vehículo, ubicación). | La solicitud se guarda correctamente (estado inicial REGISTRADA o equivalente). | |
| 2 | En el paso final del wizard, pulsar **Elegir taller**. | Se abre la pantalla de selección de talleres candidatos. | |
| 3 | Verificar que se cargue la lista de talleres. | `GET .../talleres-candidatos` responde 200 con uno o más talleres (nombre, score o distancia). | |
| 4 | Seleccionar un taller de la lista y confirmar. | `POST .../seleccionar-taller` responde 200; mensaje de éxito en la app. | |
| 5 | Consultar el estado de la solicitud en seguimiento. | Estado **EN_REVISION**; taller asignado al elegido. | |
| 6 | Iniciar sesión en el portal **web del taller elegido** y abrir bandeja de solicitudes disponibles. | La solicitud aparece **solo** en ese taller (no en todos los talleres del tenant). | |
| 7 | (Negativo) Intentar listar candidatos sin haber registrado ubicación. | El sistema responde error 422 indicando registrar ubicación primero. | |

| | |
|:---|:---|
| **Responsable** | |
| **Resultado de la prueba** | |
| **Adjunto (Interfaz, consultas, reportes, otros)** | Captura lista de talleres en móvil; captura bandeja del taller web; opcional respuestas API candidatos/seleccionar. |

---

# Prueba de caso de uso CU38: Procesar pago mediante pasarela

| | |
|:---|:---|
| **Caso de uso 1** | CU38 Procesar pago mediante pasarela |
| **Descripción** | Este caso de uso permite al **cliente** pagar el servicio de emergencia vehicular mediante una pasarela de pago. El monto se basa en el **presupuesto en BOB** registrado por el técnico (CU39). Si el cliente elige **tarjeta** y Stripe está configurado, se usa Payment Sheet; si elige efectivo, transferencia o QR, o no hay claves Stripe, el pago se procesa en modo **simulado**. Al confirmarse, el pago queda **PAGADO**, se registra la comisión del taller y el cliente recibe confirmación (y notificación si aplica). |
| **Precondiciones** | a) El cliente debe tener sesión iniciada (CU2).<br>b) La solicitud debe tener **presupuesto_bob** definido (técnico en estado EN_ATENCION — CU39).<br>c) El módulo de pagos y el backend deben estar habilitados.<br>d) Debe existir conexión activa con la base de datos.<br>e) Solo puede existir un pago **PAGADO** por solicitud. |

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|:---:|:---|:---|:---:|
| 1 | Como cliente, abrir **Pago** desde el seguimiento de la solicitud con presupuesto. | Se muestra el monto; si hay presupuesto, el campo monto aparece bloqueado a ese valor. | |
| 2 | Elegir método de pago **Efectivo** (o transferencia / QR). | Se inicia el pago (`POST .../pagos`); no se exige Stripe. | |
| 3 | Confirmar el pago en el flujo simulado hasta completar. | Estado del pago **PAGADO**; mensaje o pantalla de confirmación al cliente. | |
| 4 | (Opcional) Repetir con método **Tarjeta** y Stripe configurado en `.env`. | Se muestra Payment Sheet; tarjeta de prueba `4242 4242 4242 4242`; confirmación **PAGADO**. | |
| 5 | (Negativo) Intentar pagar un monto distinto al presupuesto. | El sistema rechaza la operación (validación 422). | |
| 6 | (Negativo) Intentar un segundo pago PAGADO para la misma solicitud. | El sistema no permite duplicar pago exitoso. | |

| | |
|:---|:---|
| **Responsable** | |
| **Resultado de la prueba** | |
| **Adjunto (Interfaz, consultas, reportes, otros)** | Capturas flujo pago en app móvil (método, confirmación, comprobante); opcional pantalla Stripe. |

---

# Prueba de caso de uso CU39: Actualizar estado de atención del servicio

| | |
|:---|:---|
| **Caso de uso 1** | CU39 Actualizar estado de atención del servicio |
| **Descripción** | Este caso de uso permite al **técnico mecánico** actualizar el estado operativo del servicio asignado desde la app móvil: **En camino**, **En atención** y **Finalizada**. Al pasar a **En atención** debe registrar el **presupuesto en bolivianos (BOB)**, que queda disponible para el pago del cliente (CU38). Cada cambio válido se persiste en base de datos y se registra en el historial de estados; el cliente puede recibir notificación. |
| **Precondiciones** | a) El técnico debe tener sesión iniciada (CU2) en la app móvil.<br>b) Debe tener un servicio asignado (CU28 / CU32 Visualizar servicios asignados).<br>c) Las transiciones de estado deben respetar la secuencia: TECNICO_ASIGNADO → EN_CAMINO → EN_ATENCION → FINALIZADA.<br>d) Debe existir conexión activa con el backend. |

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|:---:|:---|:---|:---:|
| 1 | Iniciar sesión como técnico y abrir un servicio asignado. | Se muestra el detalle del servicio con el estado actual. | |
| 2 | Actualizar el estado a **En camino** (EN_CAMINO). | El cambio se guarda; el cliente ve el nuevo estado en seguimiento. | |
| 3 | Intentar pasar a **En atención** (EN_ATENCION) **sin** ingresar presupuesto. | El sistema muestra error de validación y no permite el cambio. | |
| 4 | Actualizar a **En atención** ingresando presupuesto (ej. 150.00 BOB). | Estado EN_ATENCION guardado; presupuesto persistido; historial actualizado. | |
| 5 | Compartir ubicación GPS desde la app técnico (si aplica al flujo). | Coordenadas guardadas; el cliente puede usar CU36. | |
| 6 | Actualizar el estado a **Finalizada** (FINALIZADA). | Servicio cerrado operativamente; estado FINALIZADA en sistema. | |
| 7 | (Negativo) Intentar saltar de TECNICO_ASIGNADO directamente a FINALIZADA. | El sistema rechaza la transición (error 422). | |

| | |
|:---|:---|
| **Responsable** | |
| **Resultado de la prueba** | |
| **Adjunto (Interfaz, consultas, reportes, otros)** | Capturas app técnico (cambio de estado y presupuesto); captura cliente con presupuesto visible. |

---

# Prueba de caso de uso CU40: Gestionar tenant o red de talleres

| | |
|:---|:---|
| **Caso de uso 1** | CU40 Gestionar tenant o red de talleres |
| **Descripción** | Este caso de uso permite al **administrador de plataforma** gestionar las **organizaciones (tenants)** del modelo SaaS: consultar el listado, crear nuevas organizaciones (slug, nombre, plan), editar datos y operar el contexto multi-tenant. Las organizaciones agrupan usuarios, talleres, clientes y datos operativos con aislamiento por `tenant_id`. El administrador superadmin puede filtrar el panel (usuarios, talleres, finanzas) por organización seleccionada. |
| **Precondiciones** | a) El usuario debe tener sesión iniciada como **ADMIN** de plataforma (superadmin, sin tenant fijo).<br>b) Debe tener permisos de tenants (`tenants:leer`, `tenants:crear`, `tenants:actualizar`).<br>c) El módulo de administración web debe estar habilitado (`/admin/login` → `/admin/panel`).<br>d) Debe existir conexión activa con la base de datos (tabla `tenants`, migraciones 0015–0017). |

| Paso | Acción | Resultado esperado | Estado (Satisfactorio/Fallido) |
|:---:|:---|:---|:---:|
| 1 | Acceder a `http://localhost/admin/login` e iniciar sesión (`patricio.mendez@sc-demo.test` / `scdemo1`). | Tras login se muestra el panel admin con menú lateral (Resumen, Organizaciones, etc.). | |
| 2 | Abrir el módulo **Organizaciones** (`/admin/panel/organizaciones`). | Se muestra la lista de tenants (incluye organización demo **demo-sc**). | |
| 3 | Crear una nueva organización con slug único, nombre y plan. | Se guarda correctamente y aparece en la lista. | |
| 4 | Editar una organización existente (nombre o plan). | Los cambios se guardan y se reflejan al actualizar la vista. | |
| 5 | Usar el selector **Organización** en la barra superior del panel admin. | Los listados de usuarios, talleres o finanzas se filtran por la organización elegida. | |
| 6 | (Negativo) Intentar crear organización con **slug duplicado**. | El sistema muestra error de validación; no se duplica el registro. | |

| | |
|:---|:---|
| **Responsable** | |
| **Resultado de la prueba** | |
| **Adjunto (Interfaz, consultas, reportes, otros)** | Captura lista de organizaciones; captura formulario crear/editar; captura selector de organización en shell admin. |

---

## Dónde está el detalle técnico (caja negra)

Técnicas PE / VL / TD / TE y notas de implementación: `PRUEBAS_ACEPTACION_CICLO4_CU36-40.md` (mismo folder).

Casos de uso (descripción académica): `docs/puds/casos-uso/CICLO4_DETALLE_CASOS_USO.md`.
