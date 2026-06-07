-- =========================================================
-- Notificaciones inmediatas: idempotencia por evento_id + permiso FCM taller.
-- Paquete: comunicacion_y_notificaciones / seguimiento tiempo real.
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'tipo_notificacion'
          AND e.enumlabel = 'SOLICITUD_PENDIENTE_TALLER'
    ) THEN
        ALTER TYPE tipo_notificacion ADD VALUE 'SOLICITUD_PENDIENTE_TALLER';
    END IF;
END$$;

ALTER TABLE notificaciones
    ADD COLUMN IF NOT EXISTS evento_id VARCHAR(120);

CREATE UNIQUE INDEX IF NOT EXISTS uq_notificaciones_evento_id
    ON notificaciones(evento_id)
    WHERE evento_id IS NOT NULL;

INSERT INTO rol_permiso (rol_id, permiso_id, created_at)
SELECT r.id, p.id, NOW()
FROM roles r
JOIN permisos p ON p.codigo = 'dispositivos:fcm'
WHERE r.nombre = 'TALLER_RESPONSABLE'
ON CONFLICT (rol_id, permiso_id) DO NOTHING;
