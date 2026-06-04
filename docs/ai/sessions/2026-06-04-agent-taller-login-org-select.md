# Sesión: selector de organización en login taller

**Fecha:** 2026-06-04

## Objetivo

Reemplazar el input de texto «Organización (slug)» en `/taller` por un desplegable con las organizaciones activas del sistema.

## Cambios

- `frontend/src/app/core/services/public-api.service.ts` — nuevo servicio público `listActiveTenants()`.
- `frontend/src/app/taller/features/auth/taller-login/taller-login.component.ts` — carga tenants en `ngOnInit`, preselección inteligente.
- `taller-login.component.html` — `<select>` con etiqueta `nombre (slug)`.
- `taller-login.component.scss` — estilos para select oscuro con chevron.

## API usada

`GET /api/public/tenants` → `[{ slug, nombre }]` (tenants activos).

## Verificación

1. Rebuild frontend: `docker compose up --build frontend` (o stack completo).
2. Abrir `http://localhost/taller`.
3. Confirmar que el desplegable lista orgs (p. ej. `demo-sc`, `si2-angelica`).
4. Login con slug correcto + credenciales del responsable.
