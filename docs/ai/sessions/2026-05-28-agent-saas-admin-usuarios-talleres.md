# Sesión 2026-05-28 — Admin SaaS: usuarios, talleres y slug

## Objetivo
Alinear el panel admin con multi-tenant: slug/organización en altas, clientes fuera del admin, talleres ligados al tenant.

## Cambios backend
- `UsuarioCreate.tenant_id`; superadmin puede crear cuenta plataforma (`null`) o de organización.
- `get_usuarios_admin`: oculta usuarios con rol `CLIENTE`.
- `roles/service.asignar_roles_usuario`: rechaza asignar rol `CLIENTE` desde admin.
- `TallerCreate.tenant_id`; validación responsable mismo `tenant_id`; `TallerRead.tenant_id`.

## Cambios frontend
- `AdminTenantContextService`: `tenantCreateBody()`, `orgScopeLabel()`, `requiresOrgForCreate()`.
- Usuarios: texto SaaS, ámbito organización, sin rol CLIENTE en filtros/asignación, checkbox cuenta plataforma.
- Talleres: ámbito slug, crear responsable en modal, `tenant_id` en POST taller.

## Modelo de actores (resumen)
| Actor | Quién lo da de alta | Slug |
|-------|---------------------|------|
| Admin plataforma | Superadmin (sin tenant) | — |
| Personal org (taller/técnico/admin tenant) | Admin + org seleccionada | `tenant_id` / slug en barra |
| Cliente final | Registro app móvil | `X-Tenant-Slug` |
| Taller (negocio) | Admin con org + responsable | `tenant_id` del taller |

## Verificación manual
1. Superadmin: elegir org `demo-sc` → Usuarios → crear técnico → asignar rol TECNICO.
2. Talleres → Nuevo taller → crear responsable o elegir existente → Crear taller.
3. Confirmar que usuarios CLIENTE de seeds no aparecen en lista admin.
4. Mobile: registro cliente con slug `demo-sc` sigue funcionando.
