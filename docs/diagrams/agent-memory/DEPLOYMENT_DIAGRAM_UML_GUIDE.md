# Guía UML 2.5 — Diagrama de despliegue (D-006)

**Fuentes:** [uml-diagrams.org/deployment-diagrams](https://www.uml-diagrams.org/deployment-diagrams.html), [Sparx UML2 Deployment Tutorial](https://www.sparxsystems.com/resources/tutorials/uml2/deployment-diagram.html), OMG UML 2.5 § Nodes/Artifacts.

**Referencia académica del curso:** dispositivos + artefactos | Internet | entornos de ejecución anidados (VM → Docker → Frontend/Backend/BD).

---

## 1. Qué responde el diagrama (PUDS)

| Pregunta | Artefacto UML |
|----------|---------------|
| ¿Dónde corre el software? | Nodos + artefactos |
| ¿En qué hardware/plataforma? | `«device»`, `«executionEnvironment»` |
| ¿Cómo se comunican? | **CommunicationPath** con protocolo |
| ¿Qué archivo/imagen se despliega? | **Artifact** dentro del nodo |

Trazabilidad: `docker-compose.yml` → servicios → nodos EA.

---

## 2. Elementos UML obligatorios

| Elemento | Stereotype EA | Forma | Ejemplo proyecto |
|----------|---------------|-------|------------------|
| **Device** | `device` | Cubo 3D | Web, Dispositivo móvil |
| **Artifact** | (keyword artifact) | Rectángulo + icono doc | Navegador Angular, App Flutter, FastAPI, PostgreSQL |
| **Execution environment** | `executionEnvironment` | Cubo 3D | Azure VM, Docker Compose, Frontend, Backend, Base de datos |
| **Node** genérico | — | Cubo 3D | Internet |
| **Communication path** | — | Línea + etiqueta | HTTPS, REST/HTTP, PostgreSQL |
| **External** (convención) | `external` | Cubo 3D | Stripe, Firebase FCM |

### Reglas de anidamiento (UML 2.5)

```
«device» Web
  └── Artifact: Navegador Angular

«executionEnvironment» Azure VM Docker Host
  └── «executionEnvironment» Capa aplicacion
  │     ├── «executionEnvironment» Frontend
  │     │     └── Artifact: nginx + Angular SPA
  │     └── «executionEnvironment» Backend
  │           └── Artifact: FastAPI uvicorn
  └── «executionEnvironment» Base de datos
        └── Artifact: PostgreSQL 15
```

- Los **execution environment** pueden anidarse (BD dentro de Docker dentro de VM).
- Los **artefactos** van **dentro** del nodo donde se ejecutan (no flotando en el canvas).
- Relación alternativa: **Dependency** con stereotype `«deploy»` del artefacto al nodo.

---

## 3. Layout académico (referencia curso)

```
┌─────────┐                    ┌──────────────────────────────────┐
│ «device»│                    │ «executionEnvironment»           │
│  Web    │──HTTPS──┐          │  Azure VM                        │
│ [artef.]│         │          │  ┌────────────────────────────┐  │
└─────────┘         │          │  │ «executionEnvironment»     │  │
┌─────────┐         │  ┌───────│──│ Docker Compose             │  │
│ «device»│──HTTPS──┼─►│Internet│  │ ┌Frontend [art]┐          │  │
│  Móvil  │         │  └───────│──│ │ Backend [art]│──Stripe   │  │
│ [artef.]│         │          │  │ └Base datos[art]┘  FCM     │  │
└─────────┘         │          │  └────────────────────────────┘  │
                    │          └──────────────────────────────────┘
```

**Columnas (x creciente):**

1. Dispositivos (~40–170 px)
2. Internet (~230 px)
3. Stack servidor (~420 px) — **mismo ancho** en Frontend/Backend/BD
4. Externos (~680 px)

**Filas:** Web arriba, móvil abajo; servidor en pila vertical; artefactos **dentro** de cada cubo.

---

## 4. Conectores (CommunicationPath)

| Origen | Destino | Etiqueta |
|--------|---------|----------|
| Web | Internet | HTTPS |
| Dispositivo móvil | Internet | HTTPS |
| Internet | Capa aplicacion | HTTPS :80 / :8000 |
| Frontend | Backend | REST/HTTP |
| Backend | Base de datos | PostgreSQL |
| Backend | Stripe | HTTPS API |
| Backend | Firebase FCM | HTTPS |

No conectar artefactos directamente a Internet; conectar **nodos**.

---

## 5. Mapeo Examen-1-SI2 → UML

| docker-compose | Puerto host | Nodo UML | Artefacto |
|----------------|-------------|----------|-----------|
| frontend | 80 | Frontend | nginx + Angular SPA |
| backend | 8000 | Backend | FastAPI uvicorn |
| db | 5432 (interno) | Base de datos | PostgreSQL 15 |
| — | — | Azure VM Docker Host | (contenedor lógico) |
| — | — | Docker Compose | emergencias_network |

---

## 6. Enterprise Architect — reglas MCP

### ✅ Hacer

1. Crear **jerarquía en el Project Browser** (`owningElementID` padre → hijo).
2. En el **canvas**, colocar solo nodos hoja visibles si el MCP tapa padres.
3. Terminar layout **manual en EA** (2 min):
   - Seleccionar Frontend + Backend + Base de datos
   - **Insert → Boundary** → nombre `Docker Compose`
   - Seleccionar Boundary + los 3 → **Insert → Boundary** → `Azure VM Docker Host`
4. **Diagram → Layout Diagram** o líneas ortogonales.
5. **View → Zoom → Fit in Window**.

### ❌ No hacer (aprendido 2026-05-28)

- Colocar nodo padre grande **y** hijos en las mismas coordenadas vía MCP → el padre **tapa** hijos.
- Dejar artefactos sueltos fuera del device/nodo padre.
- Usar **Actor** en despliegue (reservado para casos de uso).
- Mezclar C4 Container con UML Deployment en el mismo diagrama.

### Diagrama EA canónico

| Diagrama | diagramID | Estado |
|----------|-----------|--------|
| **Despliegue Azure UML** | **9** | ✅ **Canónico** — usar este |
| Despliegue Azure / produccion | 5, 4, 7 | Obsoleto |
| OBSOLETO Docker Azure | 3 | Borrar |

---

## 7. PlantUML alineado

Ver `uml/deployment-docker-azure.puml` — debe reflejar anidamiento `node` + `artifact`, no solo cajas sueltas.

---

## 8. Defensa oral (PUDS)

- **Análisis:** actores Cliente, Técnico, Taller; sistema en Azure VM.
- **Diseño lógico:** capas Frontend / Backend / Persistencia.
- **Diseño de despliegue:** este diagrama + `docker-compose.yml`.
- **Implementación:** contenedores `frontend`, `backend`, `db`.
- **Pruebas:** healthchecks compose; acceso :80 y :8000.
