-- 0017_saas_billing_phase3.sql — Fase 3 SaaS: suscripción Stripe y metadatos billing

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS stripe_price_id VARCHAR(255);

CREATE INDEX IF NOT EXISTS ix_tenants_stripe_subscription
    ON tenants (stripe_subscription_id)
    WHERE stripe_subscription_id IS NOT NULL;
