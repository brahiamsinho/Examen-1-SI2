-- =========================================================
-- CU43/CU45 — Idempotencia al crear solicitud desde mobile offline.
-- client_request_id: UUID generado en el dispositivo; replay seguro.
-- =========================================================

BEGIN;

ALTER TABLE solicitudes_emergencia
    ADD COLUMN IF NOT EXISTS client_request_id UUID NULL;

COMMENT ON COLUMN solicitudes_emergencia.client_request_id IS
    'UUID del cliente para idempotencia al sincronizar borradores offline (CU43/CU45).';

CREATE UNIQUE INDEX IF NOT EXISTS uq_solicitudes_cliente_client_request_id
    ON solicitudes_emergencia (cliente_id, client_request_id)
    WHERE client_request_id IS NOT NULL;

COMMIT;
