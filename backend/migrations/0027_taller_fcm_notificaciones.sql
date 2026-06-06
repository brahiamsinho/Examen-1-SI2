-- Portal taller web: push FCM + registro de dispositivo (CU19 web).
-- TALLER_RESPONSABLE ya tenía notificaciones:leer (0004); falta dispositivos:fcm.

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'dispositivos:fcm'
WHERE r.nombre = 'TALLER_RESPONSABLE'
ON CONFLICT (rol_id, permiso_id) DO NOTHING;
