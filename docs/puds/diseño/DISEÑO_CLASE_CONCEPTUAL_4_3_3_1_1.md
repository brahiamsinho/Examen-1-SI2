# 4.3.3.1.1 Diagrama de Clase — Diseño conceptual de la base de datos

**Sistema:** Plataforma Inteligente de Atención de Emergencias Vehiculares (SaaS multi-tenant)  
**Artefacto PUDS:** Diseño — **diagrama de clases conceptual** del modelo de datos de dominio.

| Artefacto | Ubicación |
|-----------|-----------|
| **PlantUML (canónico)** | `docs/diagrams/uml/class-database-conceptual.puml` (D-020) |
| **draw.io (editable)** | `docs/diagrams/drawio/d020-diseno-conceptual-bd.drawio` |
| **Mermaid puente MCP** | `docs/diagrams/drawio/mermaid/class-database-conceptual.mmd` |
| **Enterprise Architect** | Paquete **8** `Diseno de Datos Logico` → **9** `Objetos de dominio` → diagrama **24** `DISEÑO CONCEPTUAL DE LA BASE DE DATOS` |
| **Script recreación EA** | `scripts/ea-create-class-database-conceptual.ps1` (EA abierto con .eapx) |

---

## Qué es (nivel 0)

Un **diagrama de clases conceptual** describe **entidades del dominio**, sus **atributos principales** y **relaciones** (asociaciones con multiplicidad y verbos), **sin** detallar tipos SQL, índices ni triggers.

| Elemento UML | En este diagrama |
|--------------|------------------|
| **Clase** | Entidad de negocio / tabla principal |
| **Atributo** | Campo persistente (tipo lógico: int, string, float, datetime) |
| **Asociación** | Línea sólida con verbo en español |
| **Multiplicidad** | `1`, `0..1`, `0..*` en cada extremo |

**Para entender bien esto:** es la vista **4.3.3.1.1** del PUDS; conecta el análisis (actores, CUs) con la implementación ORM en `backend/app/modules/*/models.py`.

---

## Clases y atributos (trazabilidad backend)

Atributos tomados de los modelos SQLAlchemy reales. Se omiten `created_at`, `updated_at` y campos Stripe en Tenant por ser detalle de implementación.

| Clase | Tabla | Modelo backend | Atributos en diagrama |
|-------|-------|----------------|------------------------|
| **Tenant** | `tenants` | `tenants/models.py` | id, slug, nombre, estado, plan |
| **Usuario** | `usuarios` | `usuarios/models.py` | id, email, password_hash, estado, tenant_id |
| **Rol** | `roles` | `roles/models.py` | id, nombre, descripcion |
| **UsuarioRol** | `usuario_rol` | `roles/models.py` | id, usuario_id, rol_id, asignado_at |
| **Cliente** | `clientes` | `clientes/models.py` | id, usuario_id, tenant_id, ciudad, direccion |
| **MarcaVehiculo** | `marcas_vehiculo` | `vehiculos/models.py` | id, nombre |
| **Vehiculo** | `vehiculos` | `vehiculos/models.py` | id, placa, anio, color, tenant_id |
| **Taller** | `talleres` | `talleres/models.py` | id, nombre_comercial, direccion, latitud, longitud, tenant_id, estado |
| **Tecnico** | `tecnicos` | `talleres/models.py` | id, usuario_id, taller_id, estado |
| **SolicitudEmergencia** | `solicitudes_emergencia` | `emergencias/models.py` | id, descripcion_texto, estado, tenant_id |
| **Pago** | `pagos` | `pagos/models.py` | id, monto, moneda, estado, metodo, referencia_externa |
| **Permiso** | `permisos` | `permisos/models.py` | id, codigo, nombre, modulo |
| **RolPermiso** | `rol_permiso` | `roles/models.py` | id, rol_id, permiso_id |
| **ModeloVehiculo** | `modelos_vehiculo` | `vehiculos/models.py` | id, marca_id, nombre |
| **TipoVehiculo** | `tipos_vehiculo` | `vehiculos/models.py` | id, nombre |
| **SolicitudUbicacion** | `solicitud_ubicaciones` | `emergencias/models.py` | id, solicitud_id, latitud, longitud, es_actual |
| **SolicitudEvidencia** | `solicitud_evidencias` | `emergencias/models.py` | id, solicitud_id, tipo, archivo_url |
| **SolicitudHistorialEstado** | `solicitud_historial_estado` | `emergencias/models.py` | id, solicitud_id, estado_anterior, estado_nuevo |
| **ComisionTaller** | `comisiones_taller` | `atencion/taller_emergencias/models.py` | id, solicitud_id, taller_id, monto_comision, estado |
| **Notificacion** | `notificaciones` | `notificaciones/models.py` | id, usuario_id, solicitud_id, tipo, titulo, leida |
| **SolicitudMensaje** | `solicitud_mensajes` | `mensajes_solicitud/models.py` | id, solicitud_id, emisor/receptor_usuario_id, mensaje |
| **UsuarioFcmToken** | `usuario_fcm_tokens` | `dispositivos_push/models.py` | id, usuario_id, token, platform |
| **Sesion** | `sesiones` | `auth/models.py` | id, usuario_id, token_jti, estado, expira_at |
| **Bitacora** | `bitacora` | `bitacora/models.py` | id, usuario_id, modulo, entidad, accion, ip_address |

