# Sesión 2026-05-28 — C4 4 capas, draw.io, UML 2.5+ y memoria PUDS

## Objetivo

Completar modelo **C4 en 4 capas**, abrirlo en **draw.io** vía MCP, reforzar **UML 2.5+ obligatorio** para despliegue y consolidar memoria para continuidad entre agentes.

## Entregables

| ID | Artefacto | Tipo |
|----|-----------|------|
| D-001 | `c4/01-context.puml` + `drawio/mermaid/01-context-c4.mmd` | C4 Context |
| D-002 | `c4/02-containers.puml` + `02-containers-c4.mmd` | C4 Container |
| D-003c | `c4/03-components-backend.puml` + `03-components-backend-c4.mmd` | C4 Component |
| D-004c | `c4/04-code-emergencias-alta.puml` + `04-code-emergencias-c4.mmd` | C4 Code (CU11) |
| D-006 | `uml/deployment-docker-azure.puml` | UML 2.5 despliegue |
| D-006m | `drawio/mermaid/deployment-docker-azure-uml.mmd` | draw.io UML (no Docker/C4) |
| — | `docs/diagrams/c4/README.md` | Índice C4 |
| — | `docs/ai/PUDS_GUIDE.md` | Guía PUDS + trazabilidad |

## draw.io MCP

- Servidor Cursor: **`user-drawio`** (global `~/.cursor/mcp.json` + proyecto `.cursor/mcp.json`).
- Tools: `open_drawio_mermaid`, `open_drawio_xml`, `open_drawio_csv`.
- C4 en draw.io: Mermaid nativo `C4Context`, `C4Container`, `C4Component`; nivel 4 = `classDiagram`.
- **Pendiente usuario:** guardar `.drawio` en `docs/diagrams/drawio/` (D-001…D-004, D-006).

## Aprendizajes clave

1. **UML 2.5+ siempre** para paquetes, secuencia, clases y despliegue académico.
2. **C4 ≠ UML despliegue** — no mezclar en entrega.
3. **PlantUML primero**, draw.io = puente visual; EA = modelo académico opcional.
4. **EA reset** manual (MCP no borra paquetes); fuente Git intacta.
5. **C4 4 capas** obligatorias para defensa de arquitectura del producto.

## Próximo agente

- Confirmar reset EA si aplica.
- Recrear D-006 en EA con `despliegue-azure-d006.layout.json`.
- Guardar `.drawio` exportados por usuario.
- Completar `TRACEABILITY_MATRIX.md` con **`puds`**.
