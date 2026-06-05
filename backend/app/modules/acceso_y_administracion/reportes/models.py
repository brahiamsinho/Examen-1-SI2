"""Plantillas de reporte QBE (personalizadas y predefinidas del sistema)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportTemplate(Base):
    __tablename__ = "reportes_plantilla"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    taller_id: Mapped[int | None] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    qbe_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_system_report: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
