"""Modelos ORM del módulo backup."""
from __future__ import annotations

import enum
from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoBackupEnum(str, enum.Enum):
    PLATAFORMA = "PLATAFORMA"
    TENANT = "TENANT"
    TALLER = "TALLER"
    EVIDENCIAS = "EVIDENCIAS"


class EstadoBackupEnum(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"
    RESTAURADO = "RESTAURADO"
    EXPIRADO = "EXPIRADO"


class FrecuenciaBackupEnum(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class BackupRegistro(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True
    )
    taller_id: Mapped[int | None] = mapped_column(
        ForeignKey("talleres.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[TipoBackupEnum] = mapped_column(SAEnum(TipoBackupEnum, name="tipo_backup"))
    archivo: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    tamano_mb: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    estado: Mapped[EstadoBackupEnum] = mapped_column(
        SAEnum(EstadoBackupEnum, name="estado_backup"),
        nullable=False,
        default=EstadoBackupEnum.PENDIENTE,
    )
    incluye_evidencias: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expira_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    creado_por_usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    error_mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)
    restaurado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    restaurado_por_usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    motivo_restore: Mapped[str | None] = mapped_column(Text, nullable=True)


class BackupConfig(Base):
    __tablename__ = "backup_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    backup_automatico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    hora_backup: Mapped[time] = mapped_column(Time, nullable=False, default=time(3, 0))
    frecuencia: Mapped[str] = mapped_column(String(10), nullable=False, default="daily")
    retencion_dias: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    incluir_evidencias: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class TallerBackupConfig(Base):
    __tablename__ = "taller_backup_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    backup_automatico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    hora_backup: Mapped[time] = mapped_column(Time, nullable=False, default=time(3, 0))
    frecuencia: Mapped[str] = mapped_column(String(10), nullable=False, default="daily")
    retencion_dias: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    ultimo_backup_auto: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
