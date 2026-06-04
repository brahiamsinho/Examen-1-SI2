# 4.2.4 — Analizar paquete (diagrama general de paquetes)

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares  
**Artefacto PUDS:** Análisis de dependencias entre **paquetes funcionales** (módulos de casos de uso).

| Artefacto | Ubicación |
|-----------|-----------|
| **EA** | `Model` → **Analisis de paquetes CU** (package **11**) → **DIAGRAMA GENERAL DE PAQUETES** (diagramID **38**) |
| **PlantUML** | `docs/diagrams/uml/paquetes-cu/diagrama-general-paquetes-analizar.puml` |
| **Paquetes identificados (4.2.1)** | `IDENTIFICACION_PAQUETES_CU.md` |

---

## Qué pide esta sección (nivel 0)

A diferencia de **4.2.1.3** (encapsular: actores + CU dentro de un paquete), aquí se **analiza cómo se relacionan los paquetes entre sí**:

| Elemento | Significado |
|----------|-------------|
| **Paquete contenedor** | El sistema completo (como “Ventanilla Única Mail” en la plantilla) |
| **Sub-paquetes** | Los módulos funcionales (§2.5 del examen) |
| **Dependency** (flecha discontinua) | El paquete **origen** **usa / depende de** el paquete **destino** |

**Regla UML:** flecha **A → B** = “A depende de B” (A necesita elementos o comportamiento de B).

---

## Estructura del diagrama (como plantilla académica)

```
┌─ Plataforma Inteligente de Atención de Emergencias Vehiculares ─────────┐
│  [Administración SaaS]     [Continuidad offline]                        │
│                                                                         │
│       [Selección taller y pagos] ──► [Seguimiento tiempo real]         │
│                    │                         │                          │
│                    └──────────► [SaaS]       └──────────► [SaaS]        │
│                                            │                            │
│                                            ▼                            │
│                              [Analítica operacional y KPIs]             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Dependencias modeladas

| Origen (depende) | Destino (provee) | Justificación |
|------------------|------------------|---------------|
| Continuidad offline y sincronización | Selección de taller y pagos | Tras registrar/sincronizar la emergencia (CU43/CU45), el cliente entra al flujo de taller, cotización y pago (CU37–CU44). |
| Selección de taller y pagos | Seguimiento y atención en tiempo real | Una vez elegido taller y avanzado el servicio comercial, tiene sentido el seguimiento en mapa, estado y notificaciones (CU36, CU39, CU41). |
| Seguimiento y atención en tiempo real | Analítica operacional y KPIs | Los KPIs (CU46) consumen datos de estados del servicio, tiempos y operación en curso. |
| Selección de taller y pagos | Administración multi-tenant SaaS | Talleres, tenants y configuración SaaS (CU40) son precondición del catálogo de talleres y pagos por organización. |
| Seguimiento y atención en tiempo real | Administración multi-tenant SaaS | El seguimiento y las notificaciones operan en el **contexto del tenant** activo. |

**Flujo principal (cadena):** Offline → Taller/Pagos → Seguimiento → Analítica  
**Transversal:** Taller/Pagos y Seguimiento → SaaS

---

## Elementos en Enterprise Architect

| Elemento | elementID |
|----------|-----------|
| Contenedor sistema | **191** |
| PKG Seguimiento | **174** |
| PKG Taller y pagos | **175** |
| PKG Offline | **176** |
| PKG Analítica | **177** |
| PKG SaaS | **178** |

**Conectores entre paquetes (EA):** **388–392**

---

## Cómo defenderlo en oral

1. “Identifiqué cinco paquetes por módulo del documento de requisitos (§2.5).”  
2. “El diagrama general muestra **dependencias de análisis**, no herencia ni composición de código.”  
3. “La cadena refleja el **orden lógico del negocio**: emergencia (offline) → taller/pago → seguimiento → métricas.”  
4. “SaaS es **transversal**: sin tenant no hay talleres ni servicios aislados por organización.”

---

## Revisión en EA

1. Abrir diagrama **38** — `DIAGRAMA GENERAL DE PAQUETES`.  
2. Verificar que los cinco sub-paquetes queden **dentro** del contenedor **191**.  
3. Flechas **discontinuas** (`Dependency`); si se doblan: **Line Style → Direct**.  
4. **Ctrl+S** en `.eapx` y exportar PNG para el Word (sección 4.2.4).
