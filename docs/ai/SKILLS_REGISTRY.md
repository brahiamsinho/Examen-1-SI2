# SKILLS_REGISTRY.md

Registro de skills del proyecto (`.cursor/skills/`, `.agents/skills/`).

Última actualización: **2026-05-28**

## Skills de diagramas y documentación (proyecto)

| Skill | Ruta | Cuándo usar |
|-------|------|-------------|
| **uml-c4-puds-diagrams** | `.cursor/skills/uml-c4-puds-diagrams/` | UML 2.5+, C4 4 capas, PUDS, PlantUML, draw.io, EA, trazabilidad |
| **plantuml-ascii** | `.agents/skills/plantuml-ascii/` | Render `-utxt` / `-txt` para README o chat |

## Subagentes relacionados (no son skills)

| Subagente | Rol |
|-----------|-----|
| `diagrams-modeling` | Ejecuta modelado; lee skill `uml-c4-puds-diagrams` |
| `puds` | Análisis PUDS, trazabilidad; delega diagramas |
| `docs-memory` | Memoria `docs/ai/` |

## Regla

- **Skill** = checklist y reglas que cualquier agente puede seguir.
- **Subagente** = rol especializado con delegación desde `orchestrator`.

Tras añadir una skill nueva, actualizar esta tabla y `HANDOFF_LATEST.md` si afecta al equipo.