### Tablas backend omitidas (detalle operativo — opcional en diagrama físico)

| Tabla | Motivo de omisión en conceptual |
|-------|----------------------------------|
| `usuario_tokens_seguridad` | Token opaco email/reset; detalle de auth |
| `especialidades_tecnico` | Catálogo auxiliar del técnico |
| `taller_disponibilidad` | Config operativa del taller (capacidad) |
| `solicitud_taller_bandeja` | Bandeja aceptación/rechazo (CU taller) |
| `solicitud_asignaciones_tecnico` | Historial técnico reasignaciones |

### Notas de modelado (conceptual vs implementación)

1. **Cliente ↔ Usuario (1:0..1):** `Cliente.usuario_id` es FK única; el email/teléfono/documento viven en **Usuario**, no en Cliente.
2. **Tecnico ↔ Usuario (1:0..1):** el nombre del técnico se obtiene de **Usuario** (`nombres`, `apellidos`).
3. **Vehiculo:** se relaciona con **MarcaVehiculo**, **ModeloVehiculo** y **TipoVehiculo** (FKs `marca_id`, `modelo_id`, `tipo_vehiculo_id`).
4. **SolicitudEmergencia — ubicación GPS:** va en **SolicitudUbicacion** (`solicitud_ubicaciones`), no en la cabecera.
5. **RBAC completo:** `Usuario` ↔ `UsuarioRol` ↔ `Rol` ↔ `RolPermiso` ↔ `Permiso`.
6. **Multi-tenant:** `tenant_id` en Usuario, Cliente, Taller, Vehiculo y SolicitudEmergencia refleja RLS y aislamiento SaaS (`migrations/0015`, `0016`).

---

## Relaciones y multiplicidades

