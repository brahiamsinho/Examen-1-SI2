# RULES — Qué usar y qué NO usar

Última actualización: 2026-05-28 (C4 4 capas + UML 2.5 + PUDS)

## Usar SIEMPRE

| Necesidad | Herramienta |
|-----------|-------------|
| Diagramas en Git, PR, examen | **PlantUML** (`.puml` en `docs/diagrams/`) |
| Vista arquitectura por niveles | **C4** vía includes C4-PlantUML en `c4/` |
| Paquetes, secuencia, despliegue académico | **UML 2.5+** en `uml/` |
| Casos de uso (general / include / extend) | **`USE_CASE_INCLUDE_EXTEND_GUIDE.md`** — Include/Extend en EA y PlantUML |
| ASCII en chat o README | `plantuml -utxt` (skill `plantuml-ascii`) |
| Edición visual / presentación | **draw.io MCP** (`user-drawio` en Cursor; config `drawio` en mcp.json) + `.drawio` en `docs/diagrams/drawio/` |
| C4 completo (4 capas) | `c4/01`…`04` + `drawio/mermaid/01`…`04` — ver `c4/README.md` |
| PUDS / trazabilidad | `docs/ai/PUDS_GUIDE.md`; CU en comentario `.puml`; coordinar con **`puds`** |
| UML despliegue en draw.io | **UML 2.5+** obligatorio — `drawio/mermaid/deployment-docker-azure-uml.mmd` ← `uml/deployment-docker-azure.puml` |
| Validar / **crear** modelo UML en EA | **Model Wizard + docs Sparx primero** → `EA_MODEL_WIZARD_WORKFLOW.md`; luego MCP `user-Enterprise Architect` + **`args: ["-enableEdit"]`** + EA abierto |
| Nombres de módulos backend | Rutas reales: `app.modules.<paquete>.<submódulo>` |
| Actores | `PROJECT_VISION.md` (Administrador, Cliente, Técnico, Taller Responsable) |
| SaaS en diagramas | `tenants`, `tenant_id`, `X-Tenant-Slug`, superadmin plataforma |
| Memoria del agente | Esta carpeta `agent-memory/` |
| Contexto producto | `docs/ai/ARCHITECTURE.md`, `DECISIONS_LOG.md`, **`PUDS_GUIDE.md`** |

## NO usar (salvo pedido explícito del usuario o del curso)

| Evitar | Por qué | Alternativa |
|--------|---------|-------------|
| Mermaid como **única** fuente de verdad | Debe existir `.puml` o modelo EA | PlantUML `.puml`; Mermaid solo en `drawio/mermaid/` |
| draw.io sin `.puml` respaldo | Pierde trazabilidad Git/PUDS | Crear/actualizar `.puml` primero |
| Confundir `@drawio/mcp` con `drawio-mcp` (npm) | Paquetes distintos | Usar solo `@drawio/mcp` (`.cursor/mcp.json`) |
| Inventar módulos o APIs | Rompe defensa y trazabilidad | Grep en `backend/app/modules/` |
| `localhost:8000` fijo en despliegue | Acopla a un entorno | Roles: API, BD, Cliente móvil; env en nota |
| Etiquetas `CU12`, `Ciclo 3` en diagramas de entrega | UX/copy del producto las eliminó | Comentario `' traza: CU11` en `.puml` |
| Diagrama gigante único | Ilegible en ASCII y en EA | Dividir por caso de uso o por capa C4 |
| Asumir MCP EA solo lectura sin configurar | Falta `-enableEdit` en MCP3.exe | Activar edición; backup `.eapx` |
| Asumir MCP EA crea el modelo sin `-enableEdit` | Tools de escritura deshabilitadas por Sparx | Ver `EA_INTEGRATION.md` |
| Crear diagrama EA solo con MCP (sin Wizard) | Lifelines genéricos, sin BCE, duplicados (ej. diagrama 11 vs 12) | **Ctrl+Shift+M** → pestaña Diagram → patrón UML; leer panel derecho; ver `EA_MODEL_WIZARD_WORKFLOW.md` |
| COCO/YOLO como “IA del negocio” en C4 | Confunde visión con clasificador | Caja `ai-inference` + backend `modules/ai` |
| BPMN / ArchiMate / SysML | No es el core del SI2 actual | Solo si la materia lo exige |
| `Association` entre dos casos de uso | Pierde `«include»`/`«extend»` en EA y defensa | `type: Include` o `type: Extend` en MCP; ver guía include/extend |
| Duplicar el mismo flujo en 4 archivos | Deuda de mantenimiento | Un `.puml` secuencia + enlace en PACKAGE_DESIGN |
| Hardcodear secretos, keys Stripe, JWT | Seguridad | “Stripe webhook” sin valores |

## Stack de notación (prioridad)

1. **C4 (4 capas)** — Context, Container, Component, Code (`c4/01`…`04`).  
2. **UML 2.5+ paquetes** — alineado a `backend/app/modules/`.  
3. **UML 2.5+ secuencia / clases** — flujos críticos (emergencia, pago, login tenant).  
4. **UML 2.5+ despliegue** — `device`, `executionEnvironment`, `artifact`, CommunicationPath (D-006). **Nunca** sustituir por C4 Container ni subgraphs Docker en entrega académica.  
5. **PUDS** — trazabilidad CU → diagrama → módulo (`PUDS_GUIDE.md`).

## Calidad mínima antes de dar por cerrado

- [ ] **EA:** Model Wizard revisado y documentación Sparx del tipo de diagrama consultada (`EA_MODEL_WIZARD_WORKFLOW.md`)
- [ ] **CU general:** include/extend con tipo correcto (`USE_CASE_INCLUDE_EXTEND_GUIDE.md`); actores solo con Association sólida
- [ ] Nombres verificados contra código o `ARCHITECTURE.md`  
- [ ] Leyenda o título con versión/fecha en comentario `@startuml`  
- [ ] Entrada en `CURRENT_STATE.md`  
- [ ] Fila en `docs/ai/PACKAGE_DESIGN.md` o `DIAGRAMS_GUIDE.md` si es diagrama nuevo  
- [ ] Render probado **o** motivo documentado en `LEARNINGS.md` (sin PlantUML, sin red C4)
