-- Horarios de atención por taller (día de semana + franja horaria, configurable por responsable).
BEGIN;

CREATE TABLE IF NOT EXISTS taller_horarios (
    id SERIAL PRIMARY KEY,
    taller_id INTEGER NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
    dia_semana SMALLINT NOT NULL CHECK (dia_semana >= 0 AND dia_semana <= 6),
    hora_apertura TIME NOT NULL,
    hora_cierre TIME NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT uq_taller_horarios_dia UNIQUE (taller_id, dia_semana),
    CONSTRAINT ck_taller_horarios_franja CHECK (hora_apertura < hora_cierre)
);

CREATE INDEX IF NOT EXISTS ix_taller_horarios_taller_id ON taller_horarios (taller_id);

COMMIT;
