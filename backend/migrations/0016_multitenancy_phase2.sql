-- 0016_multitenancy_phase2.sql
-- Fase 2 SaaS: email/tel por tenant, billing Stripe, RLS (DEC-023)

DO $$ BEGIN
    CREATE TYPE estado_suscripcion_tenant AS ENUM (
        'TRIAL', 'ACTIVA', 'PAST_DUE', 'CANCELADA', 'SUSPENDIDA'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_status estado_suscripcion_tenant DEFAULT 'TRIAL';
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS subscription_ends_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS ix_tenants_stripe_customer ON tenants (stripe_customer_id)
    WHERE stripe_customer_id IS NOT NULL;

-- Email/teléfono: únicos por tenant; plataforma (tenant_id NULL) aparte
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_email_key;
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_telefono_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_tenant_email
    ON usuarios (tenant_id, lower(email))
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_platform_email
    ON usuarios (lower(email))
    WHERE tenant_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_tenant_telefono
    ON usuarios (tenant_id, telefono)
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_platform_telefono
    ON usuarios (telefono)
    WHERE tenant_id IS NULL;

-- Placa de vehículo única por tenant
ALTER TABLE vehiculos DROP CONSTRAINT IF EXISTS vehiculos_placa_key;

CREATE UNIQUE INDEX IF NOT EXISTS uq_vehiculos_tenant_placa
    ON vehiculos (tenant_id, lower(placa))
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_vehiculos_platform_placa
    ON vehiculos (lower(placa))
    WHERE tenant_id IS NULL;

-- Row Level Security (shared schema)
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE talleres ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE solicitudes_emergencia ENABLE ROW LEVEL SECURITY;

DO $$ DECLARE t text; BEGIN
    FOREACH t IN ARRAY ARRAY['usuarios','talleres','clientes','vehiculos','solicitudes_emergencia'] LOOP
        EXECUTE format('DROP POLICY IF EXISTS tenant_rls_all ON %I', t);
        EXECUTE format($p$
            CREATE POLICY tenant_rls_all ON %I
            FOR ALL
            USING (
                COALESCE(current_setting('app.bypass_rls', true), '') = 'on'
                OR tenant_id IS NULL
                OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::integer
            )
            WITH CHECK (
                COALESCE(current_setting('app.bypass_rls', true), '') = 'on'
                OR tenant_id IS NULL
                OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::integer
            )
        $p$, t);
    END LOOP;
END $$;
