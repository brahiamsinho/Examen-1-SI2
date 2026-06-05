-- =========================================================
-- CU42 — Registrar cotización del servicio (taller web).
-- Detalle de cotización + permiso presupuestos:registrar.
-- =========================================================

BEGIN;

ALTER TABLE solicitudes_emergencia
    ADD COLUMN IF NOT EXISTS presupuesto_detalle TEXT NULL;

COMMENT ON COLUMN solicitudes_emergencia.presupuesto_detalle IS
    'Detalle de trabajo/repuestos de la cotización (taller o revisión técnica).';

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
VALUES (
    'presupuestos:registrar',
    'Registrar cotización de servicio',
    'taller_operacion',
    'Permite al taller registrar presupuesto (cotización) en BOB para una solicitud asignada',
    NOW(),
    NOW()
)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'presupuestos:registrar'
WHERE r.nombre IN ('ADMIN', 'TALLER_RESPONSABLE')
ON CONFLICT (rol_id, permiso_id) DO NOTHING;

COMMIT;
