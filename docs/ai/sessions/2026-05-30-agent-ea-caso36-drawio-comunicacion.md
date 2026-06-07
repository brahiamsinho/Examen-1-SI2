# Sesión 2026-05-30 — EA `comm caso36-drawio` (réplica Draw.io)

## Diagrama EA
- **Ruta:** `/Model/Comunicacion`
- **Nombre:** `comm caso36-drawio Consultar ubicacion tecnico`
- **diagramID:** **38**
- **Tipo:** Communication

## Fuente Draw.io
- `docs/diagrams/CU36-comunicacion-ubicacion-tecnico.drawio`
- Layout compacto: actor x=210, boundary x=370, control x=545, entidades x=773

## Elementos (reutilizados del modelo CU36)
| Rol | Nombre | ID |
|-----|--------|-----|
| Actor | Cliente | 93 |
| Boundary | V.Seguimiento | 124 |
| Boundary | V.UbicacionTecnico | 125 |
| Control | SeguimientoController | 123 |
| Entity | SolicitudEmergencia | 97 |
| Entity | Tecnico | 98 |

## Mensajes (igual Draw.io)
`1.AbrirSeguimiento`, `1.1 VerUbicacionTecnico`, `1.2 ConsultarUbicacion`, `1.2b ValidarSolicitud`, `1.3 getUbicacionTecnico`, `1.4 return`, `1.5 viewMapa`, `1.6 Reintentar`

## Otros diagramas CU36 comunicación
- ID **22** — wizard expandido (`CU36_Comunicacion_Recuperado`)
- Draw.io — archivo en `docs/diagrams/`
