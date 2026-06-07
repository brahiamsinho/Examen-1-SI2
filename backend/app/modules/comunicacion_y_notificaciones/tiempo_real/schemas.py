# Envelope JSON de eventos en tiempo real por solicitud.
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RealtimeEventType(str, Enum):
    ESTADO_INCIDENTE = "estado_incidente"
    UBICACION_TECNICO = "ubicacion_tecnico"
    MENSAJE_NUEVO = "mensaje_nuevo"
    BANDEJA_ACTUALIZADA = "bandeja_actualizada"
    TECNICO_ASIGNADO = "tecnico_asignado"
    SEGUIMIENTO_ACTUALIZADO = "seguimiento_actualizado"
    TALLER_SELECCIONADO = "taller_seleccionado"
    PAGO_CONFIRMADO = "pago_confirmado"


class RealtimeEventEnvelope(BaseModel):
    tipo: RealtimeEventType
    solicitud_id: int
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime

    def to_ws_json(self) -> dict[str, Any]:
        return {
            "tipo": self.tipo.value,
            "solicitud_id": self.solicitud_id,
            "payload": self.payload,
            "occurred_at": self.occurred_at.isoformat(),
        }
