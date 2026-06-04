# Sesión 2026-05-28 — EA despliegue, MCP, reset

## Decisión del usuario

Dejar **EA en limpio** (borrar diagramas/paquetes) y **consolidar aprendizajes** en memoria del subagente `diagrams-modeling`.

## Limitación crítica MCP

**No hay tools de borrado** de diagramas, elementos ni paquetes. Reset = manual en EA (`EA_CLEAN_RESET.md`).

Tools de borrado existentes: solo `delete_connectors_or_messages`.

## Aprendizajes consolidados (D-006 despliegue)

1. **Jerarquía browser ≠ canvas** — `owningElementID` correcto no garantiza vista anidada.
2. **Padre tapa hijos** — Azure VM (102) cubre Capa/FE/BE si z-order mal; fix: Bring to Front manual.
3. **Conectores duplicados** — recrear paths sin borrar → efecto “escoba”; siempre listar y borrar antes.
4. **FE/BE horizontal** — vertical superpone en MCP; x=385 vs x=505, y=151.
5. **Internet → Capa (103)** — una flecha `HTTPS :80 / :8000`, no dos a FE/BE.
6. **Elemento 47** — duplicado obsoleto; MCP no quita del canvas.
7. **Diagrama nuevo (10)** — peor que iterar en diagrama 9; no migrar solo para limpiar.
8. **XML** — MCP no importa/exporta; usuario hace Package to XML; agente usa `.layout.json`.
9. **Pipeline híbrido** — MCP crea + JSON acomoda + usuario pulisce z-order + XML congela.

## Fuentes de verdad post-reset

| Entrega académica | Fuente |
|-------------------|--------|
| Despliegue Azure | `uml/deployment-docker-azure.puml` + `ea-templates/layouts/despliegue-azure-d006.layout.json` |
| Login clases | `uml/class-auth-login.puml` + `EA_LOGIN_CLASS_RUNBOOK.md` |
| C4 / secuencias | `.puml` en `docs/diagrams/` |

## Archivos memoria actualizados

- `EA_CLEAN_RESET.md` (nuevo)
- `EA_MCP_LAYOUT_PIPELINE.md`
- `EA_COORDINATE_GRID.md`
- `EA_DEPLOYMENT_MANUAL_FIX.md`
- `LEARNINGS.md`
- `CURRENT_STATE.md`
- `HANDOFF.md`
- `EA_INTEGRATION.md`
- `.cursor/agents/diagrams-modeling.md`
