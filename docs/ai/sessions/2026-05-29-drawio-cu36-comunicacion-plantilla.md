# Sesión 2026-05-29 — Draw.io CU36 comunicación (plantilla BCE)

## Plantilla de referencia

Modelo del usuario: actores `umlActor`, boundaries `umlBoundary`, control `umlControl`, entidades `umlEntity`, enlaces `line` horizontales, mensajes en celdas `text` 10px, flechas `endArrow=block` (actor) y `endArrow=classic` (mensajes).

## Archivo generado

- **`docs/diagrams/CU36-comunicacion-ubicacion-tecnico.drawio`** — abrir en Draw.io Desktop (Electron).
- **Corrección 2026-05-29:** Reescrito con la misma geometría que la plantilla login (827×1169): líneas `line` horizontales/verticales, enlaces `endArrow=none` control→entidades, flechas `block`/`classic` y etiquetas 10px para todos los mensajes 1.x y 2.x.

## CU36 — Consultar ubicación del técnico

### Artefactos BCE

| Rol | Nombre | Código |
|-----|--------|--------|
| Actor | Cliente | `mobile/lib/cliente/` |
| Boundary | V.Seguimiento | `emergencia_seguimiento_screen.dart` |
| Boundary | V.UbicacionTecnico | `emergencia_ubicacion_tecnico_screen.dart` |
| Boundary | V.Error | estados error / reintento |
| Control | SeguimientoController | `GET .../ubicacion-tecnico` |
| Entity | SolicitudEmergencia | `tecnico_ult_lat/lon`, validación cliente |
| Entity | Tecnico | precondición CU28 asignación |

### Mensajes (flujo normal)

| Msg | Paso CU | Descripción |
|-----|---------|-------------|
| 1. AbrirSeguimiento() | 2–3 | Lista → pantalla seguimiento |
| 1.1 VerUbicacionTecnico() | 4 | Botón ver ubicación |
| 1.2 ConsultarUbicacion() | 5 | Llama API FastAPI |
| 1.3 getUbicacionTecnico() | 6 | Valida dueño + GPS en BD |
| 1.4 return() | 6–7 | Respuesta JSON |
| 1.5 viewMapa() | 7 | Mapa + abrir en mapas |
| 1.6 Reintentar() | 8 opc. | `invalidate` provider |

### Excepciones (rojo en diagrama)

| Msg | Excepción CU |
|-----|-------------|
| 2.1 SinTecnicoAsignado() | Sin técnico asignado |
| 2.2 SinUbicacionCompartida() | Sin GPS compartido (CU37) |
| 2.3 ErrorRedOSesion() | Red / sesión CU2 |

### API anotada en diagrama

`GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico`
