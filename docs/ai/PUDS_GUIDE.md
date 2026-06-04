# PUDS_GUIDE.md — Proceso Unificado y artefactos del proyecto

Última actualización: **2026-05-29**

Este proyecto usa un enfoque **alineado a PUDS** (Proceso Unificado de Desarrollo de Software): análisis → diseño → implementación → pruebas → despliegue, con **trazabilidad** entre artefactos y código real.

## Reglas transversales (obligatorias)

| Regla | Detalle |
|-------|---------|
| **UML 2.5+** | Paquetes, secuencia, clases, componentes y **despliegue** usan notación UML 2.5 o superior. No sustituir despliegue académico por C4 Container ni diagramas Docker genéricos. |
| **C4 (4 capas)** | Context, Container, Component, Code — arquitectura lógica del producto. Ver `docs/diagrams/c4/README.md`. |
| **Fuente Git** | PlantUML `.puml` en `docs/diagrams/` es la verdad versionada. draw.io y EA son vistas derivadas. |
| **No inventar** | Módulos, rutas API y actores deben coincidir con `backend/app/modules/` y `ARCHITECTURE.md`. |
| **Agentes** | **`puds`** → trazabilidad y artefactos; **`diagrams-modeling`** → generación `.puml`, C4, draw.io, EA. |

## Fases PUDS ↔ artefactos en este repo

| Fase PUDS | Artefacto | Ubicación | Estado |
|-----------|-----------|-----------|--------|
| Visión / alcance | Visión del producto | `PROJECT_VISION.md` | ✅ |
| Requisitos | Casos de uso, RF (Word/curso) | Externo + comentarios en `.puml` | Parcial |
| Análisis | Actores, contexto sistema | C4 D-001, secuencias | ✅ |
| Diseño lógico | Paquetes backend | D-003 `uml/packages-backend-logical.puml`, `PACKAGE_DESIGN.md` | ✅ |
| Diseño arquitectura | Contenedores, componentes | C4 D-002, D-003c | ✅ |
| Diseño detallado | Clases por flujo | D-004c, D-010 login, secuencias | ✅ parcial |
| Diseño despliegue | UML Deployment 2.5+ | D-006 `uml/deployment-docker-azure.puml` | ✅ |
| Implementación | Código modular | `backend/app/modules/*` | ✅ |
| Pruebas | Estrategia, pytest | `TESTING_STRATEGY.md`, `backend/tests/` | Parcial |
| Despliegue | Docker Compose, Azure | `docker-compose.yml`, D-006 | ✅ |

## Matriz trazabilidad mínima (CU → diagrama → código)

| CU / flujo | Diagrama | Implementación |
|------------|----------|----------------|
| CU11 Alta emergencia cliente | D-004 secuencia, D-004c Code | `incidentes/emergencias/` |
| CU36–CU40 Ciclo 4 (ubicación, taller, pago, tenant) | `uml/usecases/ciclo4/` + EA paquete **7** diag. **13–17** | CU36–37: `emergencias/` (ubicacion, seleccion_taller); CU38: `pagos/` + Stripe; CU39: `tecnico/`; CU40: `tenants/`, `billing/`. Matriz: `docs/puds/casos-uso/CICLO4_SEGUIMIENTO_TIEMPO_REAL.md` |
| Login + tenant | D-010 clases | `acceso_y_administracion/auth/` |
| Arquitectura global | D-001…D-002 C4 | `main.py`, front, mobile |
| Módulos API | D-003c Component, D-003 paquetes | `app/modules/*` |
| Despliegue VM Azure | D-006 UML 2.5 | `docker-compose.yml` |

Pendiente ampliar: `TRACEABILITY_MATRIX.md` (coordinar con agente **`puds`**).

## Notación: cuándo usar qué

```
┌─────────────────────────────────────────────────────────────┐
│  C4 (Simon Brown)     →  ¿Quién? ¿Qué apps? ¿Módulos API?   │
│  UML paquetes/secuencia/clases  →  Diseño lógico PUDS       │
│  UML despliegue 2.5+  →  device, executionEnvironment,      │
│                          artifact, CommunicationPath          │
└─────────────────────────────────────────────────────────────┘
```

**No mezclar** C4 Container con UML Deployment en el mismo diagrama de entrega.

## Casos de uso — include y extend (UML 2.5)

Artefacto **4.1.5 Estructurar el Modelo de Caso de Uso**: diagrama general con actores, límite del sistema y relaciones entre CU.

| Relación | Notación | Regla |
|----------|----------|--------|
| Actor ↔ CU | Asociación **sólida** | Participación del actor |
| **include** | Flecha **discontinua** `«include»` | CU base → CU incluido (comportamiento obligatorio reutilizado) |
| **extend** | Flecha **discontinua** `«extend»` | CU extensión → CU base (comportamiento opcional) |

Guía del proyecto: `docs/diagrams/agent-memory/USE_CASE_INCLUDE_EXTEND_GUIDE.md`.  
Ciclo 4: `docs/puds/casos-uso/MODELO_GENERAL_CASOS_USO.md` + EA diagrama **26**.

## Flujo de trabajo diagramas (PUDS + agentes)

1. **`puds`** identifica CU/RF y qué artefacto falta.
2. **`diagrams-modeling`** crea/actualiza `.puml` (UML 2.5+ o C4).
3. Puente draw.io: `docs/diagrams/drawio/mermaid/*.mmd` → MCP **`user-drawio`**.
4. EA (opcional): modelo académico; pipeline MCP + layout JSON; reset manual si hace falta.
5. Actualizar `PACKAGE_DESIGN.md`, `CURRENT_STATE.md`, `HANDOFF_LATEST.md`.

## Defensa oral — frases útiles

- «El **diseño lógico por paquetes** está en D-003 y refleja `app.modules.*`.»
- «El **diagrama de despliegue** es UML 2.5 con `device`, `executionEnvironment` y `artifact`, no C4.»
- «La trazabilidad CU11 va de la secuencia al router `emergencias` y al servicio `crear_solicitud`.»
- «C4 nivel 2 muestra contenedores desplegables; nivel 3 zoom en la API FastAPI.»

## Referencias internas

- `docs/ai/DIAGRAMS_GUIDE.md`
- `docs/diagrams/agent-memory/RULES.md`
- `docs/diagrams/agent-memory/DEPLOYMENT_DIAGRAM_UML_GUIDE.md`
- `docs/diagrams/c4/README.md`
