from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PricingPlan(Base):
    __tablename__ = "pricing_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price_monthly_bob: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BOB")
    benefits: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    badge: Mapped[str | None] = mapped_column(String(80))
    cta_label: Mapped[str] = mapped_column(String(120), nullable=False)
    cta_router_link: Mapped[str | None] = mapped_column(String(255))
    cta_href: Mapped[str | None] = mapped_column(String(255))
    stripe_price_id: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime | None] = mapped_column()
    updated_at: Mapped[datetime | None] = mapped_column()
