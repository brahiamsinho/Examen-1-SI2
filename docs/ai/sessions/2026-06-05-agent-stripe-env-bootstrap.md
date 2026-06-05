# Sesión 2026-06-05 — Stripe test desde `.env` + bootstrap automático

## Objetivo

Usar `STRIPE_SECRET_KEY` / `STRIPE_PUBLISHABLE_KEY` del `.env` sin configurar manualmente `price_...` en admin.

## Implementación

1. **`stripe_price_resolver.py`** — Price ID efectivo: BD válida → `STRIPE_SAAS_PRICE_PRO|MAX|STARTER` del `.env`.
2. **`stripe_saas_bootstrap.py`** — Al arrancar con Stripe habilitado:
   - Sincroniza IDs del `.env` a `pricing_plans` si la BD tiene vacío/inválido.
   - Si `STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true` (default), crea Products/Prices en Stripe test y guarda en BD.
3. **`main.py` lifespan** — ejecuta bootstrap antes de seeds.
4. **`docker-compose.yml`** — pasa `STRIPE_SAAS_*` y `STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES`.
5. **Checkout/suscripción** — `billing`, `subscription_service`, `pricing_plans` usan el resolver.

## Config mínima `.env`

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true
```

Opcional (override manual por plan):

```env
STRIPE_SAAS_PRICE_PRO=price_...
STRIPE_SAAS_PRICE_MAX=price_...
```

## Verificación

```powershell
docker compose up -d --build backend
# Login taller → GET /api/app/taller/suscripcion → pro/max can_upgrade: true
# POST /api/app/taller/suscripcion/checkout plan_slug=pro → checkout_url cs_test_...
```
