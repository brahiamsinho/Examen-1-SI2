# Sesión 2026-06-05 — Confirmación checkout Stripe (sin webhook local)

## Problema

Tras pagar en Stripe Checkout (test), el plan del tenant no cambiaba al volver al panel taller.

**Causa:** el upgrade solo se aplicaba vía webhook `POST /api/webhooks/stripe-saas`. En local, Stripe no alcanza `localhost` sin Stripe CLI/ngrok.

## Solución

1. **Backend:** `POST /api/app/taller/suscripcion/confirm` con `{ session_id }`.
   - Consulta `stripe.checkout.Session.retrieve`.
   - Valida `status=complete`, `payment_status=paid`, `metadata.tenant_id`.
   - Reutiliza `aplicar_checkout_session_completada` (misma lógica que webhook).

2. **Frontend:** `success_url` incluye `session_id={CHECKOUT_SESSION_ID}`.
   - Al volver con `?checkout=ok&session_id=cs_...`, llama confirm y muestra plan actualizado.

3. **Refactor:** `aplicar_checkout_session_completada` extraída de `aplicar_evento_stripe_saas`.

## Archivos

- `billing/service.py`, `stripe_saas_client.py`, `plan_tiers.py`
- `taller_responsable/router.py`, `subscription_service.py`, `schemas.py`
- `taller-suscripcion.component.ts`, `taller-api.service.ts`, `taller-api.models.ts`

## Producción

Seguir usando webhook + `STRIPE_SAAS_WEBHOOK_SECRET`. La confirmación por URL es idempotente y complementa el webhook en dev.
