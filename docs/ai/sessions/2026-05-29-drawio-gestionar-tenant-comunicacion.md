# Sesión 2026-05-29 — Draw.io: comunicación Gestionar tenant

## Artefacto
- `docs/diagrams/gestionar-tenant-comunicacion.drawio`

## Estado código (honesto)
**Diseño objetivo / ficha CU** — a 2026-05-29 no hay en repo:
- Rutas `/api/admin/tenants`
- Pantalla `/admin/panel/organizaciones`
- `tenant_id` en modelos ni RLS PostgreSQL
- `require_writable_tenant_subscription`

El diagrama sirve para defensa de **arquitectura SaaS prevista**, alineado a EA diagrama ID **30**.

## Trazabilidad ficha → mensajes

| Paso | Mensaje | Previsto |
|------|---------|----------|
| 1 | 1.IngresarPanelOrganizaciones | Angular admin shell |
| 2 | 1.1 listarTenants | GET /api/admin/tenants |
| 3 | 1.2 crearTenant | POST slug, nombre, plan |
| 4 | 1.3 editarTenant | PATCH /api/admin/tenants/{id} |
| 5 | 1.5 vincularStripe | billing/ SaaS |
| 6 | 1.6 seleccionarOrganizacion | filtro shell admin |
| 7 | 1.7 aplicarRLS_JWT | aislamiento por tenant_id |

## Excepciones
- 2.1 SlugDuplicado
- 2.2 SuscripcionVencida (require_writable_tenant_subscription)
- 2.3 AdminNoSuperadmin (tenant_id NULL)

## EA
- `docs/ai/sessions/2026-05-29-agent-ea-gestionar-tenant.md`
