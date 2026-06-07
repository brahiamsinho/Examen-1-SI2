# Sesión 2026-05-30 — CU36 diagrama comunicación (patrón wizard EA)

## Ubicación
- Paquete: `/Model/Comunicacion/CU36_Comunicacion_Recuperado` (packageID **24**)
- Diagrama oficial: **`sd CU36 Consultar ubicacion tecnico`** (diagramID **22**, tipo **Communication**)
- Plantilla wizard: `/Model/Comunicacion/Communication Diagrams with Business Objects`

## Artefactos en el diagrama
| Rol | Elemento | ID |
|-----|----------|-----|
| Actor | Cliente | 93 |
| Boundary | V.Seguimiento | 124 |
| Boundary | V.UbicacionTecnico | 125 |
| Control | SeguimientoController | 123 |
| Entity | SolicitudEmergencia | 97 |
| Entity | Tecnico | 98 |

`V.Error` (126) oculto fuera del lienzo.

## Patrón wizard
1. **Association** (líneas estructurales entre lifelines)
2. **Collaboration** (mensajes numerados con flecha)

## Mensajes CU36 (flujo principal)
| Msg | De → A |
|-----|--------|
| 1.AbrirSeguimiento() | Cliente → V.Seguimiento |
| 1.1 VerUbicacionTecnico() | Cliente → V.Seguimiento |
| 1.6 Reintentar() | Cliente → V.Seguimiento |
| 1.2 ConsultarUbicacion() | V.Seguimiento → SeguimientoController |
| 1.2b ValidarSolicitud() | SeguimientoController (self) |
| 1.3 getUbicacionTecnico() | SeguimientoController → SolicitudEmergencia |
| 1.4 return() | SolicitudEmergencia → SeguimientoController |
| 1.5 viewMaps() | SeguimientoController → V.UbicacionTecnico |

## API
`GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico`

## Draw.io paralelo
`docs/diagrams/CU36-comunicacion-ubicacion-tecnico.drawio`
