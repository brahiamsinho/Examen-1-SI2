# Guía — Diagramas de análisis de clases (BCE) en Enterprise Architect

**Paquete:** `/Model/Clase`  
**Tipo de diagrama EA:** `Class` (análisis robustness / BCE)  
**Última actualización:** 2026-05-29

---

## Objetivo

Modelar **un solo caso de uso** con pocos artefactos, trazables al ER y al código, sin mezclar CUs vecinos ni pantallas de error genéricas.

---

## Plantilla mínima (obligatoria para nuevos CUs)

| Capa | Cantidad | Regla |
|------|----------|--------|
| **Actor** | 1 | Solo el actor iniciador del CU. |
| **Boundary** | 1–2 | **Máximo 2** vistas del CU (resumen + paso principal; fusionar confirmación con selección si aplica). |
| **Control** | 1–2 | 1 controlador del CU; +1 solo si hay servicio/API distinto (ej. `AssignmentRankService`, IA). |
| **Entity (Class)** | 2–4 | Solo tablas/entidades que el CU **lee o escribe**; atributos clave, no el modelo completo. |

### No incluir en el diagrama de análisis

- Vistas de **otros CUs** (wizard de CU11, login CU2, etc.) → van en su propio diagrama o en precondiciones del texto del CU.
- **V.Error** genérica → excepciones en la ficha del CU, no como boundary.
- Clase **Cliente** duplicada si el actor ya es Cliente y la relación es `solicitud.cliente_id` (evitar actor + entidad + dependencia redundante).
- Dependencias del controlador a **todas** las entidades del ER; solo **Dependency** hacia lo que el CU toca en runtime.

---

## Tipos de línea

| Línea | Uso |
|-------|-----|
| **Association** sólida | Actor/Vista → Control; Control → Control auxiliar. |
| **Dependency** punteada | Control → Entity que el CU **lee o escribe directamente** en ese paso. Servicio auxiliar → Entity que consulta. |
| **Association** entre clases + etiqueta | Relaciones **persistentes del ER** (`genera`, `registra_comision`, `atiende`, …) con multiplicidad. |

### Regla anti-redundancia (importante)

No dupliques **Dependency del control** y **Association entre entidades** para el mismo efecto.

| Situación | Qué dibujar |
|-----------|-------------|
| El control crea/actualiza `Pago` y luego la comisión es consecuencia del pago | `PagoController` → `Pago` (punteada) + `Pago` —`registra_comision`— `ComisionTaller` (sólida). **No** hace falta `PagoController` → `ComisionTaller`. |
| El control valida la solicitud **antes** de crear el pago | `PagoController` → `SolicitudEmergencia` (punteada) **sí** conviene (lectura de `presupuesto_bob`, estado). |
| Servicio externo (Stripe) solo toca el registro de pago | `StripePasarelaService` → `Pago` (punteada). La comisión la registra el flujo principal vía `Pago`. |

**Idea:** la punteada = “este artefacto de lógica toca esta tabla **en este CU**”. La sólida entre entidades = “así queda el modelo de datos”.

No duplicar: Control→Cliente + Cliente `solicita` Solicitud.

---

## Nombres recomendados

- Vista: `V.<NombrePantalla>` (ej. `V.SeleccionTaller`, `V.UbicacionTecnico`).
- Control: `<Dominio>Controller` o `<Accion>Controller` alineado al router/servicio.
- Servicio IA/API: `<Nombre>Service` (estereotipo `control`).
- Entidad: mismo nombre que tabla/ modelo (`SolicitudEmergencia`, `Taller`).

**Tipos EA (obligatorio para tablas como plantilla CU1):**

| Rol | Tipo en EA | Estereotipo | Cómo se ve |
|-----|------------|-------------|------------|
| Vista | **`Class`** | **`Vista`** | Rectángulo con `<<Vista>>` en el encabezado + operaciones `+` |
| Controlador | **`Class`** | **`Controlador`** | Rectángulo con `<<Controlador>>` en el encabezado + operaciones `+` |

**Nunca** uses estereotipos UML `boundary` / `control` en diagramas Class de EA: aunque el tipo sea `Class`, EA los pinta como **óvalos** (robustness). Por eso el usuario veía círculos.
| Entidad | **`Class`** | (ninguno) | Atributos `-` y operaciones `+` |

**No usar** tipo nativo `boundary` / `control` (óvalos/círculos). Esos quedaron como `_legacy_*` (IDs 129–130, 136–138, …).

**Encabezado de tabla:** el **nombre** del elemento = `NombreCU::UI_xxx` o `NombreCU::XxxController` (ej. `CU36 Consultar ubicacion::UI_UbicacionTecnico`).

**Elementos tabla nuevos (2026-05-30):** IDs **268–285** en paquete `/Model/Clase`.

---

## Layout sugerido (formato tabla — plantilla académica)

Réplica del estilo **CU1 Gestionar productos** (actor + cajas con operaciones):

```
[Actor] —— [UI boundary con +ops] —— [Controller con +ops] —— [Entity attrs + ops]
```

