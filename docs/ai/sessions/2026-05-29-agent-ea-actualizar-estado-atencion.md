# Sesión 2026-05-29 — Análisis: Actualizar estado atención (técnico)

## EA
- Paquete: `/Model/Clase` (27)
- Diagrama: **`class Actualizar estado atencion`** (ID **29**)

## Patrón BCE (máx. 2 vistas, sin deps redundantes)
| Artefacto | ID | Código |
|-----------|-----|--------|
| Actor Tecnico | 160 | — |
| V.ServicioAsignado | 161 | detalle servicio (CU32) |
| V.ActualizarEstado | 162 | `tecnico_servicio_actualizar_estado_screen.dart` |
| EstadoServicioController | 163 | `PATCH .../tecnico/emergencias/solicitudes/{id}/estado` |
| SolicitudEmergencia | 139 | `estado`, `presupuesto_bob` |
| SolicitudHistorialEstado | 164 | `solicitud_historial_estado` |
| Tecnico (entidad) | 141 | `asigna` solicitud |

## Dependencias
- Solo `EstadoServicioController` → `SolicitudEmergencia`
- Historial vía `registra_historial` (sin punteada duplicada al control)

## API / reglas
- Transiciones: EN_CAMINO → EN_ATENCION → FINALIZADA
- EN_ATENCION exige `presupuesto_bob`
- Notificación cliente en servicio (no modelada como entidad)

## Excepciones (ficha CU)
- Transición inválida, sin presupuesto, solicitud cerrada 409
