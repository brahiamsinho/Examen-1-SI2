# draw.io — diagramas editables

Capa visual **derivada** de PlantUML y alineada a Enterprise Architect.

## Archivos

| Tipo | Ubicación |
|------|-----------|
| `.drawio` editables | `docs/diagrams/drawio/*.drawio` (guardar aquí tras editar en el navegador) |
| Mermaid puente MCP | `docs/diagrams/drawio/mermaid/*.mmd` |
| Exports PNG/SVG | `docs/diagrams/output/drawio/` |

## Abrir con MCP (Cursor)

1. Asegurar MCP `drawio` conectado (`.cursor/mcp.json`).
2. Invocar al agente `@diagrams-modeling` con el archivo `.mmd` deseado.
3. En draw.io: **File → Save as** → copiar a `docs/diagrams/drawio/<id>-<nombre>.drawio`.

## Convención de nombres

Mismo ID que `agent-memory/CURRENT_STATE.md`:

- `01-context-c4.drawio` ↔ D-001  
- `02-containers-c4.drawio` ↔ D-002  
- `d008-componente-principal-sistema.drawio` ↔ D-008 (componente principal backend)
- `d020-diseno-conceptual-bd.drawio` ↔ D-020 (4.3.3.1.1 diseño conceptual BD)

Ver flujo completo: `../agent-memory/DRAWIO_INTEGRATION.md`.