### Reglas visuales obligatorias

| Regla | Detalle |
|-------|---------|
| **Encabezado** | `<<Vista>>` o `<<Controlador>>` + nombre `NombreCU::UI_xxx` / `NombreCU::XxxController`. |
| **Vista (boundary)** | Rectángulo amplio (~200×115 px) con operaciones públicas `+ mostrar()`, `+ crear()`, etc. |
| **Control** | Rectángulo amplio con `+ index()`, `+ store()`, `+ update()` o métodos del CU real. |
| **Entidad (Class)** | Compartimento atributos `- campo: tipo` y operaciones `+ get()`, `+ create()`, … |
| **Fila horizontal** | Actor (x≈60) → UI (x≈180) → Control (x≈420) → Entidades (x≈680+). |
| **2ª vista / servicio** | Apilar debajo de la primera UI o encima del control (mismo x≈180–420). |

### Diagramas actualizados (2026-05-30)

IDs **23, 26, 27, 28, 29, 30** en `/Model/Clase` — operaciones y posiciones aplicadas vía MCP EA.

- Actor izquierda; control centro; entidades derecha en columna.
- Relaciones ER entre entidades en el bloque derecho, sin cruzar el actor.

---

## Ejemplo aplicado: CU36 Consultar ubicación técnico

**Diagrama oficial:** `class CU36 Consultar ubicacion tecnico` (ID **27**)

| Artefacto | ID |
|-----------|-----|
| Actor Cliente | 134 |
| CU36 Consultar ubicacion::UI_UbicacionTecnico | **270** |
| CU36 Consultar ubicacion::SeguimientoController | **271** |
| SolicitudEmergencia, Tecnico | 139, 141 |

**ER en diagrama:** `Tecnico` `asigna` `SolicitudEmergencia` (`0..1` .. `0..*`).

Diagrama **24** → `_obsoleto_CU36_analisis_v1`.

---

## Ejemplo aplicado: Seleccionar taller

**Diagrama oficial:** `class Seleccionar taller servicio` (ID **26**)

| Artefacto | ID elemento |
|-----------|-------------|
| Actor Cliente | 142 |
| V.SeleccionTaller | 153 |
| TallerSeleccionController | 147 |
| AssignmentRankService | 148 |
| SolicitudEmergencia, Taller, SolicitudTallerBandeja | 149, 150, 152 |

**Relaciones ER en diagrama:** `atiende`, `genera`, `recibe` (sin entidad Cliente duplicada).

Diagrama **25** quedó `_obsoleto_Seleccionar_taller_v1` (versión con 4 vistas).

---

## Ejemplo aplicado: Procesar pago pasarela (CU20)

**Diagrama oficial:** `class Procesar pago pasarela` (ID **28**)

| Artefacto | ID |
|-----------|-----|
| Actor Cliente | 134 |
| V.PagoResumen, V.PagoPasarela | 154, 155 |
| PagoController, StripePasarelaService | 156, 157 |
| SolicitudEmergencia, Pago, ComisionTaller | 139, 158, 159 |

**ER:** `genera` (Solicitud→Pago), `registra_comision` (Pago→Comision, `0..1`).

---

## Ejemplo aplicado: Actualizar estado atención (técnico)

**Diagrama oficial:** `class Actualizar estado atencion` (ID **29**)

| Artefacto | ID |
|-----------|-----|
| Actor Tecnico | 160 |
| V.ServicioAsignado, V.ActualizarEstado | 161, 162 |
| EstadoServicioController | 163 |
| SolicitudEmergencia, SolicitudHistorialEstado, Tecnico | 139, 164, 141 |

**ER:** `asigna`, `registra_historial`. Una sola punteada: control → SolicitudEmergencia.

---

## Ejemplo aplicado: Gestionar tenant (admin SaaS)

**Diagrama oficial:** `class Gestionar tenant` (ID **30**)

| Artefacto | ID |
|-----------|-----|
| Actor Administrador | 165 |
| V.ListaOrganizaciones, V.FormularioTenant | 166, 167 |
| TenantAdminController, StripeBillingService | 168, 169 |
| Tenant, Taller, Usuario | 170, 171, 172 |

**ER:** `agrupa` hacia Taller y Usuario. Punteadas solo a **Tenant**.

> Nota: módulo multi-tenant **pendiente de implementación** en el repo; el diagrama refleja el CU y el ER objetivo.

---

## Checklist antes de dar por cerrado

- [ ] ¿Como máximo **2** boundaries del CU?
- [ ] ¿Sin vistas de CUs previos?
- [ ] ¿Máximo 4 entidades?
- [ ] ¿Sin dependencia redundante a Cliente si ya hay actor Cliente?
- [ ] ¿Excepciones solo en documento del CU?
- [ ] ¿Nombres alineados a código/ER?

---

## Referencia

- Plantilla académica: `class Analisis` (ID 23) en el mismo paquete.
- Comunicación (mensajes): ver `docs/ai/sessions/` y patrón Association+Collaboration en `Model/Comunicacion`.
