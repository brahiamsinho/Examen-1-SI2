# 4.1.5 — Estructurar el Modelo de Caso de Uso (Ciclo 4)

**Fuente oficial:** `CICLO4_DETALLE_CASOS_USO.md` — matriz **CU36–CU40**

| Artefacto | Ubicación |
|-----------|-----------|
| **EA (canónico)** | `Model` → `Ciclo 4 - Seguimiento tiempo real` → **DIAGRAMA GENERAL DE CASOS DE USO** (diagramID **26**) |
| **PlantUML** | `docs/diagrams/uml/usecases/diagrama-general-casos-uso.puml` |

## Matriz Ciclo 4

| ID | Caso de uso | Actor |
|----|-------------|-------|
| CU36 | Consultar ubicación del técnico en tiempo real | Cliente |
| CU37 | Seleccionar taller para realizar el servicio | Cliente |
| CU38 | Procesar pago mediante pasarela | Cliente |
| CU39 | Actualizar estado de atención del servicio | Técnico / Mecánico |
| CU40 | Gestionar tenant o red de talleres | Administrador |

## Actores del diagrama general

| Actor | Casos de uso asociados |
|-------|------------------------|
| **Cliente** | CU36, CU37, CU38 |
| **Técnico** | CU39 |
| **Administrador** | CU40 |

## Relaciones estructurales (`include` / `extend`)

**Notación UML 2.5:** relación **Dependency** (dependencia) con estereotipo `«include»` o `«extend»`, línea **discontinua**. **No** usar **Association** entre dos casos de uso. Ver `docs/diagrams/agent-memory/USE_CASE_INCLUDE_EXTEND_GUIDE.md`.

| Tipo | Desde | Hacia | Justificación (documento) |
|------|-------|-------|---------------------------|
| **«include»** | CU37 | CU2 | Precondición: CU2 Iniciar sesión (cliente) |
| **«include»** | CU39 | CU2 | Precondición: CU2 Iniciar sesión (técnico) |
| **«include»** | CU40 | CU2 | Precondición: CU2 Iniciar sesión (admin) |
| **«extend»** | CU36 | CU39 | Seguimiento GPS durante atención activa del técnico |
| **«extend»** | CU38 | CU39 | Post CU39: presupuesto disponible para CU38 |

**EA (diagrama 26):** conectores **346–355** — asociaciones actor→CU; **`Dependency`** + `include`/`extend` entre CUs. Líneas en estilo **Direct** (rectas).

## Diagramas individuales (detalle académico)

Cada CU tiene su diagrama de caso de uso en EA (diagramas **13–17**) y PlantUML en `docs/diagrams/uml/usecases/ciclo4/`.

## Obsoleto

- Diagrama EA **25** (paquete 10) — usaba CU genéricos (CU4, CU11, etc.), **no** corresponde al Ciclo 4.
