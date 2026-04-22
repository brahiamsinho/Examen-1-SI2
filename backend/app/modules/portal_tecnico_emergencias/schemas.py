from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.emergencias.models import EstadoSolicitudSeguimientoEnum


class ServicioAsignadoRead(BaseModel):
    """Alineado a vw_servicios_asignados_tecnico (CU32)."""

    model_config = ConfigDict(from_attributes=True)

    solicitud_id: int
    tecnico_id: int
    taller_id: int | None
    estado: EstadoSolicitudSeguimientoEnum
    tiempo_estimado_min: int | None
    created_at: datetime
    updated_at: datetime
    cliente_id: int
    nombres: str
    apellidos: str
    telefono: str
    placa: str
    marca: str | None
    modelo: str | None
    tipo_vehiculo: str | None
    latitud: Decimal | None
    longitud: Decimal | None
    direccion_referencia: str | None


class UbicacionClienteActualRead(BaseModel):
    """Ubicación actual del cliente (CU33)."""

    solicitud_id: int
    latitud: Decimal
    longitud: Decimal
    precision_metros: Decimal | None
    direccion_referencia: str | None
    registrado_at: datetime


class ActualizarEstadoServicioIn(BaseModel):
    nuevo_estado: EstadoSolicitudSeguimientoEnum
    observacion: str | None = Field(default=None, max_length=2000)
