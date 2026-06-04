from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    EstadoTenantEnum,
    PlanTenantEnum,
)


class TenantCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    nombre: str = Field(..., min_length=2, max_length=150)
    plan: PlanTenantEnum = PlanTenantEnum.STARTER
    dominio_custom: Optional[str] = Field(None, max_length=255)


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
