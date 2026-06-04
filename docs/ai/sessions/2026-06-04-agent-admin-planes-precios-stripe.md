# Sesión 2026-06-04 — Admin planes y precios + Stripe landing

## Pedido

Ocultar **Roles** y **Permisos** del sidebar del panel admin web. En su lugar, gestionar los planes/precios de la landing y habilitar pasarela Stripe.

## Implementado

### Backend (previo + integrado)

- Migración `0019_pricing_plans.sql` — tabla `pricing_plans` + seed free/pro/max.
- `GET/PATCH /api/admin/pricing-plans` (superadmin).
- `GET /api/public/pricing/plans`, `GET /api/public/pricing/stripe-config`, `POST /api/public/pricing/checkout`.

### Frontend admin

- Sidebar: grupo **Comercial → Planes y precios** (`/admin/panel/planes-precios`), solo superadmin.
- Quitado grupo **Acceso** (Roles/Permisos) del menú lateral (rutas siguen existiendo por URL directa).
- Componente `admin-planes-precios` — listado en tarjetas, edición modal (precio, beneficios, CTA, Stripe Price ID, activo/destacado).
- `AdminApiService.listPricingPlans()` / `updatePricingPlan()`.

### Landing pública

- Planes cargados desde API (`PublicApiService.listPricingPlans()`), fallback local si falla.
- Plan de pago con `stripe_price_id` + Stripe habilitado → modal email → redirect a Stripe Checkout.
- Plan free → registro taller; plan contacto → ancla `#contacto`.

## Probar

1. Reiniciar backend (migración 0019): `docker compose up -d --build backend`.
2. Login admin superadmin → **Comercial → Planes y precios**.
3. Editar plan **Pro** → pegar `stripe_price_id` de Stripe Dashboard.
4. Landing `#precios` → **Contratar Pro** → email → Stripe Checkout.
5. Variables: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` (y opcional price env legacy).

## Archivos clave

- `frontend/src/app/admin/features/planes-precios/*`
- `frontend/src/app/admin/shell/admin-shell.component.ts`
- `frontend/src/app/public/pages/landing/landing-page.component.*`
- `frontend/src/app/core/services/public-api.service.ts`
- `backend/app/modules/acceso_y_administracion/pricing_plans/*`
