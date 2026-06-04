# Guía UML 2.5 — `<<include>>` y `<<extend>>` en casos de uso

**Obligatoria** para diagramas generales (4.1.5) y modelado en EA / PlantUML.  
Referencias: UML 2.5 (relaciones de caso de uso), artefacto PUDS análisis.

---

## Tres tipos de relación en diagramas de casos de uso

| Relación | Tipo UML / EA | Línea | Flecha | Etiqueta | Cuándo usarla |
|----------|---------------|-------|--------|----------|----------------|
| **Actor ↔ Caso de uso** | **Association** | **Sólida** | Sin flecha | — | El actor participa en ese CU |
| **`<<include>>`** | **Dependency** | **Discontinua** | De CU base → CU incluido | `«include»` | Comportamiento **obligatorio** reutilizado |
| **`<<extend>>`** | **Dependency** | **Discontinua** | De CU extensión → CU base | `«extend»` | Comportamiento **opcional** en un punto de extensión |

**Regla clave:** entre dos **casos de uso** nunca uses `Association`. Usa **`Dependency`** con estereotipo `include` o `extend` (en EA también existen herramientas Include/Extend que son la misma idea; en defensa académica suele pedirse **Dependencia**).

---

## `<<include>>` (inclusión)

**Significado:** el caso de uso **base** siempre ejecuta el comportamiento del caso de uso **incluido**.

**Dirección de la flecha (UML 2.5):**

```
[CU base] ----«include»----> [CU incluido]
```

**Ejemplo académico (e-commerce):** `CU3 Generar reportes` **include** `CU7 Realizar Venta`.

**Ejemplo Ciclo 4 (este proyecto):**

| Base | Incluido | Por qué |
|------|----------|---------|
| CU37 | CU2 Iniciar sesión | Precondición en `CICLO4_DETALLE_CASOS_USO.md` |
| CU39 | CU2 Iniciar sesión | Técnico autenticado |
| CU40 | CU2 Iniciar sesión | Admin autenticado |

---

## `<<extend>>` (extensión)

**Significado:** el caso de uso **extensión** añade comportamiento **opcional** al **base**.

**Dirección de la flecha (UML 2.5):**

```
[CU extensión] ----«extend»----> [CU base]
```

**Ejemplo Ciclo 4:**

| Extensión | Base | Por qué |
|-----------|------|---------|
| CU36 | CU39 | Seguimiento GPS durante atención activa |
| CU38 | CU39 | Pago tras presupuesto en CU39 |

---

## Cómo dibujarlo

### PlantUML (Git)

```plantuml
Cliente --> CU37          ' Association (sólida)

CU37 ..> CU2 : <<include>>   ' Dependency (discontinua)
CU38 ..> CU39 : <<extend>>
```

### Enterprise Architect (MCP)

Tool: `create_or_update_connectors`

| Campo | Valor |
|-------|--------|
| `type` | **`Dependency`** (no `Association`) |
| `stereotypes` | **`include`** o **`extend`** |
| `direction` | `FromSourceToTarget` |
| `sourceEnd.relatedElementID` | Origen de la flecha (ver tablas) |
| `targetEnd.relatedElementID` | Destino de la flecha |

**Verificación:** `get_current_diagram` debe mostrar `"type":"Dependency"` y `"stereotypes":"include"` o `"extend"` entre CUs.

**Manual en EA:** Toolbox → **Dependency** → estereotipo `include` / `extend` en propiedades del conector.

**Líneas rectas (sin dobleces):** en EA, seleccionar conector → menú contextual → **Line Style** → **Direct** (o `Ctrl+Shift+4`). Evitar *Orthogonal* / *Rounded*. Tras MCP, si quedan dobleces: borrar conector en el diagrama y redibujar con estilo Direct.

---

## Checklist antes de cerrar diagrama general

- [ ] Actor → CU: **Association** (sólida, sin flecha)
- [ ] CU → CU: **Dependency** + `«include»` o `«extend»` (discontinua)
- [ ] Nunca **Association** entre dos casos de uso
- [ ] Dirección include: base → incluido
- [ ] Dirección extend: extensión → base

---

## Diagrama canónico Ciclo 4

| Artefacto | Ubicación |
|-----------|-----------|
| EA | Paquete **7**, diagramID **26** |
| PlantUML | `docs/diagrams/uml/usecases/diagrama-general-casos-uso.puml` |
| PUDS | `docs/puds/casos-uso/MODELO_GENERAL_CASOS_USO.md` |

Conectores EA (IDs **341–345**): Dependency + `include` (CU37, CU39, CU40 → CU2); Dependency + `extend` (CU36, CU38 → CU39).
