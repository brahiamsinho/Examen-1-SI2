-- Portal taller: CRUD de cuentas clientes para TALLER_RESPONSABLE.
BEGIN;

INSERT INTO permisos (codigo, nombre, modulo, descripcion, created_at, updated_at)
SELECT v.codigo, v.nombre, v.modulo, v.descripcion, NOW(), NOW()
FROM (VALUES
    ('clientes:crear', 'Crear cuentas de clientes', 'clientes', 'Alta manual de clientes en la organización del taller'),
    ('clientes:actualizar', 'Editar cuentas de clientes', 'clientes', 'Actualizar datos y estado de clientes del taller'),
    ('clientes:eliminar', 'Eliminar cuentas de clientes', 'clientes', 'Eliminación física de clientes sin historial operativo')
) AS v(codigo, nombre, modulo, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM permisos p WHERE p.codigo = v.codigo);

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo IN (
    'clientes:crear',
    'clientes:actualizar',
    'clientes:eliminar'
)
WHERE r.nombre = 'TALLER_RESPONSABLE'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo IN (
    'clientes:crear',
    'clientes:actualizar',
    'clientes:eliminar',
    'clientes:leer'
)
WHERE r.nombre = 'ADMIN'
  AND NOT EXISTS (
    SELECT 1 FROM rol_permiso rp WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
  );

COMMIT;
