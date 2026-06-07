# EA — Diagrama de arquitectura del sistema

Guía del diagrama de **componentes** que replica la vista “Sistema” (hub FastAPI, módulos de dominio, capas internas, infraestructura).

## Ubicación en Enterprise Architect

| Artefacto | ID | Ruta |
|-----------|-----|------|
| Paquete | **28** | `Model → Arquitectura` |
| Diagrama | **31** | `component Arquitectura del sistema` (tipo **Component**) |
| Diagrama | **32** | `component Acceso capas por dominio` (4 columnas Web→API→Service→Repo→SQL) |

## Diagrama 32 — Acceso por capas (réplica slide académico)

Vista **4×4 + PostgreSQL**: Auth, Usuarios, Roles/Permisos, Bitácora.

| Capa | Col 1 Auth | Col 2 Users | Col 3 Roles | Col 4 Bitácora |
|------|------------|-------------|-------------|----------------|
| Web | `web/LoginPage` (198) | `web/UsersPage` (202) | `web/RolesPermisosPage` (206) | `web/BitacoraPage` (210) |
| API | `api/auth/router.py` (199) | `api/users/router.py` (203) | `api/roles_permisos/router.py` (207) | `api/bitacora/router.py` (211) |
| Service | `service/AuthService` (200) | `service/UsuarioService` (204) | `service/RolPermisoService` (208) | `service/BitacoraService` (212) |
| Repository | `repository/SesionRepo` (201) | `repository/UsuarioRepo` (205) | `repository/RolPermisoRepo` (209) | `repository/BitacoraRepo` (213) |

**BD compartida:** `PostgreSQL acceso` (214) — tablas: usuarios, roles, permisos, usuario_rol, rol_permiso, sesiones, bitácora.

Conectores verticales por columna (390–405); los cuatro repos → BD con etiqueta **SQL**.

### Trazabilidad código real

| Componente EA | Implementación actual |
|---------------|----------------------|
| `web/LoginPage` | `frontend/.../admin-login` |
| `web/UsersPage` | `admin-usuarios` → `/admin/panel/usuarios` |
| `web/RolesPermisosPage` | `admin-roles` + `admin-permisos` (dos pantallas; un router lógico en el slide) |
| `web/BitacoraPage` | `admin-bitacora` |
| `api/*` | `backend/app/modules/acceso_y_administracion/{auth,usuarios,roles,permisos,bitacora}/router.py` |
| `service/*` | `.../service.py` correspondiente |
| `repository/*` | **Capa de diseño:** no hay archivos `*Repo.py`; el acceso ORM vive en `service.py` + `models.py`. El diagrama muestra la separación lógica que el curso pide. |

**Nota:** `api/users/router.py` en el slide = carpeta `usuarios/` en el repo. Roles y permisos son **dos** routers (`roles/`, `permisos/`), agrupados en un solo bloque API del diagrama.

### Colores (manual en EA)

El slide usa azul/verde/amarillo/rojo/morado por fila. EA no los asignó por MCP: en EA selecciona cada fila y aplica **Default Fill** o estereotipo `«layer»` si tu plantilla lo trae.

## Diagramas por paquete funcional (pkg IDENTIFICAR PAQUETES)

Mismo patrón **4 capas × N columnas (un CU por columna) + PostgreSQL**. Tecnología backend: **FastAPI** (`router.py` → `service.py` → ORM). Web = **Flutter** (cliente/técnico) o **Angular** (admin/taller).

| Paquete funcional (nota EA) | Diagrama EA (ID) | Columnas (sin prefijo CU en nombres) |
|-----------------------------|------------------|--------------------------------------|
| Seguimiento y atención en tiempo real | `component PKG Seguimiento tiempo real` (**33**) | Seguimiento ubicación · Actualizar estado · Notificaciones FCM |
| Selección de taller y pagos | `component PKG Seleccion taller y pagos` (**36**) | Selección taller · Pago pasarela · Presupuesto · ETA |
| Continuidad offline y sincronización | `component PKG Offline sincronizacion` (**37**) | Registrar offline · Sync pendientes *(diseño; cola local aún parcial)* |
| Analítica operacional y KPIs | `component PKG Analitica KPIs` (**35**) | Dashboard admin · Reportes taller |
| Administración multi-tenant SaaS | `component PKG Multi-tenant SaaS` (**34**) | Gestionar tenant *(API pendiente en repo)* |

**Convención de nombres en diagramas de paquete:** solo capa + rol (`mobile/…`, `api/…/router.py`, `service/…`, `repository/…`). Los casos de uso viven en el diagrama de paquetes / notas EA, no en el título del componente.

### Flujo por columna (defensa oral)

1. **Presentación** (`web/` o `mobile/`) — pantalla Angular/Flutter.  
2. **API** — `router.py` FastAPI, valida JWT y permisos, delega.  
3. **Service** — reglas de negocio (async, `AsyncSession`).  
4. **Repository** — capa lógica de persistencia (en código suele ser `service` + `models.py`; en **pagos** sí existe `repository.py`).  
5. **SQL** → PostgreSQL.

