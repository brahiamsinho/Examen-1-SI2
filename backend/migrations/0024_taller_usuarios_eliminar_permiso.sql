-- Portal taller: permiso desactivar/eliminar usuarios del staff.
BEGIN;

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'usuarios:eliminar'
WHERE r.nombre = 'TALLER_RESPONSABLE'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

COMMIT;
