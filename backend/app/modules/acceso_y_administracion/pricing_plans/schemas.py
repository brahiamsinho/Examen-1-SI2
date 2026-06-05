from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PricingPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: Optional[str] = None
    price_monthly_bob: Decimal
    currency: str
    benefits: list[str]
    featured: bool
    badge: Optional[str] = None
    cta_label: str
    cta_router_link: Optional[str] = None
    cta_href: Optional[str] = None
    stripe_price_id: Optional[str] = None
    sort_order: int
    active: bool


class PricingPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price_monthly_bob: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    benefits: Optional[list[str]] = None
    featured: Optional[bool] = None
    badge: Optional[str] = Field(None, max_length=80)
    cta_label: Optional[str] = Field(None, min_length=1, max_length=120)
    cta_router_link: Optional[str] = Field(None, max_length=255)
    cta_href: Optional[str] = Field(None, max_length=255)
    stripe_price_id: Optional[str] = Field(None, max_length=255)
    sort_order: Optional[int] = None
    active: Optional[bool] = None


class StripeConfigPublicRead(BaseModel):
    enabled: bool
    publishable_key: Optional[str] = None


class PublicPricingBootstrapRead(BaseModel):
    """Planes + Stripe en una sola respuesta para la landing."""

    plans: list[PricingPlanRead]
    stripe: StripeConfigPublicRead


class PublicCheckoutIn(BaseModel):
    plan_slug: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    success_url: str = Field(..., min_length=8, max_length=2048)
    cancel_url: str = Field(..., min_length=8, max_length=2048)


class CheckoutOut(BaseModel):
    checkout_url: str
    session_id: str
