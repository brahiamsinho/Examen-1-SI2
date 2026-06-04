# Memoria del subagente `diagrams-modeling`

Carpeta **exclusiva** para continuidad del agente de diagramas. No sustituye `docs/ai/` (memoria global del proyecto).

## Orden de lectura (cada sesión)

1. Skill **`.cursor/skills/uml-c4-puds-diagrams/SKILL.md`** (checklist global)  
2. `RULES.md` — prohibiciones y stack permitido  
2. **`docs/ai/PUDS_GUIDE.md`** — fases PUDS, UML 2.5+ vs C4  
3. `CONVENTIONS.md` — cómo nombrar y dónde guardar  
4. `CURRENT_STATE.md` — qué diagramas existen y su vigencia  
5. `LEARNINGS.md` — errores que **no** deben repetirse  
6. `HANDOFF.md` — último trabajo pendiente  
7. `DEPLOYMENT_DIAGRAM_UML_GUIDE.md` — despliegue UML 2.5+  
7b. **`USE_CASE_INCLUDE_EXTEND_GUIDE.md`** — obligatorio si hay diagrama general de CU (`«include»` / `«extend»`)  
8. **`EA_MODEL_WIZARD_WORKFLOW.md`** — **obligatorio antes de EA:** Model Wizard + docs Sparx  
9. `EA_INTEGRATION.md` — MCP Enterprise Architect (`-enableEdit`)  
10. `EA_MCP_LAYOUT_PIPELINE.md` — si crea/edita en EA vía MCP  
11. `EA_CLEAN_RESET.md` — si hay que vaciar el `.eapx`  
12. `DRAWIO_INTEGRATION.md` — si toca draw.io MCP  
13. `../MCP_SETUP.md` — activar servidores en Cursor  

Luego: `docs/ai/ARCHITECTURE.md` + código bajo `backend/app/modules/` según el diagrama.

## Orden de escritura (al terminar)

1. Actualizar `CURRENT_STATE.md` (tabla de diagramas)  
2. Sobrescribir `HANDOFF.md` con fecha, cambios y próximo paso  
3. Añadir entrada fechada en `LEARNINGS.md` **solo** si hubo incidente o decisión nueva  
4. Si cambió diseño lógico: `docs/ai/PACKAGE_DESIGN.md` y `docs/ai/DIAGRAMS_GUIDE.md`  
5. Sugerir al orquestador actualizar `docs/ai/HANDOFF_LATEST.md` si el hito es visible para todo el equipo  

## Aprendizaje continuo

- Cada fallo de render, timeout EA o desalineación con código → una viñeta en `LEARNINGS.md` con **síntoma → causa → regla nueva**.  
- No borrar entradas antiguas; marcar `RESUELTO` si ya no aplica.  
- Preferir reglas accionables (“usar X”) sobre opiniones vagas.

## Relación con otros agentes

| Agente | Relación |
|--------|----------|
| `puds` | RF/CU, trazabilidad, defensa oral |
| `architect-planner` | Decisiones estructurales antes de nuevos contenedores C4 |
| `docs-memory` | Sincronizar hitos en `docs/ai/CURRENT_STATE.md` |
| `backend` / `frontend` / `mobile` | Validar nombres de módulos y rutas |
