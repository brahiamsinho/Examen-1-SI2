# DRAWIO_INTEGRATION — draw.io MCP + flujo con EA y PlantUML

Última actualización: **2026-05-28**

## Servidor MCP en este repo

| Clave | Tipo | Config |
|-------|------|--------|
| `drawio` | Tool server (stdio) | `.cursor/mcp.json` → `npx -y @drawio/mcp` |
| `drawio-remote-app` | Hosted (opcional) | `https://mcp.draw.io/mcp` — previews inline en hosts MCP Apps |

**Requisitos:** Node.js 18+, `npx` en PATH. Tras editar `.cursor/mcp.json`, recargar MCP en Cursor (Settings → MCP → refresh).

## Qué hace el MCP oficial (`@drawio/mcp`)

- Abre diagramas en **app.diagrams.net** (navegador) desde el agente.
- Entrada soportada: **draw.io XML**, **CSV**, **Mermaid**.
- No sustituye PlantUML en Git; complementa edición visual y entregables `.drawio`.

Documentación: [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp), npm `@drawio/mcp`.

## Roles de cada herramienta (no mezclar fuentes de verdad)

| Herramienta | Rol | Fuente de verdad |
|-------------|-----|------------------|
| **PlantUML** (`.puml`) | Versionado Git, CI, ASCII, PUDS académico | ✅ Sí |
| **Enterprise Architect** (`.eapx`) | Modelo UML oficial del curso / defensa | ✅ Sí (entrega EA) |
| **draw.io** (`.drawio`) | Presentación, ajuste visual, export PNG/SVG/PDF | Derivado; guardar en `docs/diagrams/drawio/` |
| **Mermaid** en `drawio/mermaid/` | Puente hacia draw.io MCP | Derivado de `.puml`; no duplicar sin sync |

## Flujo integrado EA + draw.io + PlantUML

```
                    ┌─────────────────┐
                    │  Código +       │
                    │  docs/ai/       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  PlantUML (.puml)     EA MCP (lectura)    Mermaid puente
  docs/diagrams/       Sparx EA abierto    drawio/mermaid/
         │                   │                   │
         │                   │ export PNG        │
         │                   ▼                   ▼
         │              output/ea/          MCP drawio
         │              referencia          abre editor
         └───────────────────┴───────────────────┘
                             │
                             ▼
              Guardar .drawio en docs/diagrams/drawio/
              Actualizar CURRENT_STATE + PACKAGE_DESIGN
```

### Pasos recomendados por el agente

1. **Definir** en PlantUML (`.puml`) con nombres del código.
2. **Validar** con EA MCP (`get_packages_information`, `find_elements_by_name`) si EA está abierto.
3. **Derivar** Mermaid en `drawio/mermaid/<id>-<nombre>.mmd` (mismo ID que `CURRENT_STATE.md`).
4. **Invocar** MCP `user-drawio` → **`deployment-docker-azure-uml.mmd`** para despliegue (UML 2.5 obligatorio).
5. **Usuario** guarda desde draw.io → **File → Export as → `.drawio`** en `docs/diagrams/drawio/`.
6. **Registrar** ruta en `CURRENT_STATE.md` y trazabilidad en `PACKAGE_DESIGN.md`.

## Sincronización EA ↔ draw.io

| Dirección | Método práctico |
|-----------|-----------------|
| EA → draw.io | MCP `get_diagram_image` → PNG en `output/ea/`; redibujar en draw.io usando la imagen de referencia **o** export manual desde EA (imagen/SVG si el curso lo permite). |
| draw.io → EA | No hay import directo fiable UML completo; **recrear** paquetes/clases en EA siguiendo nombres de `RULES.md`. |
| PlantUML → draw.io | Copiar semántica a `drawio/mermaid/*.mmd` → MCP draw.io. |
| draw.io → PlantUML | Solo si el usuario pide convergencia; actualizar `.puml` manualmente (draw.io export XML no es PlantUML). |

**Regla:** el modelo **UML formal para nota** sigue en **EA**; **Git** sigue con **PlantUML**; **draw.io** es capa de **comunicación visual** editable.

## Carpetas

```
docs/diagrams/drawio/          ← archivos .drawio versionados
docs/diagrams/drawio/mermaid/  ← fuentes Mermaid para MCP
docs/diagrams/output/drawio/   ← PNG/SVG exportados (gitignore)
```

## Límites conocidos

- URLs muy largas pueden fallar al abrir diagramas enormes vía MCP → dividir diagramas (ver `LEARNINGS.md`).
- MCP draw.io requiere red para `app.diagrams.net`.
- Sin Node/npx → usar hosted `https://mcp.draw.io/mcp` si el host lo soporta.

## Checklist conexión draw.io

- [x] Node.js instalado (`v22.22.0` verificado 2026-05-28)
- [x] `.cursor/mcp.json` presente en el repo
- [x] `@drawio/mcp` arranca por stdio (`npx -y @drawio/mcp` → OK)
- [ ] Cursor MCP: servidor **`drawio` en verde** (falló verificación agente 2026-05-28 — no expone tools)
- [ ] Probar: agente llama `open_drawio_mermaid` con `01-context-c4.mmd`

### Verificación 2026-05-28

| Prueba | Resultado |
|--------|-----------|
| Tools `open_drawio_mermaid` / `open_drawio_xml` / `open_drawio_csv` en Cursor | ❌ No disponibles (servidor no conectado al agente) |
| Paquete npm `@drawio/mcp` | ✅ OK |
| Archivos Mermaid en repo | ✅ 4 archivos listos |

**Causa probable:** MCP `drawio` no cargado en Cursor (refresh pendiente) o `npx` en Windows (`.cursor/mcp.json` usa `npx.cmd`).

**Tras activar:** el tool devuelve una **URL** a `app.diagrams.net` con el diagrama editable.

### Archivos Mermaid listos para probar

| ID | Archivo |
|----|---------|
| D-001 | `drawio/mermaid/01-context-c4.mmd` |
| D-002 | `drawio/mermaid/02-containers-c4.mmd` |
| D-006 | `drawio/mermaid/deployment-docker-azure.mmd` |
| D-010 | `drawio/mermaid/class-auth-login.mmd` |

### Alternativa sin npm local

Añadir en MCP global o proyecto:

```json
"drawio-remote-app": {
  "url": "https://mcp.draw.io/mcp"
}
```

Hosted en `mcp.draw.io` — soporta XML inline; Mermaid/CSV vía tool server local.
