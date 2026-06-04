---
name: uml-c4-puds-diagrams
description: >-
  Workflow de diagramas y artefactos PUDS para Examen-1-SI2: UML 2.5+ obligatorio,
  C4 en 4 capas, PlantUML en Git, draw.io MCP, memoria docs/diagrams/agent-memory.
  Usar cuando el usuario pida diagramas UML, C4, despliegue, PUDS, PlantUML, draw.io,
  Enterprise Architect, trazabilidad CU/RF, o actualizar documentación de modelado.
---

# UML 2.5 + C4 + PUDS — Diagramas (Examen-1-SI2)

## Cuándo aplicar esta skill

- Crear o editar diagramas (C4, UML paquetes/secuencia/clases/**despliegue**).
- Abrir diagramas en draw.io o sincronizar con EA.
- Defensa académica, trazabilidad CU → código, artefactos PUDS.
- **No** usar para implementar backend/frontend (→ subagentes `backend`, `frontend`).

## Lectura obligatoria (orden)

1. `docs/ai/PUDS_GUIDE.md`
2. `docs/diagrams/agent-memory/RULES.md`
3. `docs/diagrams/agent-memory/LEARNINGS.md` (no repetir errores)
4. `docs/diagrams/agent-memory/CURRENT_STATE.md`
5. **Si EA:** `docs/diagrams/agent-memory/EA_MODEL_WIZARD_WORKFLOW.md` — Model Wizard + documentación Sparx **antes** de MCP
6. Código o `docs/ai/ARCHITECTURE.md` según el diagrama

## Regla de oro: UML 2.5+ vs C4

| Necesidad | Notación | Ubicación |
|-----------|----------|-----------|
| Actores + sistema + externos | **C4 Context** | `docs/diagrams/c4/01-context.puml` |
| Apps desplegables (API, BD, móvil) | **C4 Container** | `c4/02-containers.puml` |
| Módulos dentro del API | **C4 Component** | `c4/03-components-backend.puml` |
| Clases de un CU | **C4 Code** o UML clases | `c4/04-*`, `uml/class-*.puml` |
| Paquetes backend | **UML 2.5 paquetes** | `uml/packages-backend-logical.puml` |
| Flujo HTTP/service | **UML 2.5 secuencia** | `uml/sequence-*.puml` |
| Modelo general de CU (include/extend) | **UML 2.5 casos de uso** | `USE_CASE_INCLUDE_EXTEND_GUIDE.md` + `uml/usecases/diagrama-general-*.puml` |
| Infra VM/Docker académica | **UML 2.5 despliegue** | `uml/deployment-docker-azure.puml` |

**Prohibido:** usar C4 Container o subgraphs Docker como diagrama de **despliegue académico**. Despliegue = `device`, `executionEnvironment`, `artifact`, CommunicationPath.

## Flujo de trabajo

1. Verificar nombres contra `backend/app/modules/` (grep, no inventar).
2. Crear/editar `.puml` en `docs/diagrams/c4/` o `uml/`.
3. Sincronizar puente `docs/diagrams/drawio/mermaid/*.mmd` si aplica draw.io.
4. **Abrir draw.io:** MCP **`user-drawio`** → `open_drawio_mermaid` (C4: `C4Context`, `C4Container`, `C4Component`).
5. Pedir al usuario guardar `.drawio` en `docs/diagrams/drawio/`.
6. EA (opcional): leer `agent-memory/EA_MCP_LAYOUT_PIPELINE.md`; `-enableEdit`; sin delete vía MCP.
7. Actualizar memoria (ver abajo).

## MCP draw.io

- Servidor Cursor: **`user-drawio`** (config clave `drawio` en mcp.json).
- Despliegue draw.io: **`deployment-docker-azure-uml.mmd`** (no `deployment-docker-azure.mmd` obsoleto).

## Memoria al terminar

| Alcance | Archivos |
|---------|----------|
| Diagramas | `docs/diagrams/agent-memory/CURRENT_STATE.md`, `HANDOFF.md`, `LEARNINGS.md` si hubo lección |
| Proyecto global | `docs/ai/CURRENT_STATE.md`, `HANDOFF_LATEST.md`, `PACKAGE_DESIGN.md`, `DIAGRAMS_GUIDE.md` |
| Sesión | `docs/ai/sessions/YYYY-MM-DD-*.md` |
| Decisión nueva | `docs/ai/DECISIONS_LOG.md` |

## Delegación de subagentes

| Tarea | Subagente |
|-------|-----------|
| Generar `.puml`, draw.io, EA | `diagrams-modeling` |
| Trazabilidad RF/CU, defensa PUDS | `puds` |
| Memoria `docs/ai/` | `docs-memory` |
| Coordinar quién hace qué | `orchestrator` |

## Checklist calidad

- [ ] UML 2.5+ en paquetes, secuencia, clases y despliegue
- [ ] C4 4 capas referenciadas si es arquitectura completa
- [ ] `.puml` en Git antes que solo draw.io
- [ ] draw.io abierto vía MCP si el usuario pidió vista editable
- [ ] Entre casos de uso: solo `<<include>>` / `<<extend>>` (no Association); guía `USE_CASE_INCLUDE_EXTEND_GUIDE.md`
- [ ] Sin `localhost` fijo en despliegue; sin CUxx en etiquetas visibles
- [ ] Entrada en `CURRENT_STATE` (diagramas)
