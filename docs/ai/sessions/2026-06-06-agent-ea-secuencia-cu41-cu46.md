# Sesión 2026-06-06 — Diagramas de secuencia CU41–CU46 en EA

## Objetivo
Modelar en Enterprise Architect (`/Model/Secuencia`) los flujos reales de CU41–CU46 según backend + frontend/mobile del repo.

## Paquetes (hijos de Secuencia, packageID 4)

### Diagramas oficiales patrón CU_Gestionar_Tenant (referencia diagramID **12**)

Misma estructura que `Gestionar tenant (Clon Exacto Ref)`: Actor → **V.Index / V.Crear / V.Modificar** → *Controller → **M.*** (+ API.* si aplica). Lifelines con tipos EA boundary/control/entity.

| CU | Paquete EA | diagramID | Diagrama | ElementIDs (Actor, V.*, Controller, M.*) |
|----|------------|-----------|----------|------------------------------------------|
| CU41 | `CU_Recibir_Notificaciones` (39) | **67** | Recibir notificaciones inmediatas | 425 Cliente, 426–428 V.*, 429 NotificacionesController, 430 M.Notificacion, 431 API.FCM |
| CU42 | `CU_Registrar_Cotizacion` (36) | **68** | Registrar cotizacion del servicio | 432 Taller, 433–435 V.*, 436 PresupuestoController, 437 M.SolicitudEmergencia |
| CU43 | `CU_Sync_Al_Reconectar` (37) | **69** | Sync al reconectar | 438 Cliente, 439–441 V.*, 442 EmergenciasController, 443 M.SolicitudDraft, 444 M.SolicitudEmergencia |
| CU44 | `CU_Consultar_ETA_Reparacion` (38) | **70** | Consultar ETA reparacion | 445 Cliente, 446–448 V.*, 449 EtaController, 450 M.SolicitudEmergencia, 451 M.EtaCache |
| CU45 | `CU45_Registrar_Offline` (41) | **71** | Registrar emergencia offline | 459 Cliente, 460–462 V.*, 463 DraftController, 464 M.SolicitudDraft |
| CU46 | `CU_Visualizar_Dashboard_KPIs` (40) | **72** | Visualizar dashboard KPIs | 452 Administrador, 465 Taller, 453–455 V.*, 456 KpisController, 457 M.SolicitudEmergencia, 458 M.ComisionTaller |

Referencia visual primaria: **packageID 21** diagramID **12** `Gestionar tenant (Clon Exacto Ref)`.  
Layout lifelines: x ≈ 50, 150, 250, 350, 480, 650, 780; height 780.

### Diagramas borrador estilo CU38 (`sd ...`) — obsoletos

IDs **61–66** (lifelines BCE sd). IDs **55–60** (Class/Component sin notación BCE). Pueden eliminarse en EA si solo se usa el patrón Tenant.

### Diagramas borrador (obsoletos — pueden eliminarse en EA)

IDs 55–60 (lifelines Class/Component sin notación BCE).

## Convención BCE (igual CU38)

| Rol | Tipo EA | Ejemplos |
|-----|---------|----------|
| Actor | Actor | Cliente, Taller, Administrador |
| Vista | **boundary** | V.Notificaciones, V.Pago, V.ReportesKPIs |
| Controlador | **control** | NotificacionesController, PresupuestoController |
| Entidad DER | **entity** | SolicitudEmergencia, Notificacion, BD |
| API externa | **boundary** | API.FCM, API.Stripe |

Mensajes numerados: `1. metodo`, `2. metodo`, … + `return` punteado + `[alt: …]`.

## Trazabilidad código → lifelines

- **CU41:** `eventos_servicio.py`, `notificaciones/service.py`, FCM, mobile `notificaciones_centro_screen.dart`, taller web polling.
- **CU42:** `presupuesto.py`, `taller-emergencias-incidente-detalle.component`.
- **CU43:** `sync_orquestador.dart`, `crear_solicitud` + `client_request_id`.
- **CU44:** `seguimiento_eta.py`, `consultar_eta_providers.dart`, `eta_cache_repo.dart`.
- **CU45:** `emergencia_wizard_screen.dart`, `solicitud_draft_repo.dart` (Hive).
- **CU46:** `kpis.py`, `admin-kpis.component`, `taller-kpis.component`.

## Notas UML
- Estilo alineado a CU36–CU40: Actor → boundary → control → entity.
- Fragmentos `[alt ...]` en nombres de mensaje (EA MCP no crea CombinedFragment automático).
- Abrir diagrama en EA antes de editar mensajes vía MCP (requerimiento del conector).

## Mensajes modelados (resumen por CU)

- **CU41 (67):** listar notificaciones, push FCM async, marcar leída.
- **CU42 (68):** registrar cotización → update presupuesto; alt error validación.
- **CU43 (69):** sync al reconectar → find drafts → crear idempotente → delete draft.
- **CU44 (70):** consultar ETA; alt cache hit M.EtaCache; alt error.
- **CU45 (71):** wizard offline → save draft local → badge pendientes.
- **CU46 (72):** filtros admin/taller → aggregate KPIs + comisiones; alt 403.

## Pendiente manual en EA (opcional)
- Separar etiquetas de mensajes superpuestos (arrastrar perpendicular a la lifeline).
- Añadir CombinedFragment `alt`/`opt` visuales si el curso lo exige (hoy `[alt: …]` va en nombre del mensaje).
- Enlazar cada diagrama al UseCase CU41–CU46 en paquete de casos de uso.
- Eliminar diagramas obsoletos 55–66 si ya no se necesitan.
