from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, get_auth_context, require_platform_superadmin
from app.core.tenant import AuthContext
from app.modules.acceso_y_administracion.tenants import service
from app.modules.acceso_y_administracion.billing import service as billing_service
from app.modules.acceso_y_administracion.tenants.schemas import (
    TenantBillingPortalIn,
    TenantBillingPortalOut,
    TenantCheckoutIn,
    TenantCheckoutOut,
    TenantCreate,
    TenantRead,
    TenantStripeLinkIn,
    TenantUpdate,
)

router = APIRouter(prefix="/admin/tenants", tags=["Admin - Tenants SaaS"])


@router.get("", response_model=list[TenantRead])
async def listar_tenants(
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> list[TenantRead]:
    rows = await service.list_tenants(db)
    return [TenantRead.model_validate(r) for r in rows]


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def crear_tenant(
    body: TenantCreate,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantRead:
    row = await service.create_tenant(db, body.model_dump())
    return TenantRead.model_validate(row)


@router.get("/context/me", response_model=dict)
async def mi_contexto_tenant(
    ctx: AuthContext = Depends(bind_auth_context),
) -> dict:
    """Devuelve tenant_id y si el usuario es superadmin de plataforma (útil para frontends)."""
    return {
        "tenant_id": ctx.tenant_id,
        "is_platform_superadmin": ctx.is_platform_superadmin,
        "roles": ctx.roles,
    }


@router.get("/{tenant_id}", response_model=TenantRead)
async def obtener_tenant(
    tenant_id: int,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantRead:
    row = await service.get_tenant_by_id(db, tenant_id)
    return TenantRead.model_validate(row)


@router.patch("/{tenant_id}", response_model=TenantRead)
async def actualizar_tenant(
    tenant_id: int,
    body: TenantUpdate,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantRead:
    row = await service.update_tenant(
        db,
        tenant_id,
        body.model_dump(exclude_unset=True),
    )
    return TenantRead.model_validate(row)


@router.post("/{tenant_id}/stripe-customer", response_model=TenantRead)
async def vincular_stripe_customer(
    tenant_id: int,
    body: TenantStripeLinkIn,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantRead:
    """Registra el id de cliente Stripe del tenant (suscripción SaaS; distinto de pagos de emergencias)."""
    row = await service.link_stripe_customer(db, tenant_id, body.stripe_customer_id)
    return TenantRead.model_validate(row)


@router.post("/{tenant_id}/checkout-session", response_model=TenantCheckoutOut)
async def crear_checkout_suscripcion(
    tenant_id: int,
    body: TenantCheckoutIn,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantCheckoutOut:
    data = await billing_service.crear_checkout_session(
        db,
        tenant_id,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )
    return TenantCheckoutOut(checkout_url=data["url"], session_id=data["id"])


@router.post("/{tenant_id}/billing-portal", response_model=TenantBillingPortalOut)
async def portal_facturacion(
    tenant_id: int,
    body: TenantBillingPortalIn,
    _ctx: AuthContext = Depends(require_platform_superadmin),
    db: AsyncSession = Depends(get_db),
) -> TenantBillingPortalOut:
    data = await billing_service.crear_billing_portal(db, tenant_id, return_url=body.return_url)
    return TenantBillingPortalOut(portal_url=data["url"])
