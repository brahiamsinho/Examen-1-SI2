# ARCHITECTURE.md
# =========================================================
# Arquitectura del Sistema — Ciclo 1
# =========================================================

## Patrón Arquitectónico

**Arquitectura Modular por Dominio** (Domain-driven Modular Architecture).

Cada módulo encapsula sus propios:
- `models.py` — entidades SQLAlchemy
- `schemas.py` — contratos Pydantic (request/response)
- `service.py` — lógica de negocio (pura, testeable)
- `router.py` — endpoints FastAPI (solo recibe y delega)

## Árbol de módulos Backend

```
app/
├── core/              ← Transversal a todos los módulos
│   ├── config.py      ← Settings desde variables de entorno
│   ├── database.py    ← Engine + sesión asíncrona
│   ├── security.py    ← bcrypt + JWT
│   └── dependencies.py ← get_current_user, require_permission
├── modules/
│   ├── acceso/        ← Auth, roles, permisos, sesiones
│   ├── usuarios/      ← CRUD usuarios + clientes
│   ├── vehiculos/     ← Catálogos + vehículos
│   ├── talleres/      ← Talleres, técnicos, especialidades
│   ├── portal_cliente/← API móvil/portal cliente (registro, perfil, vehículos)
│   ├── portal_taller/ ← Portal responsable de taller (mi-taller, técnicos)
│   ├── portal_taller_emergencias/ ← Ciclo 3 taller: bandeja, disponibilidad, asignación técnico, historial atenciones, comisiones
│   ├── portal_tecnico_emergencias/ ← Ciclo 3 fase 3: servicios, ubicación, estado, mensajes (técnico)
│   └── bitacora/      ← Auditoría (solo lectura desde API)
└── main.py            ← Registro de routers + CORS
```

## App móvil Flutter (`mobile/lib/`)

Módulos por actor (misma idea de capas: application / data / domain / presentation):

```
lib/cliente/     ← Cliente: auth portal, vehículos, perfil; Dio + tokens en ApiClient
lib/tecnico/     ← Técnico/responsable: auth, home, perfil, placeholders; tokens en TecnicoApiClient
lib/core/        ← app_env (.env), api_constants, theme, api_error compartido
```

El **go_router** vive en `cliente/presentation/router/cliente_go_router.dart` y concentra rutas `/splash`, `/cliente/*`, `/tecnico/*`.

## Capas del sistema

```
Angular/Flutter
     ↓ JWT Bearer
FastAPI Router         ← solo valida request y delega
     ↓
FastAPI Service        ← lógica de negocio aquí
     ↓
SQLAlchemy Models      ← mapeo a PostgreSQL
     ↓
PostgreSQL             ← tablas + índices + ENUMs
```

## Esquema y migraciones (Docker)

En desarrollo con `docker-compose`, el contenedor Postgres ejecuta los SQL de `backend/migrations/` en orden (`init`, `0002`–`0004`, `0006` como `05_`, ver `docker-compose.yml`). Scripts adicionales en `scripts/` pueden aplicarse a mano en otros entornos; el modelo **debe** coincidir con la BD (ej. `solicitudes_emergencia.tecnico_asignado_at` alineado con `emergencias/models.py`). Volúmenes ya creados no re-ejecutan init: parches idempotentes (`0006`) o `ALTER` manual. Ver `DECISIONS_LOG` **DEC-009**.

## Patrón de auditoría

La función `registrar_accion()` en `bitacora/service.py`
es el único punto de escritura a la bitácora.
Todos los servicios la llaman después de cada operación exitosa.

## Autenticación

JWT con dos tokens:
- `access_token`: corta duración (60 min), para llamadas a la API
- `refresh_token`: larga duración (7 días), con JTI rastreable en BD
- `sesiones`: tabla en BD que permite revocar tokens individualmente

## Principios aplicados

- **No hardcodear**: todo vía variables de entorno
- **Soft delete**: usuarios se desactivan, no se eliminan
- **Async by default**: SQLAlchemy asyncio + asyncpg
- **Separación de responsabilidades**: router ≠ service ≠ model
