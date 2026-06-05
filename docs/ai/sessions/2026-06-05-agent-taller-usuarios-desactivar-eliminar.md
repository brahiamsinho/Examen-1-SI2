# Sesión 2026-06-05 — Usuarios taller desactivar/eliminar

## Objetivo

Misma gestión que técnicos/clientes en **Usuarios del taller**: desactivar cuenta y eliminar físicamente cuando no hay bloqueos.

## Backend

- Migración `0024_taller_usuarios_eliminar_permiso.sql`: `usuarios:eliminar` → `TALLER_RESPONSABLE`.
- `POST /api/usuarios/{id}/desactivar` — soft delete + sync `tecnicos.estado` si aplica.
- `DELETE /api/usuarios/{id}` — hard delete (bloquea responsable de taller o técnico con historial).
- Validación tenant + no auto-desactivar/eliminarse + no gestionar rol CLIENTE desde aquí.

## Frontend

- `taller-usuarios`: botones Activar, Desactivar, Eliminar.
- `AdminApiService.desactivarUsuario()`; admin panel actualizado.
- `deleteUsuario()` ahora es eliminación física.

## Probar

1. Migración `0024` + relogin en `/taller`.
2. Usuarios del taller → desactivar un técnico; activar de nuevo.
3. Eliminar usuario sin historial; 409 si es responsable o técnico con atenciones.
