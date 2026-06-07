# Sesión 2026-05-30 — EA CU36 comunicación lineal MVC (MCP)

## Diagrama creado
| Campo | Valor |
|-------|--------|
| Ruta | `Model → Comunicacion` |
| Nombre | **`comm CU36 lineal MVC flujo principal`** |
| diagramID | **40** |
| Elementos (paquete 24) | 93 Cliente, 124 V.Seguimiento, 123 SeguimientoController, 97 SolicitudEmergencia, 98 Tecnico |

## Topología (lineal, no estrella)
```
Cliente — V.Seguimiento — SeguimientoController — SolicitudEmergencia
                                                 \— Tecnico
SolicitudEmergencia — Tecnico (Association estructural)
```

**No** en el diagrama: V.UbicacionTecnico (125), V.Error (126), enlace Actor→Controlador.

## Association (533–537)
Ocultas en diagrama 40 para ver solo mensajes.

## Collaboration (538–545)
| ID | Mensaje |
|----|---------|
| 538 | 1.AbrirSeguimiento() |
| 539 | 1.1 VerUbicacionTecnico() |
| 540 | 1.6 Reintentar() |
| 541 | 1.2 ConsultarUbicacion() |
| 542 | 1.5 viewMapa() (Control → Vista) |
| 543 | 1.2b ValidarSolicitud() (self) |
| 544 | 1.3 getUbicacionTecnico() (Control → Solicitud) |
| 545 | 1.4 return() |

Sin 2.1 / 2.2 / 2.3.

## Ajuste manual obligatorio en EA
Separar etiquetas en enlace Cliente–V.Seguimiento (538, 539, 540) arrastrando arriba/abajo.

## Obsoletos
- Diagrama **39** (estrella + V.UbicacionTecnico separado)
- Diagrama **38** (réplica drawio con topología incorrecta)
