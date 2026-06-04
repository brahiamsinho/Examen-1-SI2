from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EstadoSuscripcionTenantEnum(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVA = "ACTIVA"
    PAST_DUE = "PAST_DUE"
    CANCELADA = "CANCELADA"
    SUSPENDIDA = "SUSPENDIDA"


class EstadoTenantEnum(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    PENDIENTE = "PENDIENTE"


class PlanTenantEnum(str, enum.Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class Tenant(Base):
    """
    Tabla: tenants
    Cliente B2B de la plataforma SaaS. Agrupa usuarios, talleres y datos operativos.
  """

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    estado: Mapped[EstadoTenantEnum] = mapped_column(
        SAEnum(EstadoTenantEnum, name="estado_tenant", create_type=False),
        nullable=False,
    )
    plan: Mapped[PlanTenantEnum] = mapped_column(
        SAEnum(PlanTenantEnum, name="plan_tenant", create_type=False),
        nullable=False,
    )
    dominio_custom: Mapped[str | None] = mapped_column(String(255))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255))
    stripe_price_id: Mapped[str | None] = mapped_column(String(255))
    subscription_status: Mapped[EstadoSuscripcionTenantEnum] = mapped_column(
        SAEnum(EstadoSuscripcionTenantEnum, name="estado_suscripcion_tenant", create_type=False),
        nullable=False,
    )
    subscription_ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
