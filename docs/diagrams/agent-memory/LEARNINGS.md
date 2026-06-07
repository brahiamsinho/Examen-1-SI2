# LEARNINGS — Errores y reglas aprendidas

Formato de cada entrada:

```
### YYYY-MM-DD — Título corto
- **Síntoma:** ...
- **Causa:** ...
- **Regla:** ...
- **Estado:** ACTIVO | RESUELTO
```

---

### 2026-05-28 — Implementar EA sin Model Wizard ni docs Sparx
- **Síntoma:** Diagrama login legacy (ID 11) con lifelines FastAPI/PostgreSQL; duplicado respecto al canónico BCE (ID 12).
- **Causa:** MCP creó `Object`/`Class` genéricos sin partir del patrón Analysis/Sequence del Model Wizard ni reglas BCE de la guía oficial.
- **Regla:** Antes de MCP: **Ctrl+Shift+M** → pestaña **Diagram** (o Model Patterns) → leer descripción del patrón → `Create Pattern(s)` → ajustar nombres al código. Consultar [Sequence Diagram](https://sparxsystems.com/enterprise_architect_user_guide/14.0/model_domains/sequencediagram.html). Runbook: `EA_MODEL_WIZARD_WORKFLOW.md`.
- **Estado:** ACTIVO

### 2026-05-28 — Intento D-010 login en EA: timeout MCP
- **Síntoma:** Usuario pidió crear diagrama en EA; `get_root_packages` / `get_current_package` → timeout.
- **Causa:** EA no conectado al bridge MCP3.exe en esa sesión (cerrado, proyecto no abierto, o timeout 3s).
- **Regla:** No afirmar diagrama creado en `.eapx` sin respuesta exitosa de `create_or_update_diagram`. Runbook listo: `EA_LOGIN_CLASS_RUNBOOK.md`.
- **Estado:** ACTIVO

### 2026-05-28 — EA MCP sí edita, pero requiere `-enableEdit`
- **Síntoma:** Documentación Sparx promete `create_or_update_elements` pero Cursor solo muestra tools `get_*`.
- **Causa:** Por defecto Sparx **deshabilita** creación/modificación; hace falta `"args": ["-enableEdit"]` en la config de `MCP3.exe`.
- **Regla:** Antes de pedir “diagrama en EA”, verificar tools de escritura en MCP y backup del `.eapx`. Ver FAQ oficial Sparx MCP.
- **Estado:** ACTIVO

### 2026-05-28 — MCP Enterprise Architect sin conexión
- **Síntoma:** `get_root_packages` → timeout.
- **Causa:** EA no abierto o bridge COM del MCP inactivo en Windows.
- **Regla:** Antes de depender de EA, intentar un tool MCP; si falla, continuar con PlantUML y anotar en HANDOFF que EA quedó pendiente.
- **Estado:** ACTIVO

### 2026-05-28 — C4-PlantUML requiere includes
- **Síntoma:** Render falla si no hay red o el include remoto está bloqueado.
- **Causa:** `!include https://raw.githubusercontent.com/...` necesita descargar stdlib.
- **Regla:** Documentar fallback con copia local en `docs/diagrams/lib/C4-PlantUML/` o render en máquina con internet.
- **Estado:** ACTIVO

### 2026-05-28 — No inventar POST /servicios
- **Síntoma:** Documentos académicos externos piden `/servicios` genérico.
- **Causa:** Plantilla Word no mapeada al dominio emergencias.
- **Regla:** En secuencias usar `POST /api/app/cliente/emergencias` (ver `TESTING_STRATEGY.md`).
- **Estado:** ACTIVO

### 2026-05-28 — draw.io MCP: URL / diagrama muy grande
- **Síntoma:** El editor no abre o falla al pasar XML/Mermaid enorme.
- **Causa:** Límite práctico de longitud de URL en el flujo del MCP oficial.
- **Regla:** Dividir en varios `.mmd` (por caso de uso o por capa C4); un diagrama = un ID en CURRENT_STATE.
- **Estado:** ACTIVO

### 2026-05-28 — draw.io vs EA: no hay import UML bidireccional fiable
- **Síntoma:** Se espera que draw.io “sincronice” clases con EA automáticamente.
- **Causa:** Formatos y metamodelos distintos.
- **Regla:** EA = modelo académico UML; draw.io = vista derivada; nombres alineados manualmente vía `RULES.md`.
- **Estado:** ACTIVO

### 2026-05-28 — EA despliegue: nodo padre tapa hijos vía MCP
- **Síntoma:** Diagrama D-006 con cubo Azure gigante; solo se ven etiquetas REST/HTTP y PostgreSQL; no Frontend/Backend/BD como en referencia académica.
- **Causa:** UML permite anidar nodos; EA MCP `place_elements_on_diagram` dibuja el padre **encima** de hijos en mismas coordenadas. No equivale a Insert Boundary manual.
- **Regla:** Modelo = jerarquía en browser (`102` Azure → `103` Capa → FE/BE; BD hermano). Canvas: colocar **Azure VM (102)** visible + hijos dentro; MCP no sustituye **Insert → Boundary** ni arrastre manual. Diagrama canónico: **Despliegue Azure UML** (diagramID **9**). Ver `ea-templates/README.md`.
- **Estado:** ACTIVO

### 2026-05-28 — UML despliegue ≠ C4 Container
- **Síntoma:** Mezclar actores, contenedores Docker sueltos y IP/NSG en un solo diagrama confuso.
- **Causa:** C4 describe contenedores lógicos; UML Deployment describe **device / executionEnvironment / artifact / communication path** (uml-diagrams.org).
- **Regla:** Referencia académica = dispositivos con artefacto dentro | Internet | entornos anidados con artefactos | externos `«external»`.
- **Estado:** ACTIVO

### 2026-05-28 — EA despliegue: conectores duplicados = efecto “escoba”
- **Síntoma:** 4–6 flechas paralelas entre Web→Internet o Internet→Backend; labels ilegibles.
- **Causa:** Recrear `create_or_update_connectors` sin borrar conectores previos del mismo par (IDs 46–61, 109–116, 152–159 acumulados).
- **Regla:** Siempre `get_current_diagram` → `delete_connectors_or_messages` duplicados → crear **exactamente 7** paths. Ver `EA_COORDINATE_GRID.md`.
- **Estado:** RESUELTO (diagramID 9, conectores 160–161, 164–168)

### 2026-05-28 — EA despliegue: FE/BE vertical se superponen vía MCP
- **Síntoma:** Frontend y Backend en mismas coordenadas y; solo se ve uno.
- **Causa:** EA auto-redimensiona nodos hijos dentro de `Capa aplicacion` al apilar verticalmente.
- **Regla:** Colocar Frontend y Backend **en horizontal** (x=388 vs x=508, misma y=118). Entrada Internet → **Capa aplicacion** (103), no a FE y BE por separado.
- **Estado:** ACTIVO

### 2026-05-28 — EA: diagrama nuevo (10) sin nodos hijos visibles
- **Síntoma:** `Despliegue Azure UML (final)` solo muestra cubo Azure vacío + labels de conectores; no Capa/FE/BE/BD.
- **Causa:** Crear diagrama nuevo y colocar vía MCP no reproduce el anidamiento visual que sí funciona tras iteraciones en diagrama **9**.
- **Regla:** Canónico = **diagramID 9**. No migrar a diagrama nuevo solo para quitar elemento 47; borrar 47 manualmente en el 9.
- **Estado:** ACTIVO

### 2026-05-28 — draw.io despliegue debe ser UML 2.5+, no Docker/C4
- **Síntoma:** Se abrió `deployment-docker-azure.mmd` con subgraphs Docker/NSG — no cumple entrega académica UML.
- **Causa:** Puente Mermaid antiguo mezclaba infra Docker con notación C4-like.
- **Regla:** Despliegue en draw.io/EA/PlantUML = **UML 2.5** (`device`, `executionEnvironment`, `artifact`, CommunicationPath). Usar `deployment-docker-azure-uml.mmd` ← `uml/deployment-docker-azure.puml`.
- **Estado:** ACTIVO

### 2026-05-28 — draw.io no aparecía en Settings → MCP
- **Síntoma:** Solo EA en User MCP; `drawio` solo en `.cursor/mcp.json` del repo, invisible en UI.
- **Causa:** Cursor lista **User MCP Servers** desde `%USERPROFILE%\.cursor\mcp.json` (global). El archivo del proyecto no sustituye al global en esa pantalla.
- **Regla:** Añadir `drawio` al **global** `~/.cursor/mcp.json` o **New MCP Server** en Settings. Repo mantiene copia en `.cursor/mcp.json` para el equipo.
- **Estado:** RESUELTO (añadido a global 2026-05-28)

### 2026-05-28 — draw.io MCP configurado pero no conectado en Cursor
- **Síntoma:** Agente no ve tools `open_drawio_mermaid`; solo EA/MongoDB/Figma.
- **Causa:** Servidor `drawio` en `.cursor/mcp.json` no cargado en sesión MCP (refresh) o `npx` en Windows sin `.cmd`.
- **Regla:** Verificar verde en Settings → MCP. Windows: `"command": "C:\\Program Files\\nodejs\\npx.cmd"`. Tools esperados: `open_drawio_xml`, `open_drawio_csv`, `open_drawio_mermaid`.
- **Estado:** ACTIVO (pendiente re-test usuario)

### 2026-05-28 — MCP EA no puede borrar diagramas ni paquetes
- **Síntoma:** Usuario pidió “borrar todos los diagramas y dejar EA limpio” vía agente.
- **Causa:** MCP Trial 15 solo expone `delete_connectors_or_messages`; no hay `delete_diagram`, `delete_element`, `delete_package`, ni import/export XML.
- **Regla:** Reset EA = usuario **Delete Package** en Project Browser. Inventario pre-reset en `EA_CLEAN_RESET.md`. Fuente de verdad = PlantUML + `.layout.json` en git.
- **Estado:** ACTIVO

### 2026-05-28 — C4 completo debe abrirse en draw.io, no solo en Git
- **Síntoma:** Usuario pidió modelo C4 4 capas; agente entregó solo `.puml` sin abrir draw.io.
- **Causa:** Falta invocar MCP `user-drawio` → `open_drawio_mermaid` tras crear `.mmd`.
- **Regla:** Tras crear/actualizar puente Mermaid, **siempre** abrir draw.io y dar enlaces al usuario. C4 en Mermaid: `C4Context`, `C4Container`, `C4Component`; Code = `classDiagram`.
- **Estado:** ACTIVO

### 2026-05-29 — EA: Include/Extend como Association (sin estereotipo visible)
- **Síntoma:** Diagrama general CU36–CU40 con flechas sólidas entre casos de uso; sin etiquetas `«include»` / `«extend»` como en plantilla académica.
- **Causa:** MCP `create_or_update_connectors` con `type: Association` o sin tipo `Include`/`Extend`; EA no aplica notación UML de caso de uso.
- **Regla:** Entre dos **UseCase** solo `type: Include` o `type: Extend` + `direction: FromSourceToTarget`. Actor→CU = `Association` sólida. Ver `USE_CASE_INCLUDE_EXTEND_GUIDE.md`. Verificar con `get_diagrams_information` que `type` sea Include/Extend.
- **Estado:** Si en diagrama 26 los conectores Include/Extend aparecen como `Association`, borrar esos IDs y recrear (331–335 canónicos tras fix 2026-05-29).

### 2026-05-28 — PUDS + UML 2.5 son referencia obligatoria del agente diagramas
- **Síntoma:** Riesgo de mezclar notaciones (Docker subgraph, C4 despliegue) en entrega académica.
- **Causa:** Varios estándares en paralelo (C4, UML, Docker) sin guía única.
- **Regla:** Leer `docs/ai/PUDS_GUIDE.md` y `DEPLOYMENT_DIAGRAM_UML_GUIDE.md` antes de modelar. **UML 2.5+** en paquetes/secuencia/clases/despliegue; **C4** solo para arquitectura lógica 4 capas. Trazabilidad CU → diagrama → código.
- **Estado:** ACTIVO

### 2026-06-07 - EA/PUML: Clases BCE robustas vs rectangulares en Análisis
- **Síntoma:** El usuario pidió Clases UML rectangulares con atributos explícitos, pero el diagrama mostraba círculos BCE sin métodos (Robustness).
- **Causa:** En PlantUML, usar `boundary`, `control`, `entity` fuerza iconos sin compartments. En EA, crear elementos de análisis con ciertos estereotipos/tipos o usar los del modelo de dominio puede ocultar atributos al dibujarse como íconos.
- **Regla:** Para Clases de Análisis rectangulares, en `.puml` usar `class` puro. En EA, crear clases con prefijos (`V.`, `C.`, `E.`) dentro del paquete del caso de uso con `type: Class` y `stereotypes: ""` y ponerlas en un diagrama `Class` para visualizar métodos y atributos explícitamente.
- **Estado:** ACTIVO

### 2026-06-07 - EA/UML: Actor modelado como Class
- **Síntoma:** El Actor `Tecnico` estaba modelado como una clase de análisis (`Class`) con atributos y métodos, y conectado a la entidad `E.SolicitudEmergencia`.
- **Causa:** En los diagramas de análisis BCE a veces se confunde o mezcla la entidad del dominio (ej. `E.Tecnico`) con el actor que interactúa con el sistema (`Tecnico`).
- **Regla:** El Actor que interactúa con la Boundary (Vista) debe ser estrictamente de tipo `Actor` (stickman). La entidad de dominio correspondiente debe ser `Class` (ej. `E.Tecnico`) ubicada del lado derecho y conectada solo a las entidades, **nunca** a la Vista que usa el actor.
- **Estado:** ACTIVO (Resuelto en diagramas de análisis CU36-CU40).

<!-- Añadir nuevas entradas arriba de esta línea -->
