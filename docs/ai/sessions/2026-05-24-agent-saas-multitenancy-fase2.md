# Sesión 2026-05-24 — SaaS multi-tenant fase 2

## Objetivo
Completar fase 2: RLS Postgres, unicidad email/tel/placa por tenant, billing columns Stripe, middleware y panel Angular.

## Cambios principales
- `backend/migrations/0016_multitenancy_phase2.sql` + mount Docker `16_`
- `tenant_context.py`, `tenant_middleware.py`, RLS vía `get_db`
- Auth: login `X-Tenant-Slug`, `/me` con tenant flags, bypass RLS en login
- Servicios: usuarios/talleres filtro `?tenant_id=`, vehículos `tenant_id` desde cliente
- Tenants: Stripe link endpoint, schemas suscripción
- Frontend: `AdminTenantContextService`, organizaciones, selector en shell

## Activación BD existente
```powershell
Get-Content backend\migrations\0016_multitenancy_phase2.sql | docker compose exec -T db psql -U emergencias -d emergencias_db
```
Re-login admin para refrescar JWT y `/auth/me`.

## Siguiente
Fase 3: subdominio, webhooks Stripe SaaS, tests integración RLS.
