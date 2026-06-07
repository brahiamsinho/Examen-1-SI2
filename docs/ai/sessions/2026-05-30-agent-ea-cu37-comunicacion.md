# Sesión 2026-05-30 — EA comunicación CU37 Seleccionar taller

## Ubicación EA
| Artefacto | ID |
|-----------|-----|
| Paquete | `Model → Comunicacion → CU37_Seleccionar_Taller_Com` (**30**) |
| Diagrama | `comm CU37 Seleccionar taller servicio` (**43**) |

## Elementos (paquete 30)
| elementID | Tipo | Nombre |
|-----------|------|--------|
| 295 | Actor | Cliente |
| 296 | boundary | V.SeleccionTaller |
| 297 | control | TallerSeleccionController |
| 298 | entity | Taller |
| 299 | entity | SolicitudTallerBandeja |

## Conectores nombrados (598–612)
Ver guía manual en respuesta al usuario / `seleccionar-taller-comunicacion.drawio`.

## Draw.io
`docs/diagrams/seleccionar-taller-comunicacion.drawio`

## Trazabilidad
- `POST /api/ai/assignment/rank`
- Confirmar taller + `SolicitudTallerBandeja` PENDIENTE
- CU26 aceptación taller
