# 4.2.1 — Identificación de paquetes (casos de uso)

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Artefacto PUDS:** Análisis de paquetes — vista de **casos de uso** (no confundir con paquetes de código `app/modules/`).

| Artefacto | Ubicación |
|-----------|-----------|
| **EA** | `Model` → **Analisis de paquetes CU** (packageID **11**) → diagrama **IDENTIFICAR PAQUETES - Casos de Uso** (diagramID **27**) |
| **PlantUML (completo C4+C5)** | `docs/diagrams/uml/identificacion-paquetes-casos-uso.puml` |
| **PlantUML (solo Ciclo 4, 3 paquetes)** | `docs/diagrams/uml/identificacion-paquetes-casos-uso-ciclo4.puml` |
| **Paquetes backend (implementación)** | `docs/ai/PACKAGE_DESIGN.md` — D-003 |

---

## Criterio de agrupación

Los paquetes se definen por **módulos funcionales del examen** (sección 2.5 del documento Word), alineados a los ciclos 4 y 5:

| Paquete | Módulo (documento) | Casos de uso |
|---------|-------------------|--------------|
| **Seguimiento y atención del servicio en tiempo real** | §2.5.1 Tiempo real y tracking | CU36, CU39, CU41 |
| **Selección de taller y pagos del servicio** | §2.5.3 Cotizaciones, taller y pagos | CU37, CU38, CU42, CU44 |
| **Continuidad offline y sincronización** | §2.5.2 Offline y sincronización | CU43, CU45 |
| **Analítica operacional y KPIs** | §2.5.4 Analítica y KPIs | CU46 |
| **Administración multi-tenant SaaS** | §2.5.5 Multi-tenant SaaS | CU40 |

---

## Ciclo 4 — subconjunto (diagrama general 4.1.5)

Para el **diagrama general de casos de uso** solo se modelan en detalle los CU del Ciclo 4. Agrupación mínima (3 paquetes, estilo plantilla académica):

| Paquete | CU |
|---------|-----|
| Seguimiento y atención en tiempo real | CU36, CU39 |
| Selección de taller y pagos | CU37, CU38 |
| Administración multi-tenant SaaS | CU40 |

---

## Notación del diagrama (como plantilla académica)

| Elemento | Notación UML |
|----------|----------------|
| Módulo funcional | Símbolo **Package** |
| Descripción | **Note** (comentario) |
| Enlace paquete → nota | **Dependency** (línea **discontinua** con flecha) |

---

## 4.2.2 — Relacionar paquete con caso de uso (`<<trace>>`)

Un **diagrama por paquete** (estilo plantilla académica): paquete a la izquierda, óvalos CU a la derecha, flechas discontinuas **`<<trace>>`** del paquete hacia cada CU.

| # | Paquete | Casos de uso | EA (package 11) | PlantUML |
|---|---------|--------------|-----------------|----------|
| 1 | Seguimiento y atención en tiempo real | CU36, CU39, CU41 | diagramID **28** | `rel-pkg01-seguimiento-trace.puml` |
| 2 | Selección de taller y pagos | CU37, CU38, CU42, CU44 | diagramID **31** | `rel-pkg02-taller-pagos-trace.puml` |
| 3 | Continuidad offline y sincronización | CU43, CU45 | diagramID **29** | `rel-pkg03-offline-trace.puml` |
| 4 | Analítica operacional y KPIs | CU46 | diagramID **30** | `rel-pkg04-kpis-trace.puml` |
| 5 | Administración multi-tenant SaaS | CU40 | diagramID **32** | `rel-pkg05-saas-trace.puml` |

**Notación:** `Dependency` + estereotipo **`trace`** (no `Association`). En EA: línea **Direct** si se ven dobleces.

**Elementos CU Ciclo 5** creados en paquete 11: IDs **184–189** (CU41–CU46). CU36–CU40 reutilizan elementos del paquete Ciclo 4 (7).

**Conectores trace (EA):** **361–371** (`Dependency` + `<<trace>>`).

---

## 4.2.1.3 — Vista de paquetes / Encapsular paquete

Un **diagrama por paquete** (plantilla académica): el **Package** actúa como contenedor; los **CU** van **dentro**; los **actores** en los bordes; líneas **rectas** del actor al CU (`Association` sólida); relaciones entre CU del mismo paquete solo si aplican (`Dependency` + `<<extend>>` / `<<include>>`).

| # | Paquete | Casos de uso | Actores en el diagrama | EA (package 11) | PlantUML |
|---|---------|--------------|------------------------|-----------------|----------|
| 1 | Seguimiento y atención en tiempo real | CU36, CU39, CU41 | Cliente, Técnico, Taller | **34** `VISTA-PKG01` | `vista-pkg01-seguimiento-encapsular.puml` |
| 2 | Selección de taller y pagos | CU37, CU38, CU42, CU44 | Cliente, Taller | **33** `VISTA-PKG02` | `vista-pkg02-taller-pagos-encapsular.puml` |
| 3 | Continuidad offline y sincronización | CU43, CU45 | Cliente | **37** `VISTA-PKG03` | `vista-pkg03-offline-encapsular.puml` |
| 4 | Analítica operacional y KPIs | CU46 | Administrador, Taller | **35** `VISTA-PKG04` | `vista-pkg04-kpis-encapsular.puml` |
| 5 | Administración multi-tenant SaaS | CU40 | Administrador | **36** `VISTA-PKG05` | `vista-pkg05-saas-encapsular.puml` |

**Relaciones `<<extend>>` dentro del paquete (vista):**

| Diagrama | Relación | Justificación breve |
|----------|----------|---------------------|
| VISTA-PKG01 | CU36 → CU39 | Consulta de ubicación opcional respecto a actualizar estado del servicio |
| VISTA-PKG03 | CU43 → CU45 | Envío al recuperar conexión extiende el registro offline |

**Conectores vista (EA, creados 2026-05-28):** asociaciones **372–387**; extend **375**, **382**.

**Revisión manual en EA:** si una flecha se ve doblada o como `Association` entre CU, clic derecho → **Line Style → Direct**; entre CU debe ser `Dependency` con estereotipo, no `Association`.

---

## 4.2.4 — Analizar paquete (diagrama general de paquetes)

Un **solo diagrama** con el **sistema como paquete contenedor** y los **cinco módulos funcionales** dentro, unidos por **`Dependency`** (flecha discontinua), como la plantilla *Ventanilla Única Mail* (Trámite → Organismo → Reportes).

| Artefacto | EA (package 11) | PlantUML |
|-----------|-----------------|----------|
| Diagrama general | diagramID **38** — `DIAGRAMA GENERAL DE PAQUETES` | `diagrama-general-paquetes-analizar.puml` |
| Paquete contenedor | elementID **191** — Plataforma Inteligente… | (dentro del `.puml`) |
| Dependencias PKG↔PKG | conectores **388–392** | ver `ANALIZAR_PAQUETE_4_2_4.md` |

**Documentación de defensa:** `docs/puds/analisis/ANALIZAR_PAQUETE_4_2_4.md`

---

## Siguiente paso PUDS (4.2)

1. ~~Relacionar paquetes y casos de uso (`<<trace>>`)~~ — diagramas **28–32**.  
2. ~~Vista de paquetes / encapsular~~ — diagramas **33–37**.  
3. ~~Analizar paquete (diagrama general)~~ — diagrama **38**.  
4. Trazabilidad → `TRACEABILITY_MATRIX.md` (CU → paquete → módulo backend).
