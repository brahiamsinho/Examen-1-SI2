# Reset EA — dejar `proyecto.eapx` en limpio

**Fecha inventario:** 2026-05-28  
**Proyecto:** `proyecto.eapx` (fuera del repo)  
**Limitación MCP:** no existe `delete_diagram`, `delete_element` ni `delete_package`. Solo el usuario en EA o un script COM puede borrar.

---

## Qué borrar (todo bajo `/Model`)

| packageID | Paquete | Diagramas | Acción |
|-----------|---------|-----------|--------|
| 2 | Starter Sequence Diagram | 1 | Eliminar paquete |
| 3 | Acceso y autenticacion | 2 | Eliminar paquete |
| 4 | Despliegue | 3, 4, 5, 7, 9, 10 | Eliminar paquete |
| 5 | CUP FICCT - Examen SI1 | 6, 8 | Eliminar paquete |

Tras el reset debe quedar solo **`Model`** (packageID **1**) vacío.

---

## Pasos en EA (2–3 min)

1. **File → Save** (backup implícito; opcional copiar `.eapx` antes).
2. Project Browser → expandir **Model**.
3. Por cada paquete hijo (4 paquetes):
   - Clic derecho → **Delete Package** (o **Remove Package**).
   - Confirmar **Delete from Model** (elimina diagramas + elementos del paquete).
4. Cerrar pestañas de diagramas que queden abiertas.
5. Verificar: bajo **Model** no hay subpaquetes ni diagramas.

---

## Qué NO se pierde (sigue en Git)

| Recurso | Ruta |
|---------|------|
| PlantUML D-001…D-010, D-006 | `docs/diagrams/c4/`, `docs/diagrams/uml/` |
| Layout coordenadas D-006 | `docs/diagrams/ea-templates/layouts/despliegue-azure-d006.layout.json` |
| Guías y pipeline MCP | `docs/diagrams/agent-memory/EA_*.md` |
| Mermaid / draw.io | `docs/diagrams/drawio/mermaid/` |

Para **recrear** en EA: MCP + layout JSON + runbooks; o importar XML cuando exista en `ea-templates/patterns/`.

---

## Inventario pre-reset (referencia)

### Diagramas (10 total)

| diagramID | Nombre | Tipo | Paquete |
|-----------|--------|------|---------|
| 1 | Starter Sequence Diagram | Sequence | 2 |
| 2 | Login - diagrama de clases | Class | 3 |
| 3 | OBSOLETO Despliegue Docker Azure | Deployment | 4 |
| 4 | Despliegue Azure produccion | Deployment | 4 |
| 5 | Despliegue Azure | Deployment | 4 |
| 6 | OBSOLETO - no usar | Activity | 5 |
| 7 | Despliegue Azure UML | Deployment | 4 |
| 8 | CUP Admision - Actividad con particiones | Activity | 5 |
| 9 | Despliegue Azure UML | Deployment | 4 |
| 10 | OBSOLETO no usar (final) | Deployment | 4 |

### Elementos clave D-006 (paquete 4, por si se recrea)

Jerarquía browser: `102` Azure VM → `103` Capa → `50` FE, `51` BE; `52` BD; artefactos `53–57`; obsoleto `47`.

Conectores canónicos (modelo): **160, 161, 164–168**.

---

## Próximo arranque limpio en EA

1. Crear paquete nuevo bajo Model (ej. `Examen SI2`).
2. Un diagrama por artefacto; no duplicar diagramIDs.
3. Seguir `EA_MCP_LAYOUT_PIPELINE.md`.
4. Layout manual: `Bring to Front` / `Send to Back` (`EA_DEPLOYMENT_MANUAL_FIX.md`).
5. Export XML solo cuando el diagrama esté listo.
