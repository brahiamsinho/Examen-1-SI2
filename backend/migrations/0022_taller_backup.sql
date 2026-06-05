-- Backups por taller (portal responsable) + config automática (ej. 03:00).
BEGIN;

DO $$ BEGIN
    ALTER TYPE tipo_backup ADD VALUE 'TALLER';
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE backups
    ADD COLUMN IF NOT EXISTS taller_id INTEGER REFERENCES talleres(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_backups_taller_id ON backups (taller_id);

CREATE TABLE IF NOT EXISTS taller_backup_config (
    id                  SERIAL PRIMARY KEY,
    taller_id           INTEGER NOT NULL UNIQUE REFERENCES talleres(id) ON DELETE CASCADE,
    backup_automatico   BOOLEAN NOT NULL DEFAULT TRUE,
    hora_backup         TIME NOT NULL DEFAULT '03:00',
    frecuencia          VARCHAR(10) NOT NULL DEFAULT 'daily',
    retencion_dias      INTEGER NOT NULL DEFAULT 7,
    ultimo_backup_auto  TIMESTAMPTZ,
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, v.descripcion, NOW(), NOW()
FROM (VALUES
    (
        'backup_taller:gestionar',
        'Gestionar backups del taller',
        'backup',
        'Crear, descargar, restaurar y configurar respaldos del taller'
    )
) AS v(codigo, nombre, modulo, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'backup_taller:gestionar'
WHERE r.nombre = 'TALLER_RESPONSABLE'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

COMMIT;
