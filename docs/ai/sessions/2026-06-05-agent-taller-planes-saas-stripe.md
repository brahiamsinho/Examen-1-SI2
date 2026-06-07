# Sesión 2026-06-05 — Planes SaaS en panel taller + upgrade Stripe

## Objetivo

Mostrar planes comerciales del SaaS en el sidebar del panel taller, indicar plan actual y permitir **upgrade** (no downgrade) vía Stripe con credenciales del `.env`.

## Backend

### Nuevos endpoints (`/api/app/taller`)
- `GET /suscripcion` — catálogo de planes + plan actual del tenant del usuario.
- `POST /suscripcion/checkout` — checkout Stripe solo hacia plan superior (`plan_slug`, `success_url`, `cancel_url`).

### Lógica
- `billing/plan_tiers.py` — resuelve plan actual (por `stripe_price_id` o enum legacy del tenant).
- `billing/service.crear_checkout_upgrade()` — valida `sort_order` (solo ascender).
- Webhook `checkout.session.completed` — actualiza `tenant.plan`, `stripe_price_id` desde metadata `plan_slug`.

### Archivos
- `backend/app/modules/acceso_y_administracion/billing/plan_tiers.py`
- `backend/app/modules/acceso_y_administracion/billing/service.py`
- `backend/app/modules/talleres_y_tecnicos/taller_responsable/subscription_service.py`
- `backend/app/modules/talleres_y_tecnicos/taller_responsable/router.py`
- `backend/app/modules/talleres_y_tecnicos/taller_responsable/schemas.py`

## Frontend

- Ruta `/taller/panel/suscripcion` — tarjetas de planes con botón Upgrade.
- Sidebar: bloque **Planes SaaS** (lista compacta + badge «Actual» + botón ↑ upgrade).
- Nav grupo **Suscripción → Planes SaaS**.
- `TallerApiService.getSuscripcion()` / `createSuscripcionCheckout()`.

## Configuración Stripe

1. `.env`: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` (test: `sk_test_` / `pk_test_`).
2. Con `STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true` (default), el backend crea `price_...` al arrancar — no hace falta admin manual.
3. Opcional: `STRIPE_SAAS_PRICE_PRO` / `STRIPE_SAAS_PRICE_MAX` o Admin → Planes y precios.
4. Webhook opcional en producción: `STRIPE_SAAS_WEBHOOK_SECRET` → `/api/webhooks/stripe-saas`.

## Prueba

1. `docker compose up -d --build backend frontend`
2. Login taller `luis.rivera@sc-demo.test`
3. Sidebar: ver planes; ir a **Planes SaaS**; upgrade Pro → redirect Stripe Checkout.
