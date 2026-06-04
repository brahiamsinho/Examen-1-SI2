# Guía — Diagrama de comunicación CU36 en Enterprise Architect

**Caso de uso:** CU36 Consultar ubicación del técnico  
**Draw.io (referencia visual):** `docs/diagrams/CU36-comunicacion-ubicacion-tecnico.drawio`  
**Regla de oro:** topología **lineal MVC**, no estrella.

---

## Lo que OpenCode te dijo (y es correcto)

### 1. Topología lineal, no estrella

| Enfoque | Cómo se ve | ¿Usar en CU36? |
|---------|------------|----------------|
| **Estrella (error anterior)** | Controlador en el centro con líneas al Actor, varias vistas y entidades a la vez | **No** — confunde el flujo MVC |
| **Lineal (tu Draw.io)** | `Actor → Vista → Controlador → Entidades` en fila, de izquierda a derecha | **Sí** — es la posta |

En MVC robusto (BCE):

- El **Actor** solo habla con la **Vista** (boundary).
- La **Vista** delega al **Controlador** (control).
- El **Controlador** consulta **Entidades** (entity).
- **No** conectes `Cliente — SeguimientoController` directo si tu Draw.io no lo tiene.

### 2. Mensajes superpuestos en EA ≠ error tuyo

Enterprise Architect apila varios mensajes **Collaboration** sobre la **misma** línea **Association**. Draw.io dibuja una flecha por mensaje a distinta altura; EA dibuja una línea con textos encimados.

**Solución:** seleccionar la etiqueta del mensaje y **arrastrarla** un poco arriba o abajo (perpendicular a la línea). Repetir para cada mensaje del mismo enlace.

### 3. Orden de trabajo en EA (manual, sin MCP)

1. **Association** primero (líneas estructurales sin flechas de mensaje).
2. **Add Message** / **Collaboration** sobre cada Association.
3. Separar etiquetas a mano.
4. **F5** o *Layout selected connectors* si moviste objetos.

---

## Paquetes EA en este repo

| Paquete | Uso |
|---------|-----|
| `CU36_Comunicacion_Limpio` | Versión simplificada (OpenCode sugiere armar aquí a mano) |
| `CU36_Comunicacion_Recuperado` | Diagrama wizard expandido (ID **22**) |
| `/Model/Comunicacion` | **Diagrama oficial:** **40** `comm CU36 lineal MVC flujo principal` |

Si el MCP de EA no está disponible, seguí los pasos de abajo en el paquete que uses (recomendado: **Limpio** o un diagrama nuevo en **Comunicacion**).

---

## Layout lineal (calcado al Draw.io)

Colocá en **una fila horizontal** (eje X creciente):

```
[Cliente] — [V.Seguimiento] — [SeguimientoController] — [SolicitudEmergencia arriba]
                                                      \— [Tecnico abajo]
```

**Notas del Draw.io (solo texto, no íconos extra obligatorios):**

- `V.UbicacionTecnico` y `V.Error` aparecen como **etiquetas** bajo la zona de `V.Seguimiento` (no hace falta un segundo boundary con línea propia si querés el diagrama más simple).
- Las líneas horizontales del Draw.io (`line-hub-boundary`, `line-boundary-control`) son el “carril” de mensajes: Actor–Vista–Control en la misma banda Y.

**Association (solo estas, en el flujo lineal):**

| # | Enlace |
|---|--------|
| A1 | Cliente → V.Seguimiento |
| A2 | V.Seguimiento → SeguimientoController |
| A3 | SeguimientoController → SolicitudEmergencia |
| A4 | SeguimientoController → Tecnico |
| A5 | SolicitudEmergencia — Tecnico (relación de dominio, línea sin mensajes o solo estructural) |

**No uses** (salvo que tu curso lo exija explícitamente):

- Cliente → SeguimientoController directo  
- V.UbicacionTecnico como nodo separado con Association al controlador (eso fue un atajo del MCP, no tu Draw.io)

---

## Mensajes por enlace (tabla maestra)

Alineado a tu Draw.io + instrucciones OpenCode. En EA: clic derecho en la Association → **Add Message**.

