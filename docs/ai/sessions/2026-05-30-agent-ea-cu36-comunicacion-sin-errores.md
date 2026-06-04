# Sesión 2026-05-30 — EA comunicación CU36 sin flechas de error

## Pedido
Réplica del Draw.io `CU36-comunicacion-ubicacion-tecnico.drawio` en **Enterprise Architect**, paquete **Comunicacion**, **sin** flechas/mensajes de error.

## Resultado
| Artefacto | Valor |
|-----------|--------|
| Paquete | `/Model/Comunicacion` (packageID **5**) |
| Diagrama | **`comm caso36-drawio flujo principal`** (diagramID **39**) |
| Tipo | Communication |

## Elementos en el lienzo
- Cliente (93), V.Seguimiento (124), V.UbicacionTecnico (125), SeguimientoController (123), SolicitudEmergencia (97), Tecnico (98)
- **No** aparece V.Error (126)

## Mensajes (Collaboration)
| ID | Nombre |
|----|--------|
| 526 | 1.AbrirSeguimiento() |
| 527 | 1.1 VerUbicacionTecnico() |
| 528 | 1.2 ConsultarUbicacion() |
| 529 | 1.2b ValidarSolicitud() (self) |
| 530 | 1.3 getUbicacionTecnico() |
| 531 | 1.4 return() |
| 532 | 1.5 viewMapa() |

**Excluidos:** 1.6 Reintentar, 2.1 SinTecnicoAsignado, 2.2 SinUbicacionCompartida, 2.3 ErrorRedOSesion.

## Association (ocultas en diagrama 39)
520–525: estructura Cliente–V.Seguimiento–Controller–entidades.

## Ajuste manual en EA
Varios mensajes comparten el mismo enlace (Cliente → V.Seguimiento). Separar etiquetas arrastrándolas en perpendicular a la línea (ver `EA_COMMUNICATION_DIAGRAM_GUIDE.md` §5).

## Draw.io
El archivo `docs/diagrams/CU36-comunicacion-ubicacion-tecnico.drawio` aún incluye excepciones en rojo; para paridad visual con EA 39, quitar celdas `lbl-v-err`, `txt-e2*`, `arrow-e2*`.
