# Runbook — Diagrama de clases Login en EA (MCP)

**ID:** D-010-EA | Fuente: `uml/class-auth-login.puml` + `auth/`

Ejecutar **solo** con EA abierto, proyecto cargado, MCP en verde y tools `create_or_update_*` visibles.

## 0. Pre-check

```text
get_root_packages          → debe responder (no timeout)
get_current_package        → anotar packageID destino (ej. Acceso)
```

Si timeout: EA cerrado, `-setTimeout` bajo, o MCP3.exe no arranca. Ver `MCP_SETUP.md`.

## 1. Paquete (si no existe)

Tool: `create_or_update_package`

```json
{
  "packageInfo": {
    "packageID": 0,
    "name": "Acceso y autenticacion",
    "owningPackageID": "<ROOT_PACKAGE_ID>"
  }
}
```

O usar `find_packages_by_name` con "Acceso" y reutilizar `packageID` existente.

## 2. Diagrama de clases

Tool: `create_or_update_diagram`

```json
{
  "diagramInfo": {
    "diagramID": 0,
    "name": "Login - diagrama de clases",
    "type": "Class",
    "description": "POST /api/auth/login. D-010. Generado desde class-auth-login.puml",
    "owningPackageID": "<PACKAGE_ID>",
    "owningElementID": 0
  }
}
```

Guardar `diagramID` devuelto → `<DIAGRAM_ID>`.

## 3. Clases (lote)

Tool: `create_or_update_elements`

Tipos UML estándar EA: `Class`, `Enumeration`.

| name | type | notas |
|------|------|-------|
| LoginRequest | Class | DTO |
| TokenResponse | Class | DTO |
| AuthRouter | Class | stereotype router opcional |
| AuthService | Class | |
| Usuario | Class | tabla usuarios |
| Sesion | Class | tabla sesiones |
| Rol | Class | |
| UsuarioRol | Class | |
| Tenant | Class | |
| EstadoUsuarioEnum | Enumeration | |
| EstadoSesionEnum | Enumeration | |
| SecurityUtils | Class | utility |

Ejemplo (repetir por clase o en array):

```json
{
  "elementInfo": [
    {
      "elementID": 0,
      "name": "Usuario",
      "type": "Class",
      "description": "ORM usuarios - auth login",
      "owningPackageID": "<PACKAGE_ID>",
      "owningElementID": 0
    },
    {
      "elementID": 0,
      "name": "Sesion",
      "type": "Class",
      "owningPackageID": "<PACKAGE_ID>",
      "owningElementID": 0
    }
  ]
}
```

Anotar cada `elementID` devuelto.

## 4. Atributos clave

Tool: `create_or_update_attributes` por elemento.

**Usuario:** id:int, email:String, password_hash:String, estado:EstadoUsuarioEnum, tenant_id:int (Public +)

**Sesion:** id:int, usuario_id:int, token_jti:String, estado:EstadoSesionEnum

**LoginRequest:** email:String, password:String

**TokenResponse:** access_token, refresh_token, token_type, expires_in

**Tenant:** id, slug, nombre

## 5. Asociaciones

Tool: `create_or_update_connectors`

| source | target | type | multiplicidad |
|--------|--------|------|---------------|
| Usuario | Sesion | Association | 1 → 0..* |
| Usuario | Tenant | Association | * → 0..1 |
| Usuario | UsuarioRol | Association | 1 → * |
| UsuarioRol | Rol | Association | * → 1 |
| Usuario | EstadoUsuarioEnum | Dependency | |
| Sesion | EstadoSesionEnum | Dependency | |

Ejemplo:

```json
{
  "connectorInfo": [{
    "connectorID": 0,
    "type": "Association",
    "sourceEnd": { "relatedElementID": "<Usuario_ID>", "multiplicity": "1" },
    "targetEnd": { "relatedElementID": "<Sesion_ID>", "multiplicity": "0..*" }
  }]
}
```

Dependencias diseño (AuthService → Usuario, etc.): `type`: `Dependency` o `Usage`.

## 6. Colocar en diagrama

Tool: `place_elements_on_diagram`

Grid sugerido (x, y, width 140, height 80):

| Elemento | x | y |
|----------|---|---|
| LoginRequest | 40 | 40 |
| TokenResponse | 40 | 180 |
| AuthRouter | 40 | 320 |
| AuthService | 280 | 180 |
| Usuario | 520 | 40 |
| Sesion | 720 | 40 |
| Tenant | 520 | 200 |
| Rol | 520 | 340 |
| UsuarioRol | 680 | 340 |
| SecurityUtils | 280 | 340 |
| EstadoUsuarioEnum | 900 | 40 |
| EstadoSesionEnum | 900 | 140 |

```json
{
  "diagramID": "<DIAGRAM_ID>",
  "placements": [
    { "elementID": "<Usuario_ID>", "x": 520, "y": 40, "width": 160, "height": 100 }
  ]
}
```

## 7. Verificar

- `open_diagrams` con `<DIAGRAM_ID>`
- `get_diagram_image` → guardar en `docs/diagrams/output/ea/D-010-login-class.png`
- Actualizar `EA_INTEGRATION.md` tabla de IDs
- Actualizar `CURRENT_STATE.md` fila D-010-EA

## Prompt MCP

Antes del chat, adjuntar prompt **UML_creation_rules** del servidor Enterprise Architect.