| Enlace | Mensaje | Dirección en EA |
|--------|---------|-----------------|
| Cliente → V.Seguimiento | `1.AbrirSeguimiento()` | ida |
| Cliente → V.Seguimiento | `1.1 VerUbicacionTecnico()` | ida — **arrastrar** etiqueta arriba |
| Cliente → V.Seguimiento | `1.6 Reintentar()` | ida — **arrastrar** etiqueta abajo |
| V.Seguimiento → SeguimientoController | `1.2 ConsultarUbicacion()` | ida |
| V.Seguimiento → SeguimientoController | `1.5 viewMapa()` | **retorno** (Control → Vista) |
| SeguimientoController (self) o → Solicitud | `1.2b ValidarSolicitud()` | ida / lazo en el control |
| SeguimientoController → SolicitudEmergencia | `1.3 getUbicacionTecnico()` | ida |
| SolicitudEmergencia → SeguimientoController | `1.4 return()` | **retorno** |
| SeguimientoController → zona Vista | `2.1` / `2.2` / `2.3` (opcional) | retorno hacia boundary — **solo si modelás excepciones** |

**Flujo principal sin errores:** omití `1.6`, `2.1`, `2.2`, `2.3` y la etiqueta `V.Error`.

**Detalle importante (Draw.io vs OpenCode):** en tu XML, la flecha `1.3` apunta al ícono **SolicitudEmergencia** (arriba a la derecha), no al ícono Tecnico. El API `GET .../ubicacion-tecnico` lee datos de la solicitud/GPS; en EA poné `1.3` en el enlace **Controlador → SolicitudEmergencia**. OpenCode lo puso en Control–Tecnico por simplificar; para defensa académica, **priorizá el Draw.io**.

---

## Checklist antes de entregar

- [ ] Fila lineal: Actor → Vista → Control → Entidades (sin estrella).
- [ ] Sin enlace directo Actor–Controlador.
- [ ] Cada mensaje sobre una Association que ya existe.
- [ ] Etiquetas del mismo enlace **separadas** a mano (no tapadas).
- [ ] `return()` y `viewMapa()` con **dirección de retorno** donde corresponda.
- [ ] Nombres visibles bajo cada ícono BCE.

---

## Errores que ya cometimos en sesiones anteriores (aprendé de esto)

1. **Topología estrella** con controlador en el centro y Actor cableado al control.  
2. **Segundo boundary** `V.UbicacionTecnico` con Association al controlador (no está así en Draw.io).  
3. **Ocultar todas las Association** y dejar solo Collaboration — a veces ayuda visualmente, pero al editar a mano conviene ver primero el esqueleto lineal.  
4. Pensar que “faltan flechas” cuando en realidad hay **tres textos en el mismo pixel**.

---

## Diagramas EA CU36 (2026-05-30)

| diagramID | Nombre | Uso |
|-----------|--------|-----|
| **40** | `comm CU36 lineal MVC flujo principal` | Communication — **3 Association nombradas** por par Cliente–Vista (559–561). Tras MCP: **separar líneas a mano** (ver abajo). |
| **41** | `sd CU36 Consultar ubicacion tecnico secuencia` | Sequence — **cada mensaje con flecha propia** (MCP `create_or_update_messages`). Ideal para revisión legible. |

### Arreglo manual Communication (diagrama 40)

1. Abrí el diagrama **40** en EA (doble clic en el árbol).
2. Entre **Cliente** y **V.Seguimiento** hay **3 líneas** (559, 560, 561): seleccioná cada línea y arrastrá el **segmento** (no solo el texto) a distinta altura: arriba `1.1`, medio `1.Abrir`, abajo `1.6`.
3. Entre **V.Seguimiento** y **Control**: línea superior `1.2` (562), inferior `1.5` (563).
4. **Layout → Diagram → Layout selected connectors** (o F5).

El MCP **no** puede fijar la Y de cada etiqueta en Communication; eso es límite de EA + API.

---

## Draw.io vs EA

| Necesidad | Herramienta |
|-----------|-------------|
| PDF / exposición con mensajes bien espaciados | **Draw.io** (`CU36-comunicacion-ubicacion-tecnico.drawio`) |
| Modelo Communication en EA | Diagrama **40** + ajuste manual de líneas |
| Mensajes sin solapar en EA | Diagrama **41** (Sequence) |
| Sin MCP EA | Seguí esta guía a mano en `CU36_Comunicacion_Recuperado` |

---

## Trazabilidad código

- API: `GET /api/app/cliente/emergencias/{id}/ubicacion-tecnico`  
- Flutter: `emergencia_seguimiento_screen.dart`, `emergencia_ubicacion_tecnico_screen.dart`
