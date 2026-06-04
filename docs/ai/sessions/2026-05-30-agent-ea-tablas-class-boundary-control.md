# Sesión — EA análisis de clases: tablas Class (no óvalos)

**Fecha:** 2026-05-30  
**Problema:** Vista/control se veían como óvalos (`type: boundary/control`), no como tablas de la plantilla CU1.

## Solución aplicada

1. Crear **18 elementos nuevos** `type: Class` con estereotipo `boundary` o `control` (IDs **268–285**).
2. **Nombre** = encabezado académico: `NombreCU::UI_xxx` / `NombreCU::XxxController`.
3. Operaciones `+` copiadas del CU (mostrar, index, patchEstado, etc.).
4. Diagramas **23, 26, 27, 28, 29, 30** actualizados: tablas nuevas en fila BCE; conectores nuevos (454+).
5. Antiguos óvalos renombrados `_legacy_*` y movidos a x≈2400 (fuera de vista).

## Mapa ID nuevo → CU

| ID | Nombre en EA |
|----|----------------|
| 268–269 | Gestion usuario (plantilla 23) |
| 270–271 | CU36 |
| 272–274 | Seleccionar taller |
| 275–278 | Procesar pago |
| 279–281 | Actualizar estado |
| 282–285 | Gestionar tenant |

## Verificación en EA

Abrir cada diagrama → F5. Debe verse:

- Rectángulo `<<boundary>>` con `CU::UI_*` y métodos `+`
- Rectángulo `<<control>>` con `CU::*Controller` y métodos `+`
- Entidades `Class` a la derecha

Si al alejar zoom aparecen puntos `_legacy_*`, borrarlos del diagrama (Delete from diagram, no del modelo).
