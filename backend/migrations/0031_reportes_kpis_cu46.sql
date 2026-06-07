-- =========================================================
-- CU46 — Visualizar dashboard de KPIs (admin + taller).
-- Permiso reportes:leer para lectura de métricas agregadas.
-- =========================================================

BEGIN;

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
VALUES (
    'reportes:leer',
    'Consultar reportes y KPIs',
    'reportes',
    'Permite visualizar dashboards de KPIs operativos y financieros del tenant/taller',
    NOW(),
    NOW()
)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'reportes:leer'
WHERE r.nombre IN ('ADMIN', 'TALLER_RESPONSABLE')
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

COMMIT;
