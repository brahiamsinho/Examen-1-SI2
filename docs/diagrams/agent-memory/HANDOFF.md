# HANDOFF — diagrams-modeling

**Fecha:** 2026-05-28 — **C4 4 capas + draw.io + UML 2.5 + PUDS**

## Estado actual

| Aspecto | Estado |
|---------|--------|
| C4 (4 capas) en Git | ✅ D-001…D-004c + `c4/README.md` |
| draw.io Mermaid puente | ✅ `01`…`04` + `deployment-docker-azure-uml.mmd` |
| draw.io MCP | ✅ `user-drawio` — 4 C4 abiertos en sesión 2026-05-28 |
| `.drawio` guardados en repo | ⏳ Pendiente usuario (File → Save as) |
| UML 2.5 despliegue | ✅ D-006 `.puml` + D-006m |
| PUDS guía | ✅ `docs/ai/PUDS_GUIDE.md` |
| EA `.eapx` | ⚠️ Reset manual pendiente — `EA_CLEAN_RESET.md` |

## Fuente de verdad

1. **PlantUML** `docs/diagrams/c4/` y `uml/`
2. **PUDS** `docs/ai/PUDS_GUIDE.md`, `PACKAGE_DESIGN.md`
3. **Memoria agente** `docs/diagrams/agent-memory/` (RULES, LEARNINGS)

## Reglas que no olvidar

- **UML 2.5+ obligatorio** para despliegue, paquetes, secuencia, clases.
- **C4 ≠ UML despliegue** — no mezclar en entrega.
- draw.io: MCP **`user-drawio`**; C4 nativo en Mermaid.
- EA: **Model Wizard + docs Sparx primero** (`EA_MODEL_WIZARD_WORKFLOW.md`); luego MCP sin delete; layout JSON + Bring to Front manual.

## Próximo agente

1. Verificar si usuario guardó `.drawio` en `docs/diagrams/drawio/`.
2. Confirmar reset EA; recrear D-006 con `despliegue-azure-d006.layout.json`.
3. Coordinar `TRACEABILITY_MATRIX.md` con **`puds`**.
4. Leer `sessions/2026-05-28-c4-4-capas-drawio-uml25.md` antes de tocar diagramas.
