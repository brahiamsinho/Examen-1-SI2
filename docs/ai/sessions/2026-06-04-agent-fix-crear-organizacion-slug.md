# Sesión 2026-06-04 — Fix crear organización (slug 422)

## Problema reportado

Usuario superadmin no podía crear organización desde `/admin/panel/organizaciones`.
Mensaje UI: *"No se pudo crear la organización (¿slug duplicado?)"*.
Log: `POST /api/admin/tenants` → **422 Unprocessable Entity**.

## Diagnóstico

- **422** = fallo de validación del body (Pydantic), no duplicado en BD.
- Duplicado real → **409** desde `create_tenant()` con `"Slug de tenant ya existe"`.
- El schema `TenantCreate` exigía slug en minúsculas (`pattern`), pero el usuario escribía `Nueva-Org-Test` o similar.
- El service ya hacía `.lower()`, pero **demasiado tarde**: FastAPI valida el schema antes de llamar al service.

## Cambios

| Capa | Archivo | Qué |
|------|---------|-----|
| Backend | `tenants/schemas.py` | `normalize_tenant_slug()`, validator `mode="before"` en slug y nombre |
| Backend | `tenants/service.py` | Usa `normalize_tenant_slug()` al crear |
| Frontend | `admin-organizaciones.component.ts` | `normalizeSlug()`, mensajes por status HTTP |
| Frontend | `admin-organizaciones.component.html` | Hint bajo campo slug |
| Frontend | `admin-organizaciones.component.scss` | `.org__hint` |

## Verificación

```http
POST /api/admin/tenants
Authorization: Bearer <token>
{"slug":"Nueva-Org-Test","nombre":"Nueva Org Test","plan":"STARTER","estado":"ACTIVO"}
→ 201, slug guardado: nueva-org-test
```

## Issue secundario (no bloqueante)

Seeds al startup fallan 8 veces: intento asignar rol CLIENTE vía `dev_cliente.py` bloqueado por regla de negocio en `roles/service.py`. Backend arranca igual.

## Próximo paso opcional

Ajustar seed `ensure_dev_cliente` para no llamar `asignar_roles_usuario` con CLIENTE desde panel path.
