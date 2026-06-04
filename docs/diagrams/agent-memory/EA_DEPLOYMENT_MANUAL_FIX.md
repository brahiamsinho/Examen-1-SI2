# Arreglo manual — Despliegue Azure UML (3–5 min)

**Diagrama:** `Despliegue Azure UML` (diagramID **9**) — **no** el renombrado `OBSOLETO no usar (final)`.

---

## 1. Abrir el diagrama correcto

Project Browser → **Despliegue** → **Despliegue Azure UML** (sin “OBSOLETO”).

**View → Zoom → Fit in Window**

---

## 2. Quitar basura

| Elemento | Acción |
|----------|--------|
| `OBSOLETO Azure VM (logico)` (esquina) | Seleccionar → **Delete** → **Delete from Diagram** |

---

## 3. Si el cubo Azure tapa todo (solo ves REST/HTTP y PostgreSQL)

El padre se dibujó **encima** de los hijos. En EA:

1. **Ctrl+clic** en el canvas: selecciona **Capa aplicacion**, **Frontend**, **Backend**, **Base de datos** (sin el Azure VM grande).
2. Menú **Format → Bring to Front** (o clic derecho → Order → Bring to Front).
3. Clic en **Azure VM Docker Host** → **Format → Send to Back**.

Si aún no ves Frontend/Backend:

1. Project Browser → expandir **Azure VM Docker Host → Capa aplicacion**.
2. Arrastrar **Frontend** y **Backend** al canvas **dentro** del recuadro de Capa aplicacion.
3. Igual con **Base de datos** debajo de Capa.

---

## 4. Artefactos dentro de nodos

Arrastrar desde el browser (no sueltos en el canvas):

- **Navegador Angular** → dentro de **Web**
- **Aplicacion movil** → dentro de **Dispositivo movil**
- **nginx + Angular SPA** → dentro de **Frontend**
- **FastAPI uvicorn** → dentro de **Backend**
- **PostgreSQL 15** → dentro de **Base de datos**

---

## 5. Flechas

**Diagram → Layout Diagram**

Si una flecha cruza: clic en la línea → arrastrar el **punto azul** (waypoint).

---

## 6. Congelar (opcional, para no repetir)

Cuando quede bien:

Clic derecho paquete **Despliegue** → **Package to XML** →  
`docs/diagrams/ea-templates/patterns/despliegue-azure-d006.xml`

---

## Por qué MCP no alcanza

EA dibuja nodos 3D contenedores; el MCP coloca coordenadas pero **no controla z-order** (qué cubo tapa a cuál). Eso solo lo resuelve bien **Bring to Front / Send to Back** o arrastrar desde el Project Browser — igual que el [tutorial Sparx de deployment](https://www.sparxsystems.com/resources/tutorials/uml2/deployment-diagram.html).
