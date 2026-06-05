-- Portal taller: permiso de lectura de bitácora acotada al equipo del taller.
BEGIN;

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, v.descripcion, NOW(), NOW()
FROM (VALUES
    (
        'bitacora_taller:leer',
        'Ver bitácora del taller',
        'bitacora',
        'Auditoría de actividades del responsable y técnicos del taller (sin datos de otros talleres ni clientes)'
    )
) AS v(codigo, nombre, modulo, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'bitacora_taller:leer'
WHERE r.nombre = 'TALLER_RESPONSABLE'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

COMMIT;
