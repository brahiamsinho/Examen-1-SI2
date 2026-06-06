from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    EstadoTenantEnum,
    PlanTenantEnum,
)


def normalize_tenant_slug(value: object) -> str:
    slug = str(value or "").strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


class TenantCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    nombre: str = Field(..., min_length=2, max_length=150)
    plan: PlanTenantEnum = PlanTenantEnum.FREE
    dominio_custom: Optional[str] = Field(None, max_length=255)

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: object) -> str:
        return normalize_tenant_slug(value)

    @field_validator("nombre", mode="before")
    @classmethod
    def normalize_nombre(cls, value: object) -> str:
        return str(value or "").strip()


class TenantUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    estado: Optional[EstadoTenantEnum] = None
    plan: Optional[PlanTenantEnum] = None
    dominio_custom: Optional[str] = Field(None, max_length=255)
    subscription_status: Optional[EstadoSuscripcionTenantEnum] = None
    subscription_ends_at: Optional[datetime] = None


class TenantStripeLinkIn(BaseModel):
    stripe_customer_id: str = Field(..., min_length=3, max_length=255)


class TenantCheckoutIn(BaseModel):
    success_url: str = Field(..., min_length=8, max_length=2048)
    cancel_url: str = Field(..., min_length=8, max_length=2048)


class TenantCheckoutOut(BaseModel):
    checkout_url: str
    session_id: str


class TenantBillingPortalIn(BaseModel):
    return_url: str = Field(..., min_length=8, max_length=2048)


class TenantBillingPortalOut(BaseModel):
    portal_url: str


class TenantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    nombre: str
    estado: EstadoTenantEnum
    plan: PlanTenantEnum
    dominio_custom: Optional[str]
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: EstadoSuscripcionTenantEnum = EstadoSuscripcionTenantEnum.TRIAL
    subscription_ends_at: Optional[datetime] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
