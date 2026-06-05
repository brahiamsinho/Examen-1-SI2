-- Módulo reportes personalizados QBE + permisos + plantillas predefinidas del sistema.
BEGIN;

CREATE TABLE IF NOT EXISTS reportes_plantilla (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    taller_id INTEGER REFERENCES talleres(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    qbe_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_system_report BOOLEAN NOT NULL DEFAULT FALSE,
    created_by_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_reportes_plantilla_system ON reportes_plantilla (is_system_report);
CREATE INDEX IF NOT EXISTS ix_reportes_plantilla_tenant ON reportes_plantilla (tenant_id);
CREATE INDEX IF NOT EXISTS ix_reportes_plantilla_taller ON reportes_plantilla (taller_id);

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, v.descripcion, NOW(), NOW()
FROM (VALUES
    ('reportes:leer', 'Consultar reportes', 'reportes', 'Ver y ejecutar reportes predefinidos y personalizados'),
    ('reportes:crear', 'Crear reportes personalizados', 'reportes', 'Guardar plantillas QBE propias del taller'),
    ('reportes:actualizar', 'Editar reportes personalizados', 'reportes', 'Modificar plantillas QBE del taller'),
    ('reportes:eliminar', 'Eliminar reportes personalizados', 'reportes', 'Borrar plantillas QBE del taller'),
    ('reportes:exportar', 'Exportar reportes', 'reportes', 'Descargar reportes en Excel, PDF o CSV')
) AS v(codigo, nombre, modulo, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo IN (
    'reportes:leer',
    'reportes:crear',
    'reportes:actualizar',
    'reportes:eliminar',
    'reportes:exportar'
)
WHERE r.nombre IN ('TALLER_RESPONSABLE', 'ADMIN')
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

-- Plantillas predefinidas (CU22) — visibles para todos los talleres.
INSERT INTO reportes_plantilla (nombre, descripcion, qbe_payload, is_system_report, tenant_id, taller_id, created_at, updated_at)
SELECT
    'Solicitudes recientes (30 días)',
    'Emergencias registradas en los últimos 30 días de tu taller.',
    json_build_object(
        'model', 'SolicitudEmergencia',
        'filters', json_build_object('created_at__gte', (NOW() - INTERVAL '30 days')::text),
        'order_by', json_build_array('-created_at')
    ),
    TRUE, NULL, NULL, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM reportes_plantilla rp
    WHERE rp.nombre = 'Solicitudes recientes (30 días)' AND rp.is_system_report = TRUE
);

INSERT INTO reportes_plantilla (nombre, descripcion, qbe_payload, is_system_report, tenant_id, taller_id, created_at, updated_at)
SELECT
    'Emergencias finalizadas',
    'Solicitudes con estado FINALIZADA.',
    json_build_object(
        'model', 'SolicitudEmergencia',
        'filters', json_build_object('estado', 'FINALIZADA'),
        'order_by', json_build_array('-finalizada_at', '-created_at')
    ),
    TRUE, NULL, NULL, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM reportes_plantilla rp
    WHERE rp.nombre = 'Emergencias finalizadas' AND rp.is_system_report = TRUE
);

INSERT INTO reportes_plantilla (nombre, descripcion, qbe_payload, is_system_report, tenant_id, taller_id, created_at, updated_at)
SELECT
    'Comisiones pendientes',
    'Comisiones del taller aún no liquidadas.',
    json_build_object(
        'model', 'ComisionTaller',
        'filters', json_build_object('estado', 'PENDIENTE'),
        'order_by', json_build_array('-calculado_at')
    ),
    TRUE, NULL, NULL, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM reportes_plantilla rp
    WHERE rp.nombre = 'Comisiones pendientes' AND rp.is_system_report = TRUE
);

INSERT INTO reportes_plantilla (nombre, descripcion, qbe_payload, is_system_report, tenant_id, taller_id, created_at, updated_at)
SELECT
    'Técnicos activos',
    'Personal técnico con estado ACTIVO.',
    json_build_object(
        'model', 'Tecnico',
        'filters', json_build_object('estado', 'ACTIVO'),
        'order_by', json_build_array('id')
    ),
    TRUE, NULL, NULL, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM reportes_plantilla rp
    WHERE rp.nombre = 'Técnicos activos' AND rp.is_system_report = TRUE
);

COMMIT;
