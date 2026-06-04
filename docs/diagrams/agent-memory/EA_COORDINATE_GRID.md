# Grilla de coordenadas — Despliegue Azure UML (diagramID 9)

**Objetivo:** layout reproducible en EA con **una flecha por relación**, sin efecto “escoba”, flechas ortogonales que no se crucen.

**Diagrama canónico:** `Despliegue Azure UML` — **diagramID 9** (anidamiento visible).

**No usar** diagramID **10** `(final)` — el MCP crea el canvas sin mostrar nodos hijos (solo cubo Azure vacío).

---

## 1. Columnas (eje X)

| Columna | ID | x | width | Contenido |
|---------|----|---|-------|-----------|
| A — Clientes | 44, 45, 53, 54 | 48 | 112 | Web, Móvil + artefactos |
| B — Red | 46 | 228 | 92 | Internet |
| C — Servidor | 102, 103, 50, 51, 52, 55–57 | 355–628 | 310 | Azure VM anidado |
| D — Externos | 48, 49 | 720 | 100 | Stripe, FCM |

Regla: **mínimo 60 px** entre columnas (borde derecho → borde izquierdo).

---

## 2. Filas (eje Y)

| Fila | y | height | Elementos |
|------|---|--------|-----------|
| Web | 88 | 83 | 44 + artefacto 53 |
| Internet (centro) | 178 | 64 | 46 |
| Móvil | 248 | 83 | 45 + artefacto 54 |
| Azure VM (contenedor) | 50 | 340 | 102 |
| Capa aplicación | 95 | 200 | 103 |
| Frontend / Backend (horizontal) | 118 | 70 | 50, 51 lado a lado |
| Base de datos | 310 | 68 | 52 + artefacto 57 |
| Stripe | 145 | 48 | 48 |
| Firebase FCM | 285 | 48 | 49 |

---

## 3. Anidamiento dentro de Capa aplicacion (horizontal)

EA **apila mal** Frontend/Backend en vertical cuando comparten padre. Usar **layout horizontal**:

| Elemento | x | y | w | h |
|----------|---|---|---|---|
| Capa aplicacion (103) | 378 | 95 | 250 | 200 |
| Frontend (50) | 388 | 118 | 108 | 70 |
| Backend (51) | 508 | 118 | 108 | 70 |
| nginx + Angular (55) | 396 | 155 | 92 | 22 |
| FastAPI uvicorn (56) | 516 | 155 | 92 | 22 |

Gap FE↔BE: **12 px** (388+108=496, Backend empieza 508).

---

## 4. Artefactos en dispositivos

| Artefacto | Padre | x | y | w | h |
|-----------|-------|---|---|---|---|
| Navegador Angular (53) | Web | 58 | 144 | 90 | 37 |
| Aplicacion movil (54) | Móvil | 58 | 304 | 90 | 37 |
| PostgreSQL 15 (57) | Base de datos | 388 | 336 | 195 | 28 |

Regla: artefacto **dentro** del cubo padre (y > padre.y + 40).

---

## 5. Conectores (7 CommunicationPath — sin duplicar)

| ID | Origen | Destino | Etiqueta | Notas |
|----|--------|---------|----------|-------|
| 160 | Web (44) | Internet (46) | HTTPS | |
| 161 | Móvil (45) | Internet (46) | HTTPS | |
| 168 | Internet (46) | Capa aplicacion (103) | HTTPS :80 / :8000 | **Una sola** entrada (no 2 a FE/BE) |
| 164 | Frontend (50) | Backend (51) | REST/HTTP | Horizontal |
| 165 | Backend (51) | Base de datos (52) | PostgreSQL | Vertical |
| 166 | Backend (51) | Stripe (48) | HTTPS API | Salida superior |
| 167 | Backend (51) | Firebase FCM (49) | HTTPS | Salida inferior |

### Anti-escoba (obligatorio)

1. Antes de crear conectores: `get_current_diagram` → listar connectorIDs.
2. `delete_connectors_or_messages` por IDs duplicados del mismo par origen→destino.
3. **Nunca** recrear el mismo par sin borrar el anterior.
4. Tras colocar nodos: `layout_connectors` (diagramID 9).
5. Estilo: `OrthogonalRounded` en todos.

---

## 6. Elemento obsoleto (47)

`OBSOLETO Azure VM (logico)` — duplicado del **102**. Sobró de intentos MCP anteriores.

- **Diagrama 9:** canónico. Quitar **47** (`OBSOLETO Azure VM (logico)`) esquina superior-izquierda → **Delete from Diagram**.
- **Diagrama 10:** obsoleto (no muestra Capa/FE/BE/BD en canvas).

---

## 7. Comandos MCP (orden recomendado)

```
1. place_elements_on_diagram  (grilla §2–§4)
2. delete_connectors_or_messages  (duplicados)
3. create_or_update_connectors  (solo los 7 de §5)
4. layout_connectors
5. get_diagram_image  (verificar)
```

---

## 8. Ajuste manual fino (EA UI)

Si alguna flecha aún cruza:

1. **Diagram → Layout Diagram**
2. Arrastrar **waypoint** de la flecha (clic en línea → punto azul)
3. **View → Zoom → Fit in Window**

Referencia Sparx: [Deployment Diagram Tutorial](https://www.sparxsystems.com/resources/tutorials/uml2/deployment-diagram.html) — nodos contenedores + paths etiquetados.
