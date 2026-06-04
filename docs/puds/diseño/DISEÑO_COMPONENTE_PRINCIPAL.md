# Diagrama de componente principal del sistema

**Sección examen:** **4.4.1.1.1** Diagrama de componente principal del sistema  
**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Artefacto PUDS:** Diseño — **componente principal** del backend (hub FastAPI + módulos + capas internas).

| Artefacto | Ubicación |
|-----------|-----------|
| **PlantUML (UML Component)** | `docs/diagrams/uml/componente-principal-sistema.puml` (D-008) |
| **draw.io (editable)** | `docs/diagrams/drawio/d008-componente-principal-sistema.drawio` |
| **Mermaid puente MCP** | `docs/diagrams/drawio/mermaid/componente-principal-sistema.mmd` |
| **Enterprise Architect** | `Model` → **Componentes sistema** (package **13**) → **Diagrama componente principal del sistema** (diagramID **40**) |
| **Script recreación EA** | `scripts/ea-create-componente-principal.ps1` (EA abierto con .eapx) |
| **Layout JSON** | `docs/diagrams/ea-templates/layouts/componente-principal-d008.layout.json` |

---

## Qué es (nivel 0)

| Zona del diagrama | Qué representa |
|-------------------|----------------|
| **Centro — Backend API (FastAPI)** | Punto de entrada único: `app = FastAPI()` + routers bajo `/api` |
| **Izquierda — módulos funcionales** | Dominios de negocio (`app/modules/…`) |
| **Derecha — capas internas** | Patrón por módulo: router → service → repository → model |
| **Arriba — HTTP + JWT** | REST JSON; auth Bearer + header `X-Tenant-Slug` |
| **Abajo — BD, medios, externos** | PostgreSQL, carpeta evidencias, Stripe/FCM/IA |

**Para entender bien esto:** un **componente UML** es una pieza reemplazable con interfaz; aquí el **núcleo** es FastAPI y todo lo demás **depende** o **es usado por** ese núcleo.

---

## Mapa módulos funcionales → código

| Componente diagrama | Carpeta / routers reales |
|---------------------|--------------------------|
| Acceso, Roles y Permisos | `acceso_y_administracion/auth`, `roles`, `permisos`, `tenants`, `public_tenants` |
| Usuarios | `acceso_y_administracion/usuarios` |
| Clientes y Vehículos | `clientes_y_vehiculos/clientes`, `vehiculos` |
| Incidentes (Emergencias) | `incidentes/emergencias` |
| Gestión Talleres y Técnicos | `talleres_y_tecnicos/talleres`, `tecnico`, `taller_responsable` |
| Inteligencia del Incidente | `modules/ai` (enrich, payload) |
| Priorización y Asignación | `ai` assignment/rank + lógica asignación taller |
| Atención de Solicitudes | `atencion/taller_emergencias` (bandeja, comisiones) |
| Finanzas y Pagos SaaS | `pagos_y_comisiones`, `admin_finanzas`, `billing` |
| Notificaciones y Comunicaciones | `comunicacion_y_notificaciones` |
| Historial y Trazabilidad | `acceso_y_administracion/bitacora` |

---

## Capas internas (derecha) → archivos típicos

| Capa | Archivo / carpeta |
|------|-------------------|
| Routers | `*/router.py` |
| URLs / Endpoints | `main.py` → `app.include_router(..., prefix=PREFIX)` |
| Schemas | `*/schemas.py` |
| Services | `*/service.py` o `*/service/*.py` |
| Permissions / Security | `app/core/dependencies.py`, `permisos` |
| Repositories | `*/repository.py` (emergencias, atencion, notificaciones, ai…) |
| Models | `*/models.py` |
| Migrations | `backend/migrations/*.sql` |
| Middleware | `app/core/tenant_middleware.py`, CORS en `main.py` |
| Static / Media | `app.mount(.../media/evidencias)`, `backend/uploads/` |

**Flujo discontinuo (plantilla):** Routers → Services → Repositories → Models → PostgreSQL.

---

## Infraestructura inferior

| Componente | Implementación |
|------------|----------------|
| **PostgreSQL** | Contenedor `db`, `DATABASE_URL`, RLS multi-tenant (`0016`) |
| **Almacenamiento medios** | `EVIDENCIAS_*`, uploads foto/audio emergencia |
| **Servicios externos** | Stripe (pagos/billing), Firebase FCM (push), `ai-inference` (YOLO/Whisper), SMTP/Mailhog |

