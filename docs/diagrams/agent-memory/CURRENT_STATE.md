# CURRENT_STATE — Diagramas del repositorio

Última actualización: **2026-05-28** (C4 4 capas + draw.io + UML 2.5 + PUDS)

## Estado general

| Aspecto | Estado |
|---------|--------|
| Subagente `.cursor/agents/diagrams-modeling.md` | ✅ Actualizado con pipeline EA |
| Memoria `docs/diagrams/agent-memory/` | ✅ Consolidada (reset + aprendizajes) |
| PlantUML en repo | ✅ Fuente de verdad versionada |
| MCP Enterprise Architect | ✅ Conectado; **sin tools de borrado** |
| Modelo `.eapx` en EA | ⚠️ **Reset manual** — ver `EA_CLEAN_RESET.md` |
| Modelo `.eapx` en repo | ❌ No versionado (esperado) |

## Inventario Git (`.puml` / Mermaid) — vigente

| ID | Archivo | Tipo | Notas |
|----|---------|------|-------|
| D-001 | `c4/01-context.puml` | C4 Context | |
| D-002 | `c4/02-containers.puml` | C4 Container | |
| D-003c | `c4/03-components-backend.puml` | C4 Component | Zoom API backend |
| D-004c | `c4/04-code-emergencias-alta.puml` | C4 Code | CU11 alta emergencia |
| D-003 | `uml/packages-backend-logical.puml` | UML paquetes | |
| D-004 | `uml/sequence-emergencia-alta-cliente.puml` | UML secuencia | |
| D-006 | `uml/deployment-docker-azure.puml` | UML 2.5 despliegue | **Fuente canonica** entrega academica |
| D-006m | `drawio/mermaid/deployment-docker-azure-uml.mmd` | draw.io (UML 2.5) | Puente MCP; NO usar `deployment-docker-azure.mmd` (Docker/C4) |
| D-010 | `uml/class-auth-login.puml` | UML clases | Login + tenant |
| D-011-BCE | `uml/sequence-auth-login-bce.puml` | UML 2.5 secuencia BCE | **Canónico entrega** — estilo CU2 |
| D-011-EA | EA diagramID **12** `sd Login - Iniciar sesion` | UML secuencia BCE | Paquete **6** |
| D-011 (legacy) | `uml/sequence-auth-login.puml` / EA **11** | Tecnológico | No usar en defensa |
| **Ciclo 4 UC** | `uml/usecases/ciclo4/CU36`–`CU40.puml` | UML Use Case | Git + EA paquete **7**, diagramas **13–17** (18–21 obsoletos) |
| D-UC-GEN | `uml/usecases/diagrama-general-casos-uso.puml` | UML Use Case general | **4.1.5 Ciclo 4** EA paquete **7**, diagramID **26** (CU36–CU40) |
| **Ciclo 5 UC Gen** | `uml/ciclo5/CU41-CU46-diagrama-casos-uso.puml` | UML Use Case general | EA paquete **37**, diagramID **77** |
| **CU36 Análisis Clases** | `uml/ciclo4/CU36-analisis-clases-bce.puml` | UML Análisis Clases | **EA diagramID 66** (Clases rectangulares: V.UbicacionTecnico, C.SeguimientoController, E.SolicitudEmergencia, E.Tecnico) |
| **CU37 Análisis Clases** | - | UML Análisis Clases | **EA diagramID 67** (Clases rectangulares V/C/E, asociaciones simples + asociaciones entre Entidades con multiplicidad) |
| **CU38 Análisis Clases** | - | UML Análisis Clases | **EA diagramID 68** (Clases rectangulares V/C/E, asociaciones simples + asociaciones entre Entidades con multiplicidad) |
| **CU39 Análisis Clases** | - | UML Análisis Clases | **EA diagramID 69** (Clases rectangulares V/C/E, asociaciones simples + asociaciones entre Entidades con multiplicidad) |
| **CU40 Análisis Clases** | - | UML Análisis Clases | **EA diagramID 70** (Clases rectangulares V/C/E, asociaciones simples + asociaciones entre Entidades con multiplicidad) |
| **CU41 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 71** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples + multiplicidad 1..1) |
| **CU42 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 72** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples + multiplicidad 1..1) |
| **CU43 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 73** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples + multiplicidad 1..1) |
| **CU44 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 74** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples + multiplicidad 1..1) |
| **CU45 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 75** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples) |
| **CU46 Análisis Clases** | `uml/ciclo5/CU41-CU46-analisis-clases.puml` | UML Análisis Clases | **EA diagramID 76** (Clases rectangulares V/C/E, atributos/métodos inyectados, asociaciones simples) |
| **CU36 BCE (obsoleto)** | `uml/ciclo4/CU36-analisis-clases-bce.puml` | UML Análisis BCE | **EA diagramID 62** (Iconos robustos) |
| D-020 | `uml/class-database-conceptual.puml` | UML clases BD | **Canónico** EA paquete **8**, diagramID **23** |
| D-020 (obsoleto) | `uml/class-database-multitenant-core.puml` | UML clases BD | EA diagramID **22** — layout ilegible |
| D-*m | `drawio/mermaid/01`…`04-*-c4.mmd` | Puente draw.io C4 | Notación C4Context/Container/Component |
| — | `c4/README.md` | Índice C4 4 capas | |
| — | `docs/ai/PUDS_GUIDE.md` | PUDS + UML 2.5 | Trazabilidad CU ↔ diagrama |

