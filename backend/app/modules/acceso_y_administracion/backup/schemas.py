"""Schemas Pydantic del módulo backup."""
from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.modules.acceso_y_administracion.backup.models import (
    EstadoBackupEnum,
    FrecuenciaBackupEnum,
    TipoBackupEnum,
)


class BackupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: Optional[int]
    taller_id: Optional[int] = None
    tenant_slug: Optional[str] = None
    tenant_nombre: Optional[str] = None
    tipo: TipoBackupEnum
    archivo: str
    tamano_mb: Optional[float]
    estado: EstadoBackupEnum
    incluye_evidencias: bool
    creado_en: datetime
    expira_en: Optional[datetime]
    creado_por_usuario_id: Optional[int]
    error_mensaje: Optional[str]
    restaurado_en: Optional[datetime]
    restaurado_por_usuario_id: Optional[int]
    motivo_restore: Optional[str]


class BackupCreateIn(BaseModel):
    tipo: TipoBackupEnum = TipoBackupEnum.PLATAFORMA
    tenant_id: Optional[int] = Field(
        None,
        description="Obligatorio si tipo=TENANT. Export lógico del tenant (shared schema).",
    )
    incluir_evidencias: bool = False


class BackupRestoreIn(BaseModel):
    confirmar: bool = Field(..., description="Debe ser true para restaurar")
    motivo: str = Field(..., min_length=3, max_length=500)


class BackupConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    backup_automatico: bool
    hora_backup: time
    frecuencia: str
    retencion_dias: int
    incluir_evidencias: bool
    actualizado_en: datetime


class BackupConfigUpdate(BaseModel):
    backup_automatico: Optional[bool] = None
    hora_backup: Optional[time] = None
    frecuencia: Optional[FrecuenciaBackupEnum] = None
    retencion_dias: Optional[int] = Field(None, ge=1, le=365)
    incluir_evidencias: Optional[bool] = None


class TallerBackupConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    taller_id: int
    backup_automatico: bool
    hora_backup: time
    frecuencia: str
    retencion_dias: int
    ultimo_backup_auto: Optional[datetime]
    actualizado_en: datetime


class TallerBackupConfigUpdate(BaseModel):
    backup_automatico: Optional[bool] = None
    hora_backup: Optional[time] = None
    frecuencia: Optional[FrecuenciaBackupEnum] = None
    retencion_dias: Optional[int] = Field(None, ge=1, le=90)
