# PACKAGE_DESIGN.md

Diseño lógico por paquetes — alineado al backend real y a diagramas en `docs/diagrams/`.

Última actualización: **2026-05-28** (C4 4 capas + PUDS)

## Diagrama maestro

| ID | Archivo PlantUML | Descripción |
|----|------------------|-------------|
| D-007 | `docs/diagrams/uml/diseño-logico-arquitectura-mvc.puml` | **PUDS 4.3.1.2** — MVC Vista / Controlador / Modelo (informe académico) |
| D-008 | `docs/diagrams/uml/componente-principal-sistema.puml` | **Componente principal** — hub FastAPI + módulos + capas internas |
| D-003 | `docs/diagrams/uml/packages-backend-logical.puml` | Paquetes `app.modules.*` y dependencias (detalle implementación) |

Render: ver `docs/diagrams/README.md`.

## Paquetes backend (`app/modules/`)

| Paquete | Responsabilidad | Routers / prefijos notables |
|---------|-----------------|-----------------------------|
| `acceso_y_administracion` | Auth, RBAC, usuarios, bitácora, tenants SaaS, billing Stripe, finanzas admin | `/api/auth`, `/api/admin/tenants`, `/api/admin/finanzas` |
| `clientes_y_vehiculos` | Perfil cliente, vehículos, catálogos | `/api/app/cliente`, `/api/vehiculos` |
| `talleres_y_tecnicos` | Talleres, técnicos, app técnico | `/api/talleres`, `/api/app/tecnico` |
| `incidentes.emergencias` | Solicitudes emergencia (cliente) | `/api/app/cliente/emergencias` |
| `atencion.taller_emergencias` | Bandeja, asignación, comisiones taller | `/api/app/taller/emergencias` |
| `comunicacion_y_notificaciones` | Push FCM, chat, notificaciones | bajo `/api/app/cliente`, `/api/app/tecnico` |
| `pagos_y_comisiones` | Pagos y comisiones | pagos emergencia |
| `ai` | Proxy/enriquecimiento IA | `/api/ai`, enrich en emergencias |

Transversal: `app/core` (config, DB, JWT, tenant middleware).

## Capas por módulo (patrón)

```
router.py   → HTTP, validación, Depends
service.py  → reglas de negocio
models.py   → SQLAlchemy
schemas.py  → Pydantic
```

## Frontend y móvil (referencia)

| Capa | Ubicación | Diagrama C4 |
|------|-----------|-------------|
| Admin Angular | `frontend/src/app/admin/` | `docs/diagrams/c4/02-containers.puml` |
| Taller Angular | `frontend/src/app/taller/` | idem |
| Flutter cliente/técnico | `mobile/lib/cliente`, `mobile/lib/tecnico` | idem |

## Trazabilidad diagrama ↔ flujo

| Flujo | Diagrama secuencia | API principal |
|-------|-------------------|---------------|
| Alta emergencia cliente | `uml/sequence-emergencia-alta-cliente.puml` | `POST /api/app/cliente/emergencias` |
| Login (email + password, tenant) | `uml/sequence-auth-login.puml` | `POST /api/auth/login`, header `X-Tenant-Slug` |
| Contexto sistema | `c4/01-context.puml` | — |
| Contenedores lógicos | `c4/02-containers.puml` | Docker Compose |
| Componentes API | `c4/03-components-backend.puml` | `app/modules/*` |
| Code CU11 | `c4/04-code-emergencias-alta.puml` | emergencias service |
| Despliegue académico | `uml/deployment-docker-azure.puml` | UML 2.5+ (no C4) |

Ver también **`PUDS_GUIDE.md`**.

## Multi-tenancy (SaaS)

- Columna `tenant_id` en entidades operativas.
- Resolución: `X-Tenant-Slug`, subdominio, JWT.
- Superadmin: `ADMIN` + `tenant_id IS NULL`.

Ver `ARCHITECTURE.md` y migraciones `0015`–`0017`.

## Próximos diagramas sugeridos

1. ~~`c4/03-components-backend.puml`~~ — **hecho** (2026-05-28).  
2. ~~`c4/04-code-emergencias-alta.puml`~~ — **hecho** (CU11).  
3. Secuencia login tenant + secuencia pago/comisión.

Coordinar matriz RF/CU con agente **`puds`** (`TRACEABILITY_MATRIX.md`).
