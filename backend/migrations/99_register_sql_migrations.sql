-- Marca migraciones ya aplicadas por docker-entrypoint-initdb.d.
-- Evita que docker_bootstrap vuelva a ejecutar el mismo SQL en el primer arranque del backend.
CREATE TABLE IF NOT EXISTS app_sql_migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO app_sql_migrations (filename) VALUES
    ('0002_ciclo2_fase1_emergencias.sql'),
    ('0003_ciclo2_fase2_seguimiento.sql'),
    ('0004_ciclo2_fase3_comunicaciones.sql'),
    ('0005_ciclo2_fase4_pagos.sql'),
    ('0006_tecnico_asignado_at.sql'),
    ('0007_taller_operacion_permisos.sql'),
    ('0008_taller_bandeja_disponibilidad.sql'),
    ('0009_taller_asignacion_tecnico.sql'),
    ('0010_taller_comisiones.sql'),
    ('0011_usuario_tokens_seguridad.sql'),
    ('0012_ia_modulo.sql'),
    ('0013_tecnico_ubicacion_compartida.sql'),
    ('0014_presupuesto_bob_solicitud.sql'),
    ('0015_multitenancy_saas.sql'),
    ('0016_multitenancy_phase2.sql'),
    ('0017_saas_billing_phase3.sql'),
    ('0018_taller_acceso_permisos.sql'),
    ('0019_pricing_plans.sql'),
    ('0020_taller_bitacora_permiso.sql'),
    ('0021_backup_modulo.sql'),
    ('0022_taller_backup.sql'),
    ('0023_taller_clientes_crud_permisos.sql'),
    ('0024_taller_usuarios_eliminar_permiso.sql'),
    ('0025_reportes_modulo.sql')
ON CONFLICT (filename) DO NOTHING;