| Desde | Multiplicidad | Verbo | Hacia | Multiplicidad | Justificación backend |
|-------|---------------|-------|-------|---------------|------------------------|
| Tenant | 1 | agrupa | Usuario | 0..* | `usuarios.tenant_id` |
| Tenant | 1 | agrupa | Cliente | 0..* | `clientes.tenant_id` |
| Tenant | 1 | agrupa | Taller | 0..* | `talleres.tenant_id` |
| Usuario | 1 | es | Cliente | 0..1 | `clientes.usuario_id` UNIQUE |
| Usuario | 1 | es | Tecnico | 0..1 | `tecnicos.usuario_id` UNIQUE |
| Usuario | 1 | tiene | UsuarioRol | 0..* | tabla pivote M:N |
| Rol | 1 | define | UsuarioRol | 0..* | tabla pivote M:N |
| MarcaVehiculo | 1 | clasifica | Vehiculo | 0..* | `vehiculos.marca_id` |
| Cliente | 1 | posee | Vehiculo | 0..* | `vehiculos.cliente_id` |
| Cliente | 1 | solicita | SolicitudEmergencia | 0..* | `solicitudes_emergencia.cliente_id` |
| Vehiculo | 1 | involucra | SolicitudEmergencia | 0..* | `solicitudes_emergencia.vehiculo_id` |
| Taller | 0..1 | atiende | SolicitudEmergencia | 0..* | `taller_id` nullable hasta asignación |
| Tecnico | 0..1 | asigna | SolicitudEmergencia | 0..* | `tecnico_id` nullable hasta asignación |
| Taller | 1 | emplea | Tecnico | 0..* | `tecnicos.taller_id` |
| SolicitudEmergencia | 1 | genera | Pago | 0..* | `pagos.solicitud_id` |

**Regla UML:** asociaciones **sólidas** con multiplicidad en extremos; **no** usar Dependency entre entidades de dominio.

---

## Enterprise Architect (D-020)

| Artefacto | ID / ruta |
|-----------|-----------|
| Paquete padre | **8** — `Diseno de Datos Logico` |
| Paquete clases | **9** — `Objetos de dominio` |
| Diagrama canónico | **24** — `DISEÑO CONCEPTUAL DE LA BASE DE DATOS` |
| Clases núcleo | **147–157** (Tenant … Pago) |
| Clases ampliadas | **269–281** (Permiso, RolPermiso, ModeloVehiculo, TipoVehiculo, SolicitudUbicacion/Evidencia/HistorialEstado, Notificacion, Bitacora, Sesion, ComisionTaller, SolicitudMensaje, UsuarioFcmToken) |
| Asociaciones | **276–290** (núcleo) + **480–496** (ampliadas) |

**Abrir en EA:** Browser → `Model` → `Diseno de Datos Logico` → `Objetos de dominio` → doble clic en el diagrama **24**.

**Recrear o sincronizar atributos/layout:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/ea-create-class-database-conceptual.ps1
```

(Requiere EA abierto con tu `.eapx`.)

**Revisión manual:** `View → Zoom → Fit in Window`; conectores → **Line Style → Direct**; **Ctrl+S**; export PNG.

---

### PlantUML

```bash
plantuml -tpng -o docs/diagrams/output docs/diagrams/uml/class-database-conceptual.puml
```

### draw.io

1. Abrir `docs/diagrams/drawio/d020-diseno-conceptual-bd.drawio` en [app.diagrams.net](https://app.diagrams.net).
2. **View → Fit Page**; ajustar conectores → **Line Style → Direct**.
3. Export PNG → `docs/diagrams/output/drawio/`.

---

## Cómo defenderlo en oral

1. “Es el **modelo conceptual** de la BD: entidades, atributos clave y cardinalidades.”  
2. “**Tenant** agrupa datos SaaS; cada fila operativa lleva `tenant_id` donde aplica.”  
3. “**Usuario** es identidad central; **Cliente** y **Tecnico** son especializaciones 1:1.”  
4. “**SolicitudEmergencia** es el agregado transaccional: cliente, vehículo, taller y técnico opcionales hasta asignar.”  
5. “Los atributos coinciden con **SQLAlchemy** en `backend/app/modules/`.”

---

## Trazabilidad PUDS

```
Requisitos §2 (datos)
  → Casos de uso CU11–CU16 (emergencias)
  → Paquetes análisis (4.2)
  → Diseño lógico MVC (4.3.1.2)
  → **4.3.3.1.1 Diagrama de clase conceptual (este)**
  → Migraciones backend/migrations/
  → Modelos ORM backend/app/modules/
```