## EA — estado tras reset (objetivo)

| En EA | Antes reset | Después reset (objetivo) |
|-------|-------------|---------------------------|
| Paquetes bajo Model | 2, 3, 4, 5 | **Ninguno** |
| Diagramas | IDs 1–10 | **Ninguno** |
| Layout JSON preservado | — | `ea-templates/layouts/despliegue-azure-d006.layout.json` |

## EA — inventario pre-reset (archivado)

Ver tablas en `EA_CLEAN_RESET.md` y `sessions/2026-05-28-ea-reset-y-aprendizajes.md`.

## EA — D-020 Clases BD (2026-05-28)

| Elemento | ID |
|----------|-----|
| Paquete | **9** — `Objetos de dominio` (dentro de paquete 8) |
| Diagrama **canónico** | **24** — `DISEÑO CONCEPTUAL DE LA BASE DE DATOS` |
| Diagramas obsoletos | **22** spaghetti, **23** círculos |
| Clases (147–157) | Tenant, Usuario, Rol, UsuarioRol, Cliente, MarcaVehiculo, Vehiculo, Taller, Tecnico, SolicitudEmergencia, Pago |
| Asociaciones | **276–290** (verbos: agrupa, es, tiene, define, clasifica, posee, solicita, involucra, emplea, atiende, asigna, genera) |

| D-021 | uml/modelo_conceptual.puml | UML clases BD | **Nuevo** DISEÑO CONCEPTUAL DE LA BASE DE DATOS con TODAS las entidades. EA paquete **38**, diagramID **78** |
| D-022 | `uml/modelo_conceptual.mermaid` | Mermaid ER | Código fuente ER para draw.io |
| D-022m| `drawio/diseno_bd_conceptual.drawio` | draw.io ER | Diseño conceptual generado vía MCP draw.io |

## Pendientes

| Prioridad | Tarea |
|-----------|--------|
| Alta | Usuario: **guardar `.eapx`** tras D-020 |
| Alta | Usuario: guardar `.drawio` D-001…D-004, D-006 en `docs/diagrams/drawio/` |
| Alta | Usuario: Delete Package ×4 en EA (si aún no hecho) |
| Media | Recrear D-006 en EA con pipeline MCP + layout JSON |
| Media | Recrear D-010 login si hace falta en EA |
| Baja | Export XML patrón cuando diagrama esté pulido |

## Regla EA (2026-05-28)

Antes de MCP: **Model Wizard** + documentación Sparx — ver `EA_MODEL_WIZARD_WORKFLOW.md` (DEC-029).

## Artefactos memoria EA (nuevos/actualizados)

| Archivo | Propósito |
|---------|-----------|
| `EA_MODEL_WIZARD_WORKFLOW.md` | Wizard + docs Sparx obligatorios |
| `EA_CLEAN_RESET.md` | Cómo vaciar EA |
| `EA_MCP_LAYOUT_PIPELINE.md` | MCP + layout JSON |
| `EA_COORDINATE_GRID.md` | Coordenadas D-006 |
| `EA_DEPLOYMENT_MANUAL_FIX.md` | Bring to Front, etc. |
| `ea-templates/layouts/*.layout.json` | Grilla machine-readable |
