# Sesión 2026-06-05 — CRUD técnicos y clientes en portal taller

## Objetivo

Permitir al responsable de taller **desactivar y eliminar técnicos**, y **crear, editar, desactivar y eliminar cuentas clientes** de su organización.

## Backend

- Migración `0023_taller_clientes_crud_permisos.sql`: permisos `clientes:crear|actualizar|eliminar` → `TALLER_RESPONSABLE` y `ADMIN`.
- **Técnicos** (`/api/app/taller/tecnicos`):
  - `POST /{id}/desactivar` — baja lógica (técnico + usuario `INACTIVO`).
  - `DELETE /{id}` — eliminación física si no hay asignaciones ni solicitudes.
  - Alta de técnico ahora asigna `tenant_id` del responsable.
- **Clientes** (`/api/clientes/`):
  - `POST /` — alta manual (`ClienteAdminCreate`).
  - `PUT /{id}` — editar identidad y perfil.
  - `POST /{id}/desactivar` — soft delete usuario.
  - `DELETE /{id}` — hard delete si no hay vehículos, solicitudes ni pagos.
  - Endpoints protegidos con `require_permission`.

## Frontend

- `taller-tecnicos`: botones Desactivar y Eliminar.
- `taller-clientes`: CRUD completo con modales y permisos JWT.
- `AdminApiService`: `createCliente`, `updateCliente`, `desactivarCliente`, `deleteCliente`.
- `TallerApiService`: `desactivarTecnico`, `deleteTecnico`.

## Probar

1. Aplicar migración `0023` (o `docker compose up -d --build` en BD nueva).
2. **Cerrar sesión y volver a entrar** en `/taller` para refrescar permisos en JWT.
3. Técnicos: desactivar / eliminar (eliminar falla con 409 si hay historial).
4. Clientes: crear, editar, desactivar, eliminar.
