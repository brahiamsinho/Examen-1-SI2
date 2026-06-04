# Runbook — Secuencia Login en EA (estilo académico BCE)

**Referencia visual:** diagrama `sd CU2 Gestionar categoria` (Boundary / Control / Entity + fragmentos `alt`).

**Fuente Git canónica:** `docs/diagrams/uml/sequence-auth-login-bce.puml`  
**Implementación real:** `AuthRouter` + `AuthService` → `POST /api/auth/login`

---

## Diagrama canónico EA (BCE)

| Artefacto | ID |
|-----------|-----|
| Paquete `Acceso y autenticacion` | **6** |
| Diagrama **`sd Login - Iniciar sesion`** | **12** ← usar este |
| Diagrama antiguo (tecnológico) | 11 — archivar o borrar del canvas |

### Lifelines (iconos BCE)

| Rol académico | Elemento EA | ID | Equivalente código |
|---------------|-------------|-----|-------------------|
| Actor | Usuario | 105 | Cliente / técnico / taller / admin |
| Boundary | V.Login | 112 | Pantalla login Flutter o Angular |
| Control | AuthController | 113 | `auth/router.py` + `auth/service.py` |
| Entity | M.Usuario | 114 | `usuarios` ORM |
| Entity | M.Sesion | 115 | `sesiones` ORM |
| Entity | M.Tenant | 116 | `tenants` ORM (SaaS) |

---

## Mapeo respecto al ejemplo CU2

| Ejemplo categorías | Login emergencias |
|--------------------|-------------------|
| Administrador | Usuario |
| V.index / V.Crear / V.Modificar | **V.Login** |
| CategoriaController | **AuthController** |
| M.Categoria | **M.Usuario**, **M.Sesion**, **M.Tenant** |
| alt Listar / crear / modificar / eliminar | alt **login exitoso** / **credenciales inválidas** / **cuenta pendiente** |

### Flujo `alt login exitoso` (como `alt crear`)

| Paso | De → A | Mensaje |
|------|--------|---------|
| 1 | Usuario → AuthController | `login()` |
| 2 | AuthController → V.Login | `show()` |
| 3 | V.Login → AuthController | `store(email, password [, slug])` |
| 4 | AuthController → M.Usuario | `get()` |
| 5 | M.Usuario → AuthController | `return()` |
| 6 | AuthController → M.Tenant | `get(slug)` *(opcional)* |
| 7 | M.Tenant → AuthController | `return()` |
| 8 | AuthController → M.Sesion | `create()` |
| 9 | AuthController → AuthController | `create_access_token()` |
| 10 | AuthController → V.Login | `TokenResponse` |
| 11 | V.Login → Usuario | sesión iniciada |

---

## Fragmentos `alt` en EA (manual, 5 min)

El MCP no crea cajas `alt` automáticamente. En diagrama **12**:

1. **Insert → Fragment → Alt** (o Combined Fragment).
2. Crear tres regiones:
   - `alt login exitoso` — mensajes 1–11 arriba.
   - `alt credenciales invalidas` — `store` → `get` → `401` al usuario.
   - `alt cuenta pendiente` — `get` → estado PENDIENTE → `403`.
3. Marco del diagrama: renombrar cabecera a **`sd Login - Iniciar sesion`** (clic en frame `sd`).

---

## Diagrama 11 (legacy)

Contiene lifelines duplicados (Boundary + Object). **No usar para entrega.** Eliminar del Project Browser o ignorar.

---

## Export

`get_diagram_image` diagramID **12** → `docs/diagrams/output/ea/D-011-login-sequence-bce.png`
