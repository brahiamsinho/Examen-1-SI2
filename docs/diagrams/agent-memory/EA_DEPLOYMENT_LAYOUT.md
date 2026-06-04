# Runbook — Diagrama de despliegue D-006 en EA

**Diagrama canónico:** `Despliegue Azure UML` (diagramID **9**)
**Guía UML:** `DEPLOYMENT_DIAGRAM_UML_GUIDE.md`
**Plantillas Wizard:** `../ea-templates/README.md`

Abrir: **Model → Despliegue → Despliegue Azure UML**

---

## Por qué MCP solo no alcanza

Según [Sparx Deployment Tutorial](https://www.sparxsystems.com/resources/tutorials/uml2/deployment-diagram.html), los nodos son **contenedores**: artefactos y EE hijos se **incrustan** en el cubo padre. El MCP de EA coloca cubos 3D independientes y el padre **tapa** a los hijos si comparten área.

**Solución:** jerarquía correcta en Project Browser + layout manual 2–3 min (o exportar patrón XML para Model Wizard).

---

## Estructura UML (como referencia del curso)

```
«device» Web → Artifact Navegador Angular
«device» Dispositivo móvil → Artifact Aplicacion movil
Internet
«executionEnvironment» Azure VM Docker Host (102)
  ├── «executionEnvironment» Capa aplicacion (103)
  │     ├── Frontend → nginx + Angular SPA
  │     └── Backend → FastAPI uvicorn
  └── Base de datos → PostgreSQL 15
«external» Stripe, Firebase FCM
```

---

## Ajuste manual en EA (2 min) si falta algo

1. **View → Zoom → Fit in Window**
2. Project Browser → **Despliegue** → expandir **Azure VM Docker Host**
3. Si **Frontend** no se ve: arrastrarlo **dentro** de **Capa aplicacion** en el canvas
4. Artefactos **dentro** de Web/Móvil/Frontend/Backend/BD (icono documento, no sueltos)
5. **Diagram → Layout Diagram** (conectores ortogonales)
6. Conectores solo entre **nodos** (CommunicationPath): HTTPS, REST/HTTP, PostgreSQL

---

## Grilla de coordenadas

Ver **`EA_COORDINATE_GRID.md`** — columnas A→D, FE/BE **horizontal** dentro de Capa aplicacion, 7 conectores sin duplicar.

## Conectores (7)

| Origen | Destino | Etiqueta |
|--------|---------|----------|
| Web / Móvil | Internet | HTTPS |
| Internet | Capa aplicacion | HTTPS :80 / :8000 |
| Frontend | Backend | REST/HTTP |
| Backend | Base de datos | PostgreSQL |
| Backend | Stripe | HTTPS API |
| Backend | Firebase FCM | HTTPS |

---

## Diagramas obsoletos (cerrar / borrar)

3, 4, 5, 6, 7 — intentos MCP con layout incorrecto.
