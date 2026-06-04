# 4.3.1.2 — Diseño lógico (diagrama de paquetes)

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Patrón:** **MVC** organizado en **tres capas** (Vista → Controlador → Modelo), como plantilla académica.

| Artefacto | Ubicación |
|-----------|-----------|
| **PlantUML** | `docs/diagrams/uml/diseño-logico-arquitectura-mvc.puml` (D-007) |
| **Enterprise Architect** | `Model` → **Diseño logico arquitectura** (package **12**) → **4.3.1.2 Diseño logico arquitectura MVC** (diagramID **39**) |
| **Backend detallado** | `docs/diagrams/uml/packages-backend-logical.puml` (D-003) — vista implementación |
| **Paquetes análisis CU** | `docs/puds/analisis/IDENTIFICACION_PAQUETES_CU.md` (4.2.1) |

---

## Qué responde (nivel 0)

| Capa | Qué es | En este proyecto |
|------|--------|------------------|
| **Vista** | Interfaz con el usuario | **Angular** (admin + taller web), **Flutter** (cliente + técnico móvil) |
| **Controlador** | Orquesta peticiones y reglas de entrada | **Routers/servicios FastAPI** (`app/modules/*/router.py`, `service.py`) |
| **Modelo** | Datos y persistencia | **SQLAlchemy** (`models.py`) + **PostgreSQL** |

**No confundir** con:

- **4.2.1** paquetes de *casos de uso* (análisis funcional).
- **D-003** paquetes de *código backend* (`app.modules.*`).
- **4.3.1.1** despliegue físico (Docker/Azure).

Este diagrama es la **arquitectura lógica MVC** para el documento de diseño.

---

## Módulos funcionales (5 + transversal)

Alineados a §2.5 del examen y a los paquetes de análisis 4.2.1:

| Módulo | Vista (ejemplos) | Controlador (backend) | Modelo |
|--------|------------------|----------------------|--------|
| Acceso y administración | Login admin/taller; auth Flutter; org SaaS | `acceso_y_administracion` | usuarios, tenants, roles |
| Seguimiento y atención | Mapa CU36; estado CU39; push CU41 | `incidentes.emergencias`, comunicaciones | emergencias, ubicación, estados |
| Taller y pagos | Bandeja taller; pago CU38; cotización CU42 | `atencion.taller_emergencias`, `pagos_y_comisiones` | talleres, pagos, comisiones |
| Continuidad offline | Pantallas offline CU45/CU43 | sync en emergencias | emergencia pendiente |
| Analítica KPIs | Dashboard admin CU46 | `admin_finanzas` | agregados KPI |

**Base de datos:** **PostgreSQL 15** (contenedor `db` en `docker-compose.yml`).

---

## Dependencias (plantilla académica)

### Verticales

| Origen | Destino | Significado |
|--------|---------|-------------|
| Controlador | Vista (arriba) | El controlador **usa** la capa de presentación asociada (acoplamiento MVC del curso) |
| Controlador | Modelo (abajo) | El controlador **accede** a entidades y persistencia |
| Modelo | PostgreSQL | Todos los modelos **persisten** en la misma BD |

### Horizontales (entre controladores)

| Origen | Destino | Justificación |
|--------|---------|---------------|
| Seguimiento | Taller y pagos | El seguimiento opera sobre un servicio ya asignado a taller |
| Taller y pagos | Acceso | Requiere sesión JWT y contexto tenant |
| Taller y pagos | Offline | Tras sincronizar emergencia offline entra el flujo comercial |
| Offline | Acceso | Registro/sync requiere autenticación |
| Analítica | Seguimiento | KPIs consumen datos de operación en curso |

### Cruzada (como ejemplo “actividades → venta” del curso)

| Origen | Destino |
|--------|---------|
| Controlador seguimiento | Modelo taller y pagos |

---

## Trazabilidad diagrama ↔ código

| Paquete lógico Controlador | Carpeta real |
|---------------------------|--------------|
| acceso_y_administracion | `backend/app/modules/acceso_y_administracion/` |
| seguimiento y atención | `incidentes/emergencias`, `comunicacion_y_notificaciones` |
| taller y pagos | `atencion/taller_emergencias`, `pagos_y_comisiones`, `talleres_y_tecnicos` |
| continuidad offline | lógica en emergencias + cliente Flutter |
| analítica KPIs | `acceso_y_administracion/admin_finanzas` |

| Paquete lógico Vista | Carpeta real |
|---------------------|--------------|
| acceso / admin | `frontend/src/app/admin/` |
| taller web | `frontend/src/app/taller/` |
| cliente / técnico móvil | `mobile/lib/cliente/`, `mobile/lib/tecnico/` |

---

## Enterprise Architect

| Elemento | elementID |
|----------|-----------|
| Paquetes Vista | **197–201** |
| Paquetes Controlador | **202–206** |
| Paquetes Modelo | **207–211** |
| PostgreSQL | **212** |
| Conectores | **399–420** |

**Franjas separadas por líneas (plantilla académica):**

| elementID | Elemento | Rol visual |
|-----------|----------|------------|
| **213** | DISEÑO LOGICO DE LA ARQUITECTURA | Marco exterior |
| **214** | Vista | Etiqueta franja superior |
| **215** | controlador | Etiqueta franja media |
| **216** | Modelo | Etiqueta franja inferior |

**Layout:** `docs/diagrams/ea-templates/layouts/diseño-logico-mvc-d007.layout.json`

**Pasos manuales en EA (líneas como la imagen del curso):**

1. Seleccionar paquetes **197–212** → **Format → Bring to Front**.  
2. Seleccionar nota **213** → **Format → Send to Back** (marco exterior).  
3. **Insert → Boundary** (o líneas horizontales): dibujar **3 franjas** apiladas:
   - **Vista** (arriba): paquetes 197–201  
   - **controlador** (medio): 202–206  
   - **Modelo** (abajo): 207–211 + PostgreSQL **212** centrado  
4. Colocar etiquetas **214–216** a la izquierda de cada franja (como la plantilla).  
5. **Line Style → Direct** en dependencias; **Ctrl+S**; export PNG Word **4.3.1.2**.

---

## Cómo defenderlo en oral

1. “Separé el diseño lógico en **MVC** y en los **cinco módulos** del documento de requisitos.”  
2. “La **Vista** no es solo web: tenemos **Angular** para admin/taller y **Flutter** para campo.”  
3. “Los **controladores** son los routers FastAPI; el **modelo** es SQLAlchemy sobre **PostgreSQL**.”  
4. “Las flechas son **dependencias UML**, no llamadas HTTP individuales.”  
5. “El diagrama D-003 baja al detalle de `app.modules.*`; este diagrama es la vista **académica** para el informe.”

---

## Relación con otros artefactos PUDS

```
Requisitos §2.5
    → Análisis paquetes CU (4.2.1)
        → Diseño lógico MVC (4.3.1.2) ← este documento
            → Diseño físico despliegue (4.3.1.1)
            → Secuencias / clases (4.3.x)
                → Implementación (repo)
```
