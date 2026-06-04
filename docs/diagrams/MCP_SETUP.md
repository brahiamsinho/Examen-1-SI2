# MCP — draw.io y Enterprise Architect en Cursor

## draw.io (este repo)

El proyecto incluye **`.cursor/mcp.json`** con el servidor oficial:

```json
{
  "mcpServers": {
    "drawio": {
      "command": "npx",
      "args": ["-y", "@drawio/mcp"]
    }
  }
}
```

### Activar

1. Instalar [Node.js](https://nodejs.org/) (LTS).
2. **Importante:** Cursor muestra en *Settings → Tools & MCP → User MCP Servers* lo de **`~/.cursor/mcp.json`** (global), no solo el del repo.
3. Añadir `drawio` en **`%USERPROFILE%\.cursor\mcp.json`** (o **New MCP Server** en la UI).
4. El repo también trae **`.cursor/mcp.json`** (project-level) para el equipo al clonar.
5. **Settings → MCP** → Refresh → `drawio` debe aparecer en verde con 3 tools.
6. Si falla en Windows: `"command": "C:\\Program Files\\nodejs\\npx.cmd"`.

### Límite de tools (Cursor)

EA (~35) + MongoDB plugin (~29) superan el límite práctico (~40). Si `drawio` no responde, desactiva temporalmente un plugin MCP pesado o usa solo `drawio` + EA.

### Alternativa sin npx (MCP Apps)

En configuración global `~/.cursor/mcp.json` puedes añadir (ver `.cursor/mcp.example.json`):

```json
"drawio-remote-app": {
  "url": "https://mcp.draw.io/mcp"
}
```

Útil para previews inline; depende del host MCP Apps.

### Paquetes npm relacionados

| Paquete | Uso |
|---------|-----|
| `@drawio/mcp` | **Oficial** — abre editor, Mermaid/CSV/XML |
| `drawio-mcp` | Otro paquete (API mxGraph); **no** es el configurado por defecto aquí |

## Enterprise Architect (edición vía MCP)

EA en Cursor: **`user-Enterprise Architect`** → ejecutable **`MCP3.exe`** (add-in Sparx).

### Lectura vs edición

| Modo | `args` en MCP3.exe | Tools |
|------|-------------------|-------|
| Default Sparx | `[""]` | Solo `get_*`, `open_diagrams`, `find_*`, … |
| **Crear/editar en EA** | `["-enableEdit"]` | + `create_or_update_elements`, `create_or_update_diagram`, `place_elements_on_diagram`, atributos, conectores, … |

FAQ oficial: *"I cannot create/modify models"* → activar **`-enableEdit`**.  
Doc: [sparxsystems.jp/en/MCP](https://www.sparxsystems.jp/en/MCP/)

```json
"Enterprise Architect": {
  "command": "C:\\Program Files\\Sparx Systems\\EA\\MCP_Server\\MCP3.exe",
  "args": ["-enableEdit", "-setTimeout", "30"]
}
```

**Backup del `.eapx` antes de dejar que la IA modifique el modelo.**

### Uso

1. Instalar `MCP_EA_x64.msi` + .NET Desktop Runtime 9.0.5+.
2. Abrir EA con tu proyecto.
3. Cursor MCP en verde; comprobar que aparecen tools `create_or_update_*`.
4. Usar prompt MCP **`UML_creation_rules`** al crear clases.

Detalle: `docs/diagrams/agent-memory/EA_INTEGRATION.md`.

Si timeout → subir `-setTimeout`. Si solo lectura → falta `-enableEdit`.

## Usar ambos con el subagente

```
@.cursor/agents/diagrams-modeling.md
Abre el contexto C4 en draw.io desde drawio/mermaid/01-context-c4.mmd
y contrasta paquetes con EA si está conectado.
```

Flujo: `docs/diagrams/agent-memory/DRAWIO_INTEGRATION.md`.

## Referencias

- [draw.io MCP GitHub](https://github.com/jgraph/drawio-mcp)
- [draw.io AI docs](https://www.drawio.com/blog/drawio-mcp-server)
- [Sparx EA MCP](https://www.sparxsystems.jp/en/MCP/)
