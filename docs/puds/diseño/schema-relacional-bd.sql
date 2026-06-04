-- =============================================================================
-- DISEÑO RELACIONAL DE LA BASE DE DATOS
-- Proyecto: Plataforma de Emergencias Vehiculares (Examen SI2)
-- Motor:    PostgreSQL 15+
-- Fuente:   backend/migrations/*.sql (estado consolidado)
-- Uso:      artefacto PUDS 4.3.3 | diagrama ER | crear esquema vacío
--
-- NOTA:
--   - Solo DDL (tipos, tablas, FK, índices). Sin datos seed.
--   - Políticas RLS multi-tenant: ver 0016_multitenancy_phase2.sql
--   - Vistas operativas: ver 0008 y 0010
-- =============================================================================

BEGIN;

-- =============================================================================
-- TIPOS ENUM
-- =============================================================================

CREATE TYPE estado_usuario AS ENUM (
    'ACTIVO', 'INACTIVO', 'BLOQUEADO', 'PENDIENTE'
);

CREATE TYPE estado_sesion AS ENUM (
    'ACTIVA', 'CERRADA', 'EXPIRADA', 'REVOCADA'
);

CREATE TYPE estado_taller AS ENUM (
    'ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'PENDIENTE'
);

CREATE TYPE estado_tecnico AS ENUM (
    'ACTIVO', 'INACTIVO'
);

CREATE TYPE accion_bitacora AS ENUM (
    'CREAR', 'ACTUALIZAR', 'ELIMINAR', 'INICIAR_SESION', 'CERRAR_SESION',
    'RESTABLECER_CONTRASENA', 'ASIGNAR_ROL', 'ASIGNAR_PERMISO', 'CONSULTAR'
);

CREATE TYPE estado_solicitud_seguimiento AS ENUM (
    'REGISTRADA', 'EN_REVISION', 'TALLER_ASIGNADO', 'TECNICO_ASIGNADO',
    'EN_CAMINO', 'EN_ATENCION', 'FINALIZADA', 'CANCELADA'
);

CREATE TYPE tipo_evidencia_solicitud AS ENUM (
    'FOTO', 'AUDIO'
);

CREATE TYPE tipo_notificacion AS ENUM (
    'SOLICITUD_CREADA', 'ESTADO_ACTUALIZADO', 'TALLER_ASIGNADO',
    'TECNICO_ASIGNADO', 'MENSAJE_NUEVO'
);

CREATE TYPE estado_pago AS ENUM (
    'PENDIENTE', 'PAGADO', 'FALLIDO', 'ANULADO'
);

CREATE TYPE metodo_pago AS ENUM (
    'QR', 'TARJETA', 'TRANSFERENCIA', 'EFECTIVO', 'OTRO'
);

CREATE TYPE estado_bandeja_taller AS ENUM (
    'PENDIENTE', 'ACEPTADA', 'RECHAZADA', 'EXPIRADA'
);

CREATE TYPE estado_asignacion_tecnico AS ENUM (
    'ASIGNADO', 'REASIGNADO', 'CANCELADO'
);

CREATE TYPE estado_comision_taller AS ENUM (
    'PENDIENTE', 'CALCULADA', 'LIQUIDADA', 'ANULADA'
);

CREATE TYPE estado_tenant AS ENUM (
    'ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'PENDIENTE'
);

CREATE TYPE plan_tenant AS ENUM (
    'FREE', 'STARTER', 'PRO', 'ENTERPRISE'
);

CREATE TYPE estado_suscripcion_tenant AS ENUM (
    'TRIAL', 'ACTIVA', 'PAST_DUE', 'CANCELADA', 'SUSPENDIDA'
);

-- =============================================================================
-- MULTI-TENANCY (SaaS)
-- =============================================================================

CREATE TABLE tenants (
    id                      SERIAL PRIMARY KEY,
    slug                    VARCHAR(80) NOT NULL UNIQUE,
    nombre                  VARCHAR(150) NOT NULL,
    estado                  estado_tenant NOT NULL DEFAULT 'ACTIVO',
    plan                    plan_tenant NOT NULL DEFAULT 'STARTER',
    dominio_custom          VARCHAR(255),
    stripe_customer_id      VARCHAR(255),
    stripe_subscription_id  VARCHAR(255),
    stripe_price_id         VARCHAR(255),
    subscription_status     estado_suscripcion_tenant DEFAULT 'TRIAL',
    subscription_ends_at    TIMESTAMP,
    created_at              TIMESTAMP,
    updated_at              TIMESTAMP
);

CREATE INDEX ix_tenants_slug ON tenants (slug);
CREATE INDEX ix_tenants_estado ON tenants (estado);
CREATE INDEX ix_tenants_stripe_customer ON tenants (stripe_customer_id)
    WHERE stripe_customer_id IS NOT NULL;
CREATE INDEX ix_tenants_stripe_subscription ON tenants (stripe_subscription_id)
    WHERE stripe_subscription_id IS NOT NULL;

-- =============================================================================
-- SEGURIDAD Y ACCESO (RBAC)
-- =============================================================================

CREATE TABLE roles (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL UNIQUE,
    descripcion     VARCHAR(255),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);

CREATE TABLE permisos (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo          VARCHAR(80) NOT NULL UNIQUE,
    nombre          VARCHAR(80) NOT NULL,
    modulo          VARCHAR(80) NOT NULL,
    descripcion     VARCHAR(255),
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);

CREATE TABLE usuarios (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id           INTEGER REFERENCES tenants(id) ON DELETE RESTRICT,
    nombres             VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL,
    username            VARCHAR(50) UNIQUE,
    email               VARCHAR(120) NOT NULL,
    telefono            VARCHAR(30) NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    estado              estado_usuario NOT NULL,
    ultimo_acceso_at    TIMESTAMP,
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP
);

CREATE UNIQUE INDEX uq_usuarios_tenant_email
    ON usuarios (tenant_id, lower(email))
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX uq_usuarios_platform_email
    ON usuarios (lower(email))
    WHERE tenant_id IS NULL;

CREATE UNIQUE INDEX uq_usuarios_tenant_telefono
    ON usuarios (tenant_id, telefono)
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX uq_usuarios_platform_telefono
    ON usuarios (telefono)
    WHERE tenant_id IS NULL;

CREATE INDEX ix_usuarios_tenant_id ON usuarios (tenant_id);

CREATE TABLE rol_permiso (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol_id          INTEGER NOT NULL,
    permiso_id      INTEGER NOT NULL,
    created_at      TIMESTAMP,
    CONSTRAINT uq_rol_permiso UNIQUE (rol_id, permiso_id),
    CONSTRAINT fk_rol_permiso_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_rol_permiso_permiso
        FOREIGN KEY (permiso_id) REFERENCES permisos(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE usuario_rol (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    rol_id          INTEGER NOT NULL,
    asignado_at     TIMESTAMP,
    CONSTRAINT uq_usuario_rol UNIQUE (usuario_id, rol_id),
    CONSTRAINT fk_usuario_rol_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_rol_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE sesiones (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    token_jti       VARCHAR(255) NOT NULL UNIQUE,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    dispositivo     VARCHAR(100),
    plataforma      VARCHAR(50),
    iniciado_at     TIMESTAMP NOT NULL,
    cerrado_at      TIMESTAMP,
    expira_at       TIMESTAMP,
    estado          estado_sesion NOT NULL,
    CONSTRAINT fk_sesiones_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE usuario_tokens_seguridad (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    tipo            VARCHAR(32) NOT NULL,
    token_hash      CHAR(64) NOT NULL,
    expires_at      TIMESTAMP NOT NULL,
    usado_at        TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_usuario_token_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT ck_usuario_token_tipo
        CHECK (tipo IN ('VERIFICAR_EMAIL', 'RESTABLECER_PASSWORD'))
);

CREATE TABLE usuario_fcm_tokens (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id  INTEGER NOT NULL,
    token       TEXT NOT NULL,
    platform    VARCHAR(20),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_fcm_tokens_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_usuario_fcm_token UNIQUE (token)
);

-- =============================================================================
-- ACTORES DE DOMINIO
-- =============================================================================

CREATE TABLE clientes (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id       INTEGER REFERENCES tenants(id) ON DELETE RESTRICT,
    usuario_id      INTEGER NOT NULL UNIQUE,
    ciudad          VARCHAR(100),
    direccion       TEXT,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    CONSTRAINT fk_clientes_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_clientes_tenant_id ON clientes (tenant_id);

CREATE TABLE talleres (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id               INTEGER REFERENCES tenants(id) ON DELETE RESTRICT,
    usuario_responsable_id  INTEGER NOT NULL UNIQUE,
    nombre_comercial        VARCHAR(150) NOT NULL,
    telefono_contacto       VARCHAR(30) NOT NULL,
    email_contacto          VARCHAR(120) NOT NULL,
    direccion               TEXT NOT NULL,
    ciudad                  VARCHAR(100) NOT NULL,
    latitud                 NUMERIC(10, 7),
    longitud                NUMERIC(10, 7),
    descripcion             TEXT,
    estado                  estado_taller NOT NULL,
    created_at              TIMESTAMP,
    updated_at              TIMESTAMP,
    CONSTRAINT fk_talleres_usuario_responsable
        FOREIGN KEY (usuario_responsable_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX ix_talleres_tenant_id ON talleres (tenant_id);

CREATE TABLE especialidades_tecnico (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL UNIQUE,
    descripcion     VARCHAR(255)
);

CREATE TABLE tecnicos (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id          INTEGER NOT NULL UNIQUE,
    taller_id           INTEGER NOT NULL,
    especialidad_id     INTEGER,
    documento_identidad VARCHAR(50),
    disponibilidad      VARCHAR(120),
    estado              estado_tecnico NOT NULL,
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP,
    CONSTRAINT fk_tecnicos_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_tecnicos_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_tecnicos_especialidad
        FOREIGN KEY (especialidad_id) REFERENCES especialidades_tecnico(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- =============================================================================
-- VEHÍCULOS
-- =============================================================================

CREATE TABLE marcas_vehiculo (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE modelos_vehiculo (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    marca_id        INTEGER NOT NULL,
    nombre          VARCHAR(80) NOT NULL,
    CONSTRAINT uq_modelos_vehiculo UNIQUE (marca_id, nombre),
    CONSTRAINT fk_modelos_vehiculo_marca
        FOREIGN KEY (marca_id) REFERENCES marcas_vehiculo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE tipos_vehiculo (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE vehiculos (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id           INTEGER REFERENCES tenants(id) ON DELETE RESTRICT,
    cliente_id          INTEGER NOT NULL,
    placa               VARCHAR(20) NOT NULL,
    marca_id            INTEGER NOT NULL,
    modelo_id           INTEGER NOT NULL,
    tipo_vehiculo_id    INTEGER NOT NULL,
    anio                INTEGER,
    color               VARCHAR(50),
    created_at          TIMESTAMP,
    updated_at          TIMESTAMP,
    CONSTRAINT fk_vehiculos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_vehiculos_marca
        FOREIGN KEY (marca_id) REFERENCES marcas_vehiculo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_vehiculos_modelo
        FOREIGN KEY (modelo_id) REFERENCES modelos_vehiculo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_vehiculos_tipo
        FOREIGN KEY (tipo_vehiculo_id) REFERENCES tipos_vehiculo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE UNIQUE INDEX uq_vehiculos_tenant_placa
    ON vehiculos (tenant_id, lower(placa))
    WHERE tenant_id IS NOT NULL;

CREATE UNIQUE INDEX uq_vehiculos_platform_placa
    ON vehiculos (lower(placa))
    WHERE tenant_id IS NULL;

CREATE INDEX ix_vehiculos_tenant_id ON vehiculos (tenant_id);

-- =============================================================================
-- EMERGENCIAS Y SEGUIMIENTO
-- =============================================================================

CREATE TABLE solicitudes_emergencia (
    id                          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id                   INTEGER REFERENCES tenants(id) ON DELETE RESTRICT,
    cliente_id                  INTEGER NOT NULL,
    vehiculo_id                 INTEGER NOT NULL,
    taller_id                   INTEGER,
    tecnico_id                  INTEGER,
    estado                      estado_solicitud_seguimiento NOT NULL DEFAULT 'REGISTRADA',
    descripcion_texto           TEXT,
    tiempo_estimado_min         INTEGER,
    presupuesto_bob             NUMERIC(12, 2),
    presupuesto_registrado_at   TIMESTAMP,
    ai_payload                  JSONB,
    tecnico_ult_latitud         NUMERIC(10, 7),
    tecnico_ult_longitud        NUMERIC(10, 7),
    tecnico_ult_precision_metros NUMERIC(8, 2),
    tecnico_ult_ubicacion_at    TIMESTAMP,
    tecnico_asignado_at         TIMESTAMP,
    finalizada_at               TIMESTAMP,
    created_at                  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_solicitudes_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_solicitudes_vehiculo
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_solicitudes_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_solicitudes_tecnico
        FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX ix_solicitudes_emergencia_tenant_id ON solicitudes_emergencia (tenant_id);
CREATE INDEX idx_solicitudes_cliente_id ON solicitudes_emergencia (cliente_id);
CREATE INDEX idx_solicitudes_vehiculo_id ON solicitudes_emergencia (vehiculo_id);
CREATE INDEX idx_solicitudes_taller_id ON solicitudes_emergencia (taller_id);
CREATE INDEX idx_solicitudes_tecnico_id ON solicitudes_emergencia (tecnico_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes_emergencia (estado);

CREATE TABLE solicitud_ubicaciones (
    id                    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id          INTEGER NOT NULL,
    latitud               NUMERIC(10, 7) NOT NULL,
    longitud              NUMERIC(10, 7) NOT NULL,
    precision_metros      NUMERIC(8, 2),
    direccion_referencia  TEXT,
    es_actual             BOOLEAN NOT NULL DEFAULT FALSE,
    registrado_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_solicitud_ubicaciones_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_solicitud_ubicacion_actual
    ON solicitud_ubicaciones (solicitud_id)
    WHERE es_actual = TRUE;

CREATE TABLE solicitud_evidencias (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id    INTEGER NOT NULL,
    tipo            tipo_evidencia_solicitud NOT NULL,
    archivo_url     TEXT NOT NULL,
    mime_type       VARCHAR(100),
    nombre_archivo  VARCHAR(255),
    tamano_bytes    BIGINT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_solicitud_evidencias_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE solicitud_historial_estado (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id        INTEGER NOT NULL,
    estado_anterior     estado_solicitud_seguimiento,
    estado_nuevo        estado_solicitud_seguimiento NOT NULL,
    usuario_id          INTEGER,
    observacion         TEXT,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historial_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_historial_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- =============================================================================
-- COMUNICACIONES
-- =============================================================================

CREATE TABLE notificaciones (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      INTEGER NOT NULL,
    solicitud_id    INTEGER,
    tipo            tipo_notificacion NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    mensaje         TEXT NOT NULL,
    leida           BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    leida_at        TIMESTAMP,
    CONSTRAINT fk_notificaciones_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_notificaciones_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE solicitud_mensajes (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id        INTEGER NOT NULL,
    emisor_usuario_id   INTEGER NOT NULL,
    receptor_usuario_id INTEGER NOT NULL,
    mensaje             TEXT NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    leido_at            TIMESTAMP,
    CONSTRAINT fk_mensajes_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_mensajes_emisor
        FOREIGN KEY (emisor_usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mensajes_receptor
        FOREIGN KEY (receptor_usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- =============================================================================
-- OPERACIÓN DE TALLER
-- =============================================================================

CREATE TABLE taller_disponibilidad (
    id                          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    taller_id                   INTEGER NOT NULL UNIQUE,
    acepta_nuevas_solicitudes   BOOLEAN NOT NULL DEFAULT TRUE,
    capacidad_maxima_diaria     INTEGER NOT NULL DEFAULT 10,
    servicios_activos           INTEGER NOT NULL DEFAULT 0,
    observacion                 TEXT,
    updated_by_usuario_id       INTEGER,
    updated_at                  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_taller_disponibilidad_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_taller_disponibilidad_usuario
        FOREIGN KEY (updated_by_usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE solicitud_taller_bandeja (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id        INTEGER NOT NULL,
    taller_id           INTEGER NOT NULL,
    estado              estado_bandeja_taller NOT NULL DEFAULT 'PENDIENTE',
    motivo_rechazo      TEXT,
    creado_at           TIMESTAMP NOT NULL DEFAULT NOW(),
    respondido_at       TIMESTAMP,
    CONSTRAINT uq_solicitud_taller_bandeja UNIQUE (solicitud_id, taller_id),
    CONSTRAINT fk_bandeja_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_bandeja_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE solicitud_asignaciones_tecnico (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id            INTEGER NOT NULL,
    taller_id               INTEGER NOT NULL,
    tecnico_id              INTEGER NOT NULL,
    estado                  estado_asignacion_tecnico NOT NULL DEFAULT 'ASIGNADO',
    asignado_por_usuario_id INTEGER,
    observacion             TEXT,
    created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_asignacion_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_asignacion_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_asignacion_tecnico
        FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_asignacion_usuario
        FOREIGN KEY (asignado_por_usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- =============================================================================
-- FINANZAS
-- =============================================================================

CREATE TABLE pagos (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id        INTEGER NOT NULL,
    cliente_id          INTEGER NOT NULL,
    monto               NUMERIC(10, 2) NOT NULL,
    moneda              CHAR(3) NOT NULL DEFAULT 'BOB',
    metodo              metodo_pago NOT NULL,
    estado              estado_pago NOT NULL DEFAULT 'PENDIENTE',
    referencia_externa  VARCHAR(255),
    proveedor           VARCHAR(32) NOT NULL DEFAULT 'SIMULADO',
    metadata_json       JSONB,
    conciliado_at       TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    pagado_at           TIMESTAMP,
    CONSTRAINT fk_pagos_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pagos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE UNIQUE INDEX ux_pagos_un_pagado_por_solicitud
    ON pagos (solicitud_id)
    WHERE estado = 'PAGADO';

CREATE TABLE comisiones_taller (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitud_id            INTEGER NOT NULL UNIQUE,
    taller_id               INTEGER NOT NULL,
    pago_id                 INTEGER UNIQUE,
    porcentaje_plataforma   NUMERIC(5, 2) NOT NULL DEFAULT 10.00,
    monto_servicio          NUMERIC(10, 2) NOT NULL,
    monto_comision          NUMERIC(10, 2) NOT NULL,
    monto_taller_neto       NUMERIC(10, 2) NOT NULL,
    estado                  estado_comision_taller NOT NULL DEFAULT 'PENDIENTE',
    calculado_at            TIMESTAMP NOT NULL DEFAULT NOW(),
    liquidado_at            TIMESTAMP,
    CONSTRAINT fk_comision_solicitud
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_emergencia(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_comision_taller
        FOREIGN KEY (taller_id) REFERENCES talleres(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_comision_pago
        FOREIGN KEY (pago_id) REFERENCES pagos(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- =============================================================================
-- AUDITORÍA
-- =============================================================================

CREATE TABLE bitacora (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      INTEGER,
    modulo          VARCHAR(100) NOT NULL,
    entidad         VARCHAR(100) NOT NULL,
    entidad_id      INTEGER,
    accion          accion_bitacora NOT NULL,
    descripcion     TEXT,
    ip_address      VARCHAR(45),
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT fk_bitacora_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- =============================================================================
-- ÍNDICES DE APOYO
-- =============================================================================

CREATE INDEX idx_rol_permiso_rol_id ON rol_permiso (rol_id);
CREATE INDEX idx_rol_permiso_permiso_id ON rol_permiso (permiso_id);
CREATE INDEX idx_usuario_rol_usuario_id ON usuario_rol (usuario_id);
CREATE INDEX idx_usuario_rol_rol_id ON usuario_rol (rol_id);
CREATE INDEX idx_sesiones_usuario_id ON sesiones (usuario_id);
CREATE INDEX idx_clientes_usuario_id ON clientes (usuario_id);
CREATE INDEX idx_talleres_usuario_responsable_id ON talleres (usuario_responsable_id);
CREATE INDEX idx_tecnicos_usuario_id ON tecnicos (usuario_id);
CREATE INDEX idx_tecnicos_taller_id ON tecnicos (taller_id);
CREATE INDEX idx_tecnicos_especialidad_id ON tecnicos (especialidad_id);
CREATE INDEX idx_modelos_vehiculo_marca_id ON modelos_vehiculo (marca_id);
CREATE INDEX idx_vehiculos_cliente_id ON vehiculos (cliente_id);
CREATE INDEX idx_vehiculos_marca_id ON vehiculos (marca_id);
CREATE INDEX idx_vehiculos_modelo_id ON vehiculos (modelo_id);
CREATE INDEX idx_vehiculos_tipo_vehiculo_id ON vehiculos (tipo_vehiculo_id);
CREATE INDEX idx_solicitud_ubicaciones_solicitud_id ON solicitud_ubicaciones (solicitud_id);
CREATE INDEX idx_solicitud_evidencias_solicitud_id ON solicitud_evidencias (solicitud_id);
CREATE INDEX idx_historial_estado_solicitud_id ON solicitud_historial_estado (solicitud_id);
CREATE INDEX idx_notificaciones_usuario_id ON notificaciones (usuario_id);
CREATE INDEX idx_notificaciones_solicitud_id ON notificaciones (solicitud_id);
CREATE INDEX idx_mensajes_solicitud_id ON solicitud_mensajes (solicitud_id);
CREATE INDEX idx_usuario_fcm_tokens_usuario_id ON usuario_fcm_tokens (usuario_id);
CREATE INDEX idx_usuario_tokens_lookup ON usuario_tokens_seguridad (tipo, token_hash);
CREATE INDEX idx_pagos_solicitud_id ON pagos (solicitud_id);
CREATE INDEX idx_comision_taller_id ON comisiones_taller (taller_id);
CREATE INDEX idx_bitacora_usuario_id ON bitacora (usuario_id);
CREATE INDEX idx_bitacora_modulo ON bitacora (modulo);
CREATE INDEX idx_bitacora_created_at ON bitacora (created_at);

COMMIT;
