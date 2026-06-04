from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.modules.acceso_y_administracion.bitacora.schemas import BitacoraRead


class AdminPanelOverview(BaseModel):
    total_usuarios: int
    total_talleres: int
    total_roles: int
    actividad_reciente: list[BitacoraRead]
