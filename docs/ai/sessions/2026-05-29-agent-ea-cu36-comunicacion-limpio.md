# Sesión 2026-05-29 — Diagrama comunicación CU36 en Enterprise Architect

## Diagrama definitivo (patrón wizard EA)
- Paquete: **`/Model/Comunicacion/CU36_Comunicacion_Recuperado`**
- Diagrama: **`sd CU36 Consultar ubicacion tecnico`** (ID **22**) — usar solo este. (ID 21 = `_obsoleto_CU36_v2`)
- Patrón: **Association** (línea) + **Collaboration** (mensaje con flecha), un mensaje por enlace.
- Elementos nuevos con estereotipos `control` / `boundary` / `entity`; legacy renombrados `_legacy_*`.
- Diagramas viejos renombrados `_obsoleto_*` (IDs 16, 18, 19).
- Elementos en diagrama 22: Cliente (93), SeguimientoController (123), V.Seguimiento (124), V.UbicacionTecnico (125), V.Error (126), M.SolicitudEmergencia (97).
- Conectores: Association 289–294 + Collaboration 295–297, 299–300 (patrón wizard). `1.2 return()` omitido en API para evitar solapamiento con `1.1 get()` — añadir en EA si hace falta.
- Mensajes: `0.1 consultarUbicacion`, `1.1 get`, `1.3 view` → V.Seguimiento, `2.1 view` → V.UbicacionTecnico, `3.1 errorView`.
- Se añadió **V.UbicacionTecnico** (pantalla mapa del CU36).

## Intento anterior (Limpio)
- Paquete **`/Model/Comunicacion/CU36_Comunicacion_Limpio`** — diagrama con más flujos (0–4); puede servir como referencia extendida.
- Layout estilo referencia **CU2 Gestionar categoría**: actor izquierda, controlador centro, boundaries arriba/abajo, entidades derecha.
- Artefactos: `Cliente`, `SeguimientoController`, `V.MisSolicitudes`, `V.Seguimiento`, `V.UbicacionTecnico`, `V.Error`, `M.SolicitudEmergencia`, `M.Tecnico`.
- Mensajes numerados (Collaboration): flujos 0 (listar), 1 (seguimiento), 2 (consultar ubicación + get/find), 3 (reintentar), 4.1 (errorView).
- Alineado con API real: `GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico` y pantallas Flutter `emergencia_seguimiento_screen` / `emergencia_ubicacion_tecnico_screen`.

## Ajuste manual sugerido en EA
- Colorear líneas como CU2: negro (lectura), rojo (errores si aplica), verde solo si hubiera borrado.
- Separar visualmente mensajes que comparten el mismo par de objetos (Layout → Optimize o mover etiquetas).

## Referencia wizard
- Plantilla: `/Model/Comunicacion/Communication Diagrams with Business Objects`.
