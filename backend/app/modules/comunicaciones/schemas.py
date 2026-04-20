from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.comunicaciones.models import TipoNotificacionEnum


class FcmTokenRegisterIn(BaseModel):
    token: str = Field(..., min_length=32, max_length=512)
    platform: str | None = Field(None, max_length=20)


class NotificacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    solicitud_id: int | None
    tipo: TipoNotificacionEnum
    titulo: str
    mensaje: str
    leida: bool
    created_at: datetime
    leida_at: datetime | None


class MensajeSolicitudCreateIn(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=4000)


class MensajeSolicitudRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    solicitud_id: int
    emisor_usuario_id: int
    receptor_usuario_id: int
    mensaje: str
    created_at: datetime
    leido_at: datetime | None
