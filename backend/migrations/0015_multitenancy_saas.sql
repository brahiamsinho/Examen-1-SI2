-- 0015_multitenancy_saas.sql
-- SaaS multi-tenant: shared schema + tenant_id (DEC-022)
-- Idempotente donde aplica (IF NOT EXISTS / DO blocks).

DO $$ BEGIN
    CREATE TYPE estado_tenant AS ENUM ('ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'PENDIENTE');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE plan_tenant AS ENUM ('FREE', 'STARTER', 'PRO', 'ENTERPRISE');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS tenants (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(80) NOT NULL UNIQUE,
    nombre          VARCHAR(150) NOT NULL,
    estado          estado_tenant NOT NULL DEFAULT 'ACTIVO',
    plan            plan_tenant NOT NULL DEFAULT 'STARTER',
    dominio_custom  VARCHAR(255),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants (slug);
CREATE INDEX IF NOT EXISTS ix_tenants_estado ON tenants (estado);

-- Tenant por defecto para datos legacy / demo Santa Cruz
INSERT INTO tenants (slug, nombre, estado, plan, created_at, updated_at)
SELECT 'demo-sc', 'Demo Santa Cruz (legacy)', 'ACTIVO', 'STARTER', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM tenants WHERE slug = 'demo-sc');

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE talleres ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE vehiculos ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE RESTRICT;
ALTER TABLE solicitudes_emergencia ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS ix_usuarios_tenant_id ON usuarios (tenant_id);
CREATE INDEX IF NOT EXISTS ix_talleres_tenant_id ON talleres (tenant_id);
CREATE INDEX IF NOT EXISTS ix_clientes_tenant_id ON clientes (tenant_id);
CREATE INDEX IF NOT EXISTS ix_vehiculos_tenant_id ON vehiculos (tenant_id);
CREATE INDEX IF NOT EXISTS ix_solicitudes_emergencia_tenant_id ON solicitudes_emergencia (tenant_id);

-- Backfill: todo el dataset existente al tenant demo-sc
UPDATE usuarios u
SET tenant_id = t.id
FROM tenants t
WHERE t.slug = 'demo-sc'
  AND u.tenant_id IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM usuario_rol ur
      JOIN roles r ON r.id = ur.rol_id
      WHERE ur.usuario_id = u.id AND r.nombre = 'ADMIN'
  );

UPDATE talleres SET tenant_id = (SELECT id FROM tenants WHERE slug = 'demo-sc' LIMIT 1)
WHERE tenant_id IS NULL;

UPDATE clientes SET tenant_id = (SELECT id FROM tenants WHERE slug = 'demo-sc' LIMIT 1)
WHERE tenant_id IS NULL;

UPDATE vehiculos v SET tenant_id = c.tenant_id
FROM clientes c
WHERE v.cliente_id = c.id AND v.tenant_id IS NULL;

UPDATE solicitudes_emergencia s SET tenant_id = c.tenant_id
FROM clientes c
WHERE s.cliente_id = c.id AND s.tenant_id IS NULL;

-- Permisos plataforma (superadmin ADMIN sin tenant_id)
INSERT INTO permisos (codigo, nombre, modulo, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, NOW(), NOW()
FROM (VALUES
    ('tenants:leer', 'Listar tenants SaaS', 'tenants'),
    ('tenants:crear', 'Crear tenants SaaS', 'tenants'),
    ('tenants:actualizar', 'Actualizar tenants SaaS', 'tenants')
) AS v(codigo, nombre, modulo)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
CROSS JOIN permisos p
WHERE r.nombre = 'ADMIN'
  AND p.codigo IN ('tenants:leer', 'tenants:crear', 'tenants:actualizar')
  AND NOT EXISTS (
      SELECT 1 FROM rol_permiso rp
      WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );
