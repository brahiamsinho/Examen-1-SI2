# Sesión 2026-06-04 — Admin provision taller + credenciales /taller

## Objetivo

Simplificar el alta SaaS de talleres: un solo formulario admin con credenciales de login en `/taller`, sin pasar por menú Usuarios.

## Backend

- `TallerProvisionIn` / `TallerProvisionRead` en `talleres/schemas.py`
- `provision_taller_con_responsable()` en `talleres/service.py`
- `POST /api/talleres/provision` en `talleres/router.py`
- Usuario `ACTIVO` + `tenant_id` + rol `TALLER_RESPONSABLE` + taller (sin verificación email)

## Frontend

- `AdminApiService.provisionTaller()`
- Modal único en `admin-talleres` (datos taller + acceso portal)
- Pantalla éxito con slug + email + hint `/taller`
- Sidebar: quitado ítem **Usuarios** (ruta `/admin/panel/usuarios` sigue existiendo)

## Probar

1. Superadmin → Organizaciones (org `demo-sc` existe)
2. Talleres → Nuevo taller → completar formulario → Crear
3. `/taller` con slug `demo-sc`, email y contraseña del formulario → panel OK

## Decisión

DEC-030 en `DECISIONS_LOG.md`; `FLOWS_PORTAL_TALLER.md` §6 actualizado.
