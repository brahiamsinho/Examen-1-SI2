# SAAS_PHASE3_PLAN.md — Implementado (resumen)

## Backend
- `0017_saas_billing_phase3.sql` — `stripe_subscription_id`, `stripe_price_id`
- `GET /api/public/tenants`, `GET /api/public/tenant-by-host`
- Billing: `POST /api/admin/tenants/{id}/checkout-session`, `billing-portal`, `POST /api/webhooks/stripe-saas`
- Subdominio: `tenant_resolve.py` + middleware Host
- Bitácora filtrada por tenant; registro cliente con `tenant_id`
- `require_writable_tenant_subscription` en crear emergencia
- Tests: `backend/tests/test_multitenancy_phase3.py`

## Frontend
- Mobile: campo organización + `X-Tenant-Slug` en Dio
- Taller web: slug en login + query `?org=`
- Admin: checkout Stripe en organizaciones

## Activación BD existente
```powershell
Get-Content backend\migrations\0017_saas_billing_phase3.sql | docker compose exec -T db psql -U emergencias -d emergencias_db
```

## Stripe (opcional)
Configurar en `.env`: `STRIPE_SECRET_KEY`, `STRIPE_SAAS_PRICE_STARTER`, `STRIPE_SAAS_WEBHOOK_SECRET` y endpoint webhook `https://<api>/api/webhooks/stripe-saas`.
