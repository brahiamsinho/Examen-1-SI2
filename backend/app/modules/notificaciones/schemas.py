from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.notificaciones.models import TipoNotificacionEnum


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
