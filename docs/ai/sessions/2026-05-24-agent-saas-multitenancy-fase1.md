# Sesión 2026-05-24 — SaaS multi-tenant fase 1

## Objetivo

Base multi-tenant en backend + skills de ecosistema + documentación.

## Entregables

- Skills globales: `multitenancy`, `multi-tenant-safety-checker`
- Migración `0015_multitenancy_saas.sql` + mount Docker `15_`
- Módulo `acceso_y_administracion/tenants/` (CRUD superadmin)
- `app/core/tenant.py`, `AuthContext`, JWT `tenant_id`
- `tenant_id` en modelos: usuarios, talleres, clientes, vehiculos, solicitudes_emergencia
- Finanzas admin filtradas por tenant; bandeja solo talleres del mismo tenant
- Seeds: `dev_tenant.py`, demo-sc, admin sin tenant

## Aplicar en BD existente

```powershell
docker compose exec -T db psql -U emergencias -d emergencias_db < backend/migrations/0015_multitenancy_saas.sql
docker compose exec backend python -m app.seeds
```

Re-login para JWT con `tenant_id`.

## Pendiente fase 2

- RLS PostgreSQL
- email único por `(tenant_id, email)`
- billing Stripe por tenant
- subdominio / `X-Tenant-Slug`
- filtrar todos los listados de módulos restantes
