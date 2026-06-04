-- Planes comerciales (landing + Stripe Billing)
BEGIN;

CREATE TABLE IF NOT EXISTS pricing_plans (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly_bob NUMERIC(12, 2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'BOB',
    benefits JSONB NOT NULL DEFAULT '[]'::jsonb,
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    badge VARCHAR(80),
    cta_label VARCHAR(120) NOT NULL,
    cta_router_link VARCHAR(255),
    cta_href VARCHAR(255),
    stripe_price_id VARCHAR(255),
    sort_order INT NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

INSERT INTO pricing_plans (
    slug, name, description, price_monthly_bob, currency, benefits,
    featured, badge, cta_label, cta_router_link, cta_href, stripe_price_id,
    sort_order, active, created_at, updated_at
) VALUES
(
    'free',
    'Free',
    'Prueba el flujo completo con un taller en entorno de desarrollo.',
    0,
    'BOB',
    '["1 organización / slug","Hasta 2 técnicos activos","Emergencias y bandeja","App móvil cliente y técnico","Documentación"]'::jsonb,
    FALSE,
    NULL,
    'Empezar gratis',
    '/taller/registro',
    NULL,
    NULL,
    1,
    TRUE,
    NOW(),
    NOW()
),
(
    'pro',
    'Pro',
    'Operación real con finanzas, admin y multi-tenant.',
    299,
    'BOB',
    '["Slug y organización propia","Técnicos y talleres ilimitados","Panel admin + portal taller","Finanzas y comisiones","Bitácora y roles avanzados"]'::jsonb,
    TRUE,
    'Recomendado',
    'Contratar Pro',
    '/taller/registro',
    NULL,
    NULL,
    2,
    TRUE,
    NOW(),
    NOW()
),
(
    'max',
    'Max',
    'Escala regional, B2B y facturación avanzada.',
    599,
    'BOB',
    '["Todo lo de Pro","Múltiples organizaciones","KPIs y reportes extendidos","Stripe / billing SaaS","Soporte prioritario"]'::jsonb,
    FALSE,
    NULL,
    'Contactar',
    NULL,
    '#contacto',
    NULL,
    3,
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (slug) DO NOTHING;

COMMIT;
