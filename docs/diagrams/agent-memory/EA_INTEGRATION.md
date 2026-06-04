# EA_INTEGRATION — Enterprise Architect + MCP

Última actualización: **2026-05-28** (regla Model Wizard obligatoria)

## ⚠️ Antes de cualquier creación en EA

1. Abrir **Model Wizard** (`Ctrl+Shift+M`) y revisar patrón en pestaña **Diagram** o **Model Patterns**.
2. Leer la descripción del patrón (panel derecho) y la guía Sparx del tipo de diagrama.
3. Runbook del proyecto: **`EA_MODEL_WIZARD_WORKFLOW.md`**.

**No** usar solo `create_or_update_elements` vía MCP sin haber pasado por Wizard/docs cuando exista patrón UML equivalente (evita lifelines genéricos y diagramas duplicados).

## Servidor MCP

- **Nombre en Cursor:** `user-Enterprise Architect`
- **Ejecutable:** `MCP3.exe` (instalado con el add-in MCP de Sparx, dentro de la carpeta de EA)
- **Documentación oficial:** [Sparx MCP Server](https://www.sparxsystems.jp/en/MCP/)

## ⚠️ Edición en EA: NO viene activada por defecto

Sparx expone **dos grupos de tools**:

| Grupo | Estado por defecto | Ejemplos |
|-------|-------------------|----------|
| **Lectura / interacción** | ✅ Habilitado | `get_root_packages`, `get_diagram_image`, `open_diagrams`, `find_elements_by_name` |
| **Creación / modificación** | ❌ **Deshabilitado** | `create_or_update_elements`, `create_or_update_diagram`, `place_elements_on_diagram`, `create_or_update_attributes`, `create_or_update_connectors`, … |

Para **editar el modelo desde Cursor/IA** hay que lanzar `MCP3.exe` con el argumento **`-enableEdit`**.

Sin eso, el agente solo ve las ~19 tools de lectura (como en nuestro primer intento con timeout). **No es que EA no pueda editar por MCP; es que tu config probablemente no tiene `-enableEdit`.**

### Configuración Cursor (EA Trial 15 x86 — entorno actual)

En **Settings → MCP → Edit Config** (o `~/.cursor/mcp.json` global), el bloque debe verse así:

```json
{
  "mcpServers": {
    "Enterprise Architect": {
      "command": "C:\\Program Files (x86)\\Sparx Systems\\EA Trial\\MCP_Server\\MCP3.exe",
      "args": ["-enableEdit", "-setTimeout", "30"]
    }
  }
}
```

Opcional si EA va lento:

```json
"args": ["-enableEdit", "-setTimeout", "30"]
```

(Timeout entre 3 y 600 segundos; default 3 s.)

**Antes de activar edición:** hacer **backup del `.eapx`**. Sparx lo recomienda explícitamente.

### Tras activar `-enableEdit`

En Cursor deberían aparecer tools adicionales, por ejemplo:

- **Diagramas:** `create_or_update_diagram`, `place_elements_on_diagram`, `layout_connectors`
- **Elementos:** `create_or_update_elements`, `create_or_update_attributes`, `create_or_update_operations`
- **Conectores:** `create_or_update_connectors`, `create_or_update_messages`
- **Paquetes:** `create_or_update_package`, `clone_package`

Usar el prompt MCP **`UML_creation_rules`** (en Cursor: prompts del servidor EA) para tipos exactos al crear clases (`Class`, etc.).

## Pre-requisitos en Windows

1. Enterprise Architect instalado + **add-in MCP** (MSI Sparx: `MCP_EA_x64.msi`).
2. **.NET Desktop Runtime 9.0.5+**
3. Proyecto del curso **abierto** en EA (solo una instancia con proyecto; el MCP se engancha a la primera).
4. Reiniciar Cursor tras cambiar `args`.

## Flujo recomendado: diagrama de clases Login **directo en EA**

Cuando `-enableEdit` está activo, el agente puede:

1. `get_current_package` o `find_packages_by_name` → paquete destino (ej. Acceso).
2. `create_or_update_diagram` → diagrama UML Class «Login».
3. `create_or_update_elements` → `Usuario`, `Sesion`, `Rol`, `Tenant`, … (tipos UML correctos).
4. `create_or_update_attributes` / `create_or_update_connectors` → atributos y asociaciones.
5. `place_elements_on_diagram` → colocar en el diagrama.
6. `reload_diagrams` → refrescar vista.

**PlantUML en Git** sigue siendo útil como respaldo alineado al código; no excluye modelar en EA vía MCP.

## Flujo triple (repo + EA + draw.io)

```
Código real  →  validación nombres
       ↓
PlantUML (.puml) en docs/diagrams/     ← Git / agentes
       ↓
EA MCP (-enableEdit)                   ← entrega académica .eapx
       ↓
draw.io (opcional)                     ← presentación
```

## Reset del modelo EA

MCP **no puede** borrar diagramas, elementos ni paquetes. Ver `EA_CLEAN_RESET.md`.

| Tool MCP | Borrado |
|----------|---------|
| `delete_connectors_or_messages` | ✅ Solo conectores |
| `delete_diagram` / `delete_package` | ❌ No existe |

## Registro de IDs — ARCHIVADO (pre-reset 2026-05-28)

Inventario antes de vaciar EA. Tras **Delete Package** los IDs ya no son válidos.

<details>
<summary>D-010 Login (paquete 3, diagramID 2)</summary>

Elementos 6–17, asociaciones y dependencias. Runbook: `EA_LOGIN_CLASS_RUNBOOK.md`.
</details>

<details>
<summary>D-006 Despliegue (paquete 4, diagramID 9 canónico)</summary>

Elementos 44–57, 102–103; conectores 160–161, 164–168. Layout: `ea-templates/layouts/despliegue-azure-d006.layout.json`.
</details>

## Si MCP falla

| Síntoma | Causa probable |
|---------|----------------|
| Timeout | EA cerrado o `-setTimeout` muy bajo |
| Solo tools `get_*` | Falta **`-enableEdit`** en `args` |
| No crea en diagrama | Versión reciente: crear elementos y luego `place_elements_on_diagram` (comportamiento Sparx 2.x) |

Registrar en `LEARNINGS.md`.

## Qué NO esperar

- Borrado de diagramas, paquetes o elementos (solo conectores vía `delete_connectors_or_messages`).
- Import/export XML del paquete (solo usuario en EA; agente usa `.layout.json`).
- Control de z-order / Bring to Front (manual en EA).
- HTTP MCP (solo STDIO; EULA EA).
- Sincronización automática PlantUML ↔ EA sin intervención del agente.
