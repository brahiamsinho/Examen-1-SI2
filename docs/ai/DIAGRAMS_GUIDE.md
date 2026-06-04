# DIAGRAMS_GUIDE.md

Guía global de diagramas. La **fuente versionada** vive en `docs/diagrams/`. La **memoria del agente de diagramas** en `docs/diagrams/agent-memory/`.

**PUDS y UML 2.5+:** leer **`docs/ai/PUDS_GUIDE.md`** antes de crear o entregar diagramas académicos.

## Subagentes

| Agente | Rol |
|--------|-----|
| **`diagrams-modeling`** | PlantUML, C4 (4 capas), UML 2.5+, draw.io MCP, EA |
| Skill | **`.cursor/skills/uml-c4-puds-diagrams/`** — checklist obligatorio |
| **`puds`** | Trazabilidad RF/CU, artefactos PUDS, defensa académica |

## Convenciones rápidas

| Tema | Regla |
|------|--------|
| Formato principal | PlantUML (`.puml`) en Git |
| **UML** | **2.5+ obligatorio** — paquetes, secuencia, clases, **despliegue** |
| **C4** | **4 capas:** Context, Container, Component, Code (`c4/01`…`04`) |
| Despliegue académico | UML `device` / `executionEnvironment` / `artifact` — **no** C4 ni Docker subgraph |
| Backend | UML paquetes ↔ `app.modules.*` |
| draw.io | MCP **`user-drawio`** + `drawio/mermaid/*.mmd` → guardar `.drawio` |
| EA | **Model Wizard + docs Sparx** → MCP + layout JSON; ver `agent-memory/EA_MODEL_WIZARD_WORKFLOW.md` |

Detalle: `docs/diagrams/agent-memory/RULES.md`, `DEPLOYMENT_DIAGRAM_UML_GUIDE.md`.

## Índice diagramas

| ID | Archivo | Tipo |
|----|---------|------|
| D-001 | `c4/01-context.puml` | C4 Context |
| D-002 | `c4/02-containers.puml` | C4 Container |
| D-003c | `c4/03-components-backend.puml` | C4 Component |
| D-004c | `c4/04-code-emergencias-alta.puml` | C4 Code (CU11) |
| D-003 | `uml/packages-backend-logical.puml` | UML 2.5 paquetes |
| D-004 | `uml/sequence-emergencia-alta-cliente.puml` | UML 2.5 secuencia |
| D-006 | `uml/deployment-docker-azure.puml` | **UML 2.5 despliegue** |
| D-008 | `uml/componente-principal-sistema.puml` | **UML Component — principal del sistema** |
| D-010 | `uml/class-auth-login.puml` | UML 2.5 clases |

Inventario completo: `docs/diagrams/README.md`, `agent-memory/CURRENT_STATE.md`.

## Artefactos PUDS

| Archivo | Rol |
|---------|-----|
| **`PUDS_GUIDE.md`** | Fases PUDS, trazabilidad, cuándo C4 vs UML |
| `PACKAGE_DESIGN.md` | Paquetes lógicos + enlaces `.puml` |
| `TRACEABILITY_MATRIX.md` | Pendiente — con `puds` |
| `SEQUENCE_FLOWS.md` | Pendiente |
| `COMPONENTS_OVERVIEW.md` | Pendiente |

## Render local

```powershell
cd docs\diagrams\c4
plantuml -png -o ..\output 01-context.puml 02-containers.puml 03-components-backend.puml 04-code-emergencias-alta.puml
cd ..\uml
plantuml -png -o ..\output deployment-docker-azure.puml
```

## Actualización obligatoria

Tras cambios relevantes: `docs/ai/CURRENT_STATE.md`, `HANDOFF_LATEST.md`, `docs/diagrams/agent-memory/HANDOFF.md`, sesión en `docs/ai/sessions/`.