---

## Enterprise Architect (creado)

| Artefacto | ID |
|-----------|-----|
| Paquete **Componentes sistema** | **13** |
| Diagrama **Diagrama componente principal del sistema** | **40** |

**Recrear o actualizar layout:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/ea-create-componente-principal.ps1
```

(Requiere EA abierto con tu `.eapx`.)

**Revisión manual:** `View → Zoom → Fit in Window`; **Line Style → Direct** si hay flechas dobladas; **Ctrl+S**; export PNG.

---

## draw.io (D-008)

**Abrir el diagrama:**

1. Ir a [https://app.diagrams.net](https://app.diagrams.net) o abrir la app de escritorio.
2. **File → Open from → Device** → seleccionar `docs/diagrams/drawio/d008-componente-principal-sistema.drawio`.
3. **View → Fit Page** para ver todo el lienzo.
4. Ajustar flechas: seleccionar conector → **Line Style → Direct** (líneas rectas).
5. Exportar para Word: **File → Export as → PNG** → guardar en `docs/diagrams/output/drawio/`.

**Colores (plantilla académica):**

| Zona | Color |
|------|-------|
| Módulos funcionales (izquierda) | Amarillo `#fff4cc` |
| Capas internas (derecha) | Azul `#d6eaf8` |
| Infra / externos (abajo) | Verde `#d5f5e3` |
| HTTP | Rosa `#ffe0e0` |
| Auth / tenant | Morado `#e8d4ff` |
| Núcleo FastAPI | Blanco, borde grueso |

**Puente Mermaid** (regenerar borrador vía MCP draw.io): `docs/diagrams/drawio/mermaid/componente-principal-sistema.mmd`

---

## Vista C4 complementaria

| **Vista C4** | `docs/diagrams/c4/03-components-backend.puml` |
| **Código fuente** | `backend/app/main.py`, `backend/app/modules/*`, `backend/app/core/*` |

---

## Enterprise Architect (crear manualmente — obsoleto si ya existe diagrama 40)

EA MCP no está disponible en esta sesión. Pasos recomendados:

1. **Model → Add → Package** → `Componentes sistema`  
2. **Add Diagram → Component** → nombre: `Diagrama componente principal del sistema`  
3. **Insert → Component** — colocar:
   - Centro: `Backend API (FastAPI)`  
   - Izquierda: 11 componentes funcionales (color amarillo claro)  
   - Derecha: capas internas (azul claro)  
   - Arriba: HTTP/REST, JWT  
   - Abajo: PostgreSQL (nota con tablas), Medios, Externos (verde claro)  
4. **Connectors:** Dependency o Assembly según EA; etiquetar protocolos donde aplique.  
5. Línea discontinua derecha: Routers → Services → Repositories → Models → BD.  
6. Export PNG para el Word.

**Alternativa rápida:** generar PNG desde PlantUML:

```bash
plantuml -tpng -o docs/diagrams/output docs/diagrams/uml/componente-principal-sistema.puml
```

---

## Cómo defenderlo en oral

1. “El **componente central** es la API FastAPI; todos los módulos de negocio se registran como **routers** en `main.py`.”  
2. “Cada módulo sigue **router → service → repository → model**; eso aparece en la columna derecha.”  
3. “La **seguridad** entra por JWT y **tenant** (`X-Tenant-Slug`) antes de llegar a los servicios.”  
4. “**PostgreSQL** concentra las entidades; las **evidencias** van a almacenamiento de archivos con metadatos en BD.”  
5. “Integraciones **externas** (Stripe, FCM, IA) salen del backend, no del móvil directamente.”

---

## Diferencia vs otros diagramas

| Diagrama | Pregunta que responde |
|----------|----------------------|
| **4.3.1.2 MVC paquetes** | Vista / Controlador / Modelo por módulo funcional |
| **D-008 componente principal** | **Qué piezas** tiene el backend y **cómo se conectan** |
| **C4 03-components** | Vista C4 nivel contenedor (clientes ↔ API) |
| **4.3.1.1 despliegue** | Dónde corre físicamente (Docker/Azure) |

---

## Trazabilidad PUDS

```
Requisitos §2.5
  → Casos de uso (4.1)
  → Paquetes análisis (4.2)
  → Diseño lógico MVC (4.3.1.2)
  → **Componente principal (este diagrama)**
  → Secuencias / clases por CU
  → Implementación backend/app/
```
