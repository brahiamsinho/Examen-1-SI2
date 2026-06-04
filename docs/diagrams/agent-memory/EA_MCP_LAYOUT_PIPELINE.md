# Pipeline híbrido — MCP + layout versionado (+ XML opcional)

**Objetivo:** que el agente cree diagramas en EA vía MCP y **acomode de forma reproducible**, sin depender de prueba y error en cada sesión.

---

## Lo que SÍ puede el agente (MCP)

| Tool | Uso |
|------|-----|
| `create_or_update_elements` | Modelo en Project Browser |
| `create_or_update_connectors` | CommunicationPath (1 por relación) |
| `place_elements_on_diagram` | Coordenadas x,y,width,height |
| `layout_connectors` | Rutas ortogonales |
| `get_current_diagram` / `get_diagram_image` | Verificar |

## Lo que NO puede el agente (MCP Trial 15)

| Acción | Alternativa |
|--------|-------------|
| Importar XML / XMI | Usuario: **Package to XML** / **Import Package** |
| Exportar paquete a XML | Usuario: clic derecho paquete → export |
| Quitar elemento del canvas | Usuario: **Delete from Diagram** |
| Waypoints finos de flechas | Usuario: **Diagram → Layout Diagram** o arrastrar punto azul |
| `import_element_linked_documents` | Solo RTF adjunto a elementos, **no** diagramas |

**Conclusión:** XML real lo exporta/importa **el humano en EA**. El agente usa un **layout JSON** en git como “XML lite”.

---

## Pipeline por diagrama (orden obligatorio)

```
1. Leer layout JSON (si existe) o EA_COORDINATE_GRID.md
2. create_or_update_elements     → jerarquía owningElementID
3. get_current_diagram           → listar connectorIDs existentes
4. delete_connectors_or_messages → borrar duplicados del mismo par
5. create_or_update_connectors   → solo N paths del layout JSON
6. place_elements_on_diagram     → placements del JSON (sin excludeFromDiagram)
7. layout_connectors
8. get_diagram_image             → verificar anidamiento visible
9. Si falla anidamiento: NO crear diagrama nuevo; re-place en diagramID canónico
10. Usuario (una vez): export XML → ea-templates/patterns/
```

---

## Archivos de layout (versionados en git)

| Diagrama | Layout JSON |
|----------|-------------|
| D-006 Despliegue Azure | `ea-templates/layouts/despliegue-azure-d006.layout.json` |
| (futuro) D-010 Login | `ea-templates/layouts/login-class-d010.layout.json` |

Formato: `placements[]`, `connectors[]`, `excludeFromDiagram[]`, `manualSteps[]`.

El agente **lee el JSON y llama MCP** — no edita `.eapx` directamente.

---

## XML del paquete (capa congelada)

Cuando el diagrama se ve bien en EA:

1. Paquete **Despliegue** → **Package to XML**
2. Guardar en `ea-templates/patterns/despliegue-azure-d006.xml`
3. Commit en git

**Cuándo usar XML vs JSON:**

| | Layout JSON | Package XML |
|--|-------------|-------------|
| Quién lo aplica | Agente MCP | Usuario EA |
| Cambios incrementales | ✅ Fácil | ❌ Re-export completo |
| Copia exacta a otro .eapx | ❌ | ✅ |
| Model Wizard | ❌ | ✅ (con MDG) |

Flujo ideal: **MCP + JSON** durante desarrollo → **XML** cuando el diagrama queda listo para entregar.

---

## Reglas anti-regresión

1. **Un diagramID canónico** por artefacto (D-006 = **9**).
2. **No** crear diagrama `(final)` solo para quitar un elemento suelto.
3. Antes de `create_or_update_connectors`: borrar duplicados.
4. FE/BE **horizontal** dentro de Capa aplicacion (y=151, x=385 vs 505).
5. Internet → **Capa aplicacion (103)**, no dos flechas a FE y BE.
6. Elemento **47** nunca se coloca; usuario lo quita del canvas.

---

## Diagramas obsoletos (cerrar en EA)

3, 4, 5, 6, 7, **10** — intentos MCP con layout roto o sin anidamiento visible.
