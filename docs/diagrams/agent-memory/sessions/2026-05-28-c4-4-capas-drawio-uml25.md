# Sesión diagrams-modeling — 2026-05-28 (C4 + draw.io + UML 2.5)

## Hecho

- Modelo C4 completo (4 capas) en Git + Mermaid draw.io.
- Despliegue draw.io migrado a `deployment-docker-azure-uml.mmd` (UML 2.5, no Docker/C4).
- MCP `user-drawio`: 4 diagramas C4 abiertos en navegador (Context, Container, Component, Code).
- `PUDS_GUIDE.md` creado en `docs/ai/`.

## Reglas reforzadas

| Tema | Regla |
|------|-------|
| UML | **2.5+ obligatorio** en `uml/` y despliegue draw.io/EA |
| C4 | 4 niveles; Mermaid `C4Context`/`C4Container`/`C4Component` en draw.io |
| draw.io MCP | Servidor **`user-drawio`**; no confundir con nombre `drawio` en config |
| Fuente verdad | `.puml` Git → `.mmd` puente → `.drawio` guardado por usuario |
| EA | Sin delete vía MCP; reset manual `EA_CLEAN_RESET.md` |

## Pendiente

- [ ] Usuario guarda `D-001`…`D-004-c4-*.drawio` y `D-006-deployment-uml.drawio`
- [ ] EA limpio + recrear D-006 / D-010
- [ ] Render PlantUML local (C4 includes remotos)
