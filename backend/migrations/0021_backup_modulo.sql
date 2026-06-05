-- Módulo backup/restore adaptado a shared schema + tenant_id (EmergenciasViales).
BEGIN;

DO $$ BEGIN
    CREATE TYPE tipo_backup AS ENUM ('PLATAFORMA', 'TENANT', 'EVIDENCIAS');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE estado_backup AS ENUM (
        'PENDIENTE',
        'EN_PROGRESO',
        'COMPLETADO',
        'FALLIDO',
        'RESTAURADO',
        'EXPIRADO'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS backups (
    id                      SERIAL PRIMARY KEY,
    tenant_id               INTEGER REFERENCES tenants(id) ON DELETE SET NULL,
    tipo                    tipo_backup NOT NULL,
    archivo                 VARCHAR(500) NOT NULL DEFAULT '',
    tamano_mb               NUMERIC(10, 2),
    estado                  estado_backup NOT NULL DEFAULT 'PENDIENTE',
    incluye_evidencias      BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expira_en               TIMESTAMPTZ,
    creado_por_usuario_id   INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    error_mensaje           TEXT,
    restaurado_en           TIMESTAMPTZ,
    restaurado_por_usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    motivo_restore          TEXT
);

CREATE INDEX IF NOT EXISTS ix_backups_estado ON backups (estado);
CREATE INDEX IF NOT EXISTS ix_backups_tenant_id ON backups (tenant_id);
CREATE INDEX IF NOT EXISTS ix_backups_creado_en ON backups (creado_en DESC);
CREATE INDEX IF NOT EXISTS ix_backups_expira_en ON backups (expira_en);

CREATE TABLE IF NOT EXISTS backup_config (
    id                  SERIAL PRIMARY KEY,
    backup_automatico   BOOLEAN NOT NULL DEFAULT TRUE,
    hora_backup         TIME NOT NULL DEFAULT '03:00',
    frecuencia          VARCHAR(10) NOT NULL DEFAULT 'daily',
    retencion_dias      INTEGER NOT NULL DEFAULT 7,
    incluir_evidencias  BOOLEAN NOT NULL DEFAULT TRUE,
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO backup_config (backup_automatico, hora_backup, frecuencia, retencion_dias, incluir_evidencias)
SELECT TRUE, '03:00', 'daily', 7, TRUE
WHERE NOT EXISTS (SELECT 1 FROM backup_config);

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, v.descripcion, NOW(), NOW()
FROM (VALUES
    (
        'backup:gestionar',
        'Gestionar backups de plataforma',
        'backup',
        'Crear, descargar, restaurar y eliminar respaldos (superadmin plataforma)'
    )
) AS v(codigo, nombre, modulo, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'backup:gestionar'
WHERE r.nombre = 'ADMIN'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

COMMIT;