### Ejemplo trazabilidad (PKG 1, columna seguimiento ubicación)

| Capa | Componente EA | Código |
|------|---------------|--------|
| mobile | `mobile/SeguimientoUbicacion` | `mobile/.../emergencia_seguimiento_screen.dart` |
| API | `api/emergencias/router.py` | `incidentes/emergencias/router.py` |
| Service | `service/SeguimientoService` | `emergencias/service/` |
| Repo | `repository/SolicitudRepo` | `emergencias/models.py` + queries en service |

## Correspondencia con el código (`docs/ai/ARCHITECTURE.md`)

### Clientes (izquierda)

| Componente EA | elementID | Repo |
|---------------|-----------|------|
| App Flutter Cliente | 175 | `mobile/lib/cliente/` |
| App Flutter Tecnico | 176 | `mobile/lib/tecnico/` |
| Frontend Angular Admin | 177 | `frontend/src/app/admin/` |

Conectores **Dependency** `REST JWT` → **Backend API FastAPI** (174).

### Hub central

| Componente | elementID | Repo |
|------------|-----------|------|
| Backend API FastAPI | 174 | `backend/app/main.py` + registro de routers |

### Módulos funcionales (columna izquierda → API)

Cada módulo usa conector **Assembly** `expone` hacia 174.

| Componente EA | elementID | Carpeta backend |
|---------------|-----------|-----------------|
| Modulo Acceso Roles Permisos | 178 | `modules/acceso_y_administracion/` (auth, roles, permisos, bitácora) |
| Modulo Usuarios | 179 | `usuarios`, clientes admin |
| Modulo Vehiculos | 180 | `clientes_y_vehiculos/vehiculos` |
| Modulo Incidentes | 181 | `incidentes/emergencias` |
| Modulo Talleres y Tecnicos | 182 | `talleres_y_tecnicos/` |
| Modulo Inteligencia Incidente | 183 | `ai/` |
| Modulo Priorizacion Asignacion | 184 | `ai/assignment` |
| Modulo Atencion Solicitudes | 185 | `atencion/taller_emergencias` |
| Modulo Finanzas Pagos | 186 | `pagos_y_comisiones` / `admin_finanzas` |
| Modulo Notificaciones | 187 | `comunicacion_y_notificaciones/` |
| Modulo Historial Trazabilidad | 188 | bitácora + historial de estado solicitud |

### Transversales (arriba)

| Componente | elementID | Notas |
|------------|-----------|-------|
| Autenticacion JWT Session | 190 | `core/security.py`, tabla `sesiones` |
| HTTP y WebSockets | 191 | REST + comunicaciones en tiempo real |

### Capas internas (derecha)

| Componente | elementID | Patrón por módulo |
|------------|-----------|-------------------|
| Core transversal | 189 | `core/config`, `database`, `dependencies` |
| Capas Router Service Model | 192 | `router.py` → `service.py` → `models.py` + `schemas.py` + `migrations/` |

**Backend** → **Capas** (`estructura interna`); **Capas** → **PostgreSQL** (`persiste`).

### Infraestructura (abajo)

| Componente | elementID | Repo / servicio |
|------------|-----------|-----------------|
| PostgreSQL | 193 | Docker `db`, SQL en `backend/migrations/` |
| Almacenamiento Medios | 194 | `StaticFiles`, `uploads/evidencias` |
| Servicios Externos | 195 | Stripe, FCM, geocoding |
| AI Inference Worker | 196 | `services/ai-inference` (perfil Compose `ai`) |

## Conectores principales (IDs 366–389)

- Clientes → API: **Dependency**
- Módulos → API: **Assembly** `expone`
- Auth / HTTP → API: **Dependency** `usa`
- API → Core, Capas, PostgreSQL, medios, externos, AI: **Dependency**

## Diferencias respecto al diagrama de referencia (imagen)

1. **Colores / particiones:** EA usa tipo `Component` estándar; los colores del slide son decorativos. Opcional: estereotipos o notas por zona.
2. **Capas detalladas:** En la imagen aparecen Routers, Schemas, Repositories, Signals, Tasks por separado; aquí se agruparon en **Capas Router Service Model** para legibilidad (el repo no usa capa Repository explícita en todos los módulos).
3. **Gestionar tenant:** no hay componente dedicado; el CU30 de análisis de clases es diseño futuro.
4. **Portal taller Angular:** no está como cliente separado; la funcionalidad taller vive en `frontend` bajo rutas `/taller/panel/…` (se puede añadir un cuarto componente si el profesor lo pide).

## Cómo defenderlo (PUDS)

- **Análisis:** actores y casos de uso en otros paquetes EA.
- **Diseño lógico:** este diagrama = **diagrama de componentes** del sistema.
- **Implementación:** trazabilidad módulo EA → carpeta `backend/app/modules/…`.
- **Despliegue:** complementar con diagrama Deployment (Docker Compose: `backend`, `db`, `ai-inference`, `frontend`).

## Mantenimiento

Al renombrar o mover paquetes en el backend, actualizar la **description** del componente en EA (MCP `create_or_update_elements` con `elementID` ≠ 0). No cambiar `type` de elementos existentes.
