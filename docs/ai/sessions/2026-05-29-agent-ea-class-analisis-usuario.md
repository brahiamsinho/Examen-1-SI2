# Sesión 2026-05-29 — Diagrama análisis de clases Usuario en EA

## Ubicación
- Paquete: **`/Model/Clase`** (packageID **27**)
- Diagrama: **`class Analisis`** (diagramID **23**, tipo **Class**)

## Elementos
| ID | Nombre | Tipo EA | Rol |
|----|--------|---------|-----|
| 128 | Usuario | Actor | Actor del sistema |
| 129 | V.Usuario | Object + `boundary` | Vista |
| 130 | UsuarioController | Object + `control` | Controlador |
| 131 | Unidad | Class | Entidad |
| 132 | Usuario | Class | Entidad (mismo nombre que actor, distinto tipo) |
| 133 | Rol | Class | Entidad |

## Relaciones (connectorID)
- 301: Actor → UsuarioController (Association)
- 302: V.Usuario → UsuarioController (Association)
- 303: UsuarioController → Class Usuario (Dependency)
- 304: Unidad —`pertenece`— Usuario (`1` .. `1..*`)
- 305: Usuario —`tiene`— Rol (`1..*` .. `1`)

## Nota
Atributos replicados como en plantilla (`int`). Ajustar tipos reales (String, DateTime, etc.) cuando se alinee con el modelo de BD del proyecto.
