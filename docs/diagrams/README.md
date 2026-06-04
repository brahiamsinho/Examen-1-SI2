# Diagramas del proyecto

Fuente versionada de modelos **UML 2.5+** y **C4** para defensa PUDS y continuidad entre agentes.

## Estructura

| Carpeta | Contenido |
|---------|-----------|
| `c4/` | Diagramas C4 (contexto, contenedores, componentes) |
| `uml/` | Paquetes, secuencia, componentes, despliegue |
| `drawio/` | `.drawio` editables + `mermaid/` para MCP draw.io |
| `output/` | Artefactos generados (PNG, `.utxt`) — ver `.gitignore` |
| `agent-memory/` | **Memoria exclusiva** del subagente `@diagrams-modeling` |
| `MCP_SETUP.md` | Activar draw.io y EA en Cursor |

## Generar (local)

Requisito: [PlantUML](https://plantuml.com/) instalado o JAR.

```powershell
cd docs\diagrams\c4
plantuml -utxt -o ..\output 01-context.puml
plantuml -png -o ..\output 02-containers.puml
```

Unicode ASCII (recomendado en README/PR):

```powershell
plantuml -utxt -o ..\output ..\uml\sequence-emergencia-alta-cliente.puml
```

C4 usa includes remotos de [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML); hace falta red en el primer render o copiar el stdlib local (ver `agent-memory/CONVENTIONS.md`).

## Índice de diagramas

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `c4/01-context.puml` | C4 Context | Actores y sistema |
| `c4/02-containers.puml` | C4 Container | Backend, BD, front, móvil, IA, Stripe |
| `c4/03-components-backend.puml` | C4 Component | Módulos dentro del API FastAPI |
| `c4/04-code-emergencias-alta.puml` | C4 Code | Clases CU11 — alta emergencia cliente |
| `c4/README.md` | Índice C4 | Las 4 capas + render |
| `uml/packages-backend-logical.puml` | UML paquetes | Módulos `app.modules.*` |
| `uml/sequence-emergencia-alta-cliente.puml` | UML 2.5 secuencia | Alta emergencia cliente |
| `uml/sequence-auth-login.puml` | UML 2.5 secuencia | Login `POST /api/auth/login` |
| `uml/class-auth-login.puml` | UML clases | Login `POST /api/auth/login` |
| `uml/deployment-docker-azure.puml` | UML despliegue | Docker Compose en VM Microsoft Azure |
| `uml/componente-principal-sistema.puml` | UML Component | Hub FastAPI + módulos + capas |

## Agentes

- Crear/actualizar diagramas: **`.cursor/agents/diagrams-modeling.md`**
- Trazabilidad PUDS: **`.cursor/agents/puds.md`**
- Convenciones globales: **`docs/ai/DIAGRAMS_GUIDE.md`**
