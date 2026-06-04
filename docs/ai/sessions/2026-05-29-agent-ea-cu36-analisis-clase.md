# Sesión 2026-05-29 — Análisis de clases CU36 en EA

## Ubicación
- Paquete: **`/Model/Clase`** (packageID **27**)
- Diagrama: **`class CU36 Consultar ubicacion tecnico`** (diagramID **27**) — simplificado
- Obsoleto: ID **24** (`_obsoleto_CU36_analisis_v1`)

## Simplificación (2026-05-29)
- Vistas: solo **V.UbicacionTecnico** (mapa + reintentar; acceso desde seguimiento en ficha CU).
- Sin V.Seguimiento, V.Error, entidad Cliente duplicada.
- Entidades: **SolicitudEmergencia** (lee `tecnico_ult_*`) + **Tecnico** (`asigna`).
- Patrón: `docs/ai/EA_ANALYSIS_CLASS_GUIDE.md`

## Trazabilidad CU36
| Paso CU | Artefacto análisis | Implementación |
|---------|-------------------|----------------|
| 3–4 | V.Seguimiento | `emergencia_seguimiento_screen.dart` |
| 5–7 | V.UbicacionTecnico | `emergencia_ubicacion_tecnico_screen.dart` |
| 5 | SeguimientoController | `GET .../emergencias/{id}/ubicacion-tecnico` |
| 6 | SolicitudEmergencia + Cliente | `obtener_ubicacion_tecnico_compartida_cliente` |
| Excepciones | V.Error | HTTP 404 / red / sesión |
| CU37 (precondición) | `tecnico_ult_*` en SolicitudEmergencia | `compartir_ubicacion_tecnico` (técnico) |

## Elementos (IDs)
- 134 Actor Cliente
- 135–137 Boundaries V.Seguimiento, V.UbicacionTecnico, V.Error
- 138 Control SeguimientoController
- 139–141 Class SolicitudEmergencia, Cliente, Tecnico

## Relaciones ER replicadas
- Cliente `solicita` SolicitudEmergencia (1 .. 0..*)
- Tecnico `asigna` SolicitudEmergencia (0..1 .. 0..*)

## Nota diseño
No hay entidad `UbicacionHistorico` separada: la última GPS vive en columnas `tecnico_ult_*` de `solicitudes_emergencia` (migración 0013).
