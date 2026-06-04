# Plantillas EA — Model Wizard / Model Builder

**Objetivo:** Reutilizar el diagrama de despliegue D-006 como patrón al crear proyectos nuevos en Enterprise Architect.

## Fuentes Sparx

- [Deployment Diagram (User Guide)](https://sparxsystems.com/enterprise_architect_user_guide/17.0/modeling_languages/deploymentdiagram.html)
- [Execution Environment (anidamiento)](https://sparxsystems.com/enterprise_architect_user_guide/17.0/modeling_languages/execution_environment.html)
- [UML2 Deployment Tutorial](https://www.sparxsystems.com/resources/tutorials/uml2/deployment-diagram.html)
- [Model Wizard — plantillas custom](https://sparxsystems.com/enterprise_architect_user_guide/17.1/modeling_frameworks/model_templates2.html)

## Layout JSON (agente MCP — en lugar de editar XML)

Durante el desarrollo el agente **no importa XML** (MCP no lo soporta). Usa:

`layouts/despliegue-azure-d006.layout.json` → `place_elements_on_diagram` + `layout_connectors`

Ver pipeline completo: `../agent-memory/EA_MCP_LAYOUT_PIPELINE.md`

## Crear patrón XML (congelar cuando esté listo)

1. En EA, abrir **`proyecto.eapx`** → paquete **`Despliegue`**.
2. Verificar diagrama **`Despliegue Azure UML`** (diagramID **9**).
3. Clic derecho en paquete **Despliegue** → **Copy / Branch → Package to XML** (o **Project Transfer → Export Package**).
4. Guardar como: `docs/diagrams/ea-templates/patterns/despliegue-azure-d006.xml`
5. (Opcional) Documentación Wizard: exportar `.rtf` con el mismo nombre base desde un **Document Artifact** en el paquete.
6. Para MDG Technology propio: en `.mts` agregar:

```xml
<ModelTemplates>
  <ModelTemplate name="Despliegue Azure D-006"
    location="despliegue-azure-d006.xml"
    icon="33"
    isFramework="false" />
</ModelTemplates>
```

`icon="33"` = icono diagrama Deployment en EA.

## Usar patrón en proyecto nuevo

1. **Add Model using Wizard** (o Start → Create from Pattern).
2. Pestaña **Model Patterns** o **Diagram**.
3. Seleccionar **Despliegue Azure D-006** (si está registrado en MDG) **o** importar XML manualmente.
4. Renombrar artefactos si cambia el stack (React→Angular, Django→FastAPI, MongoDB→PostgreSQL).

## Mejorar plantilla oficial EA

Las plantillas built-in de EA (Model Wizard → UML) suelen ser genéricas. Para acercarlas a la referencia del curso:

| Plantilla EA | Mejora |
|--------------|--------|
| Deployment genérico | Agregar `«device»` + **Artifact** dentro (no Actor) |
| Server node | Anidar 2–3 `«executionEnvironment»` (VM → capa → FE/BE) |
| Database | **Base de datos** como EE hermano de capa app, no suelto |
| Conectores | **CommunicationPath** con HTTPS / REST/HTTP / PostgreSQL |

## Limitación MCP (Cursor)

El MCP de EA **no** reproduce bien cubos 3D anidados como el tutorial Sparx (“Node as Container”). Tras generar vía MCP:

1. **View → Zoom → Fit in Window**
2. Arrastrar hijos faltantes desde Project Browser
3. **Diagram → Layout Diagram**
4. Ajustar artefactos **dentro** de devices/nodos (no flotando)

Ver `../agent-memory/DEPLOYMENT_DIAGRAM_UML_GUIDE.md` §6.
