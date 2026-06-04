from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.tenants.models import (
    EstadoSuscripcionTenantEnum,
    EstadoTenantEnum,
    PlanTenantEnum,
    Tenant,
)
from app.modules.acceso_y_administracion.tenants.schemas import normalize_tenant_slug

DEFAULT_TENANT_SLUG = "demo-sc"


async def get_tenant_by_id(db: AsyncSession, tenant_id: int) -> Tenant:
    r = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    t = r.scalar_one_or_none()
    if t is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant no encontrado")
    return t


async def get_tenant_by_slug(db: AsyncSession, slug: str) -> Tenant | None:
    r = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return r.scalar_one_or_none()


async def list_tenants(db: AsyncSession) -> list[Tenant]:
    r = await db.execute(select(Tenant).order_by(Tenant.nombre))
    return list(r.scalars().all())


async def ensure_default_tenant(db: AsyncSession) -> Tenant:
    existing = await get_tenant_by_slug(db, DEFAULT_TENANT_SLUG)
    if existing is not None:
        return existing
    now = utc_now_naive()
    t = Tenant(
        slug=DEFAULT_TENANT_SLUG,
        nombre="Demo Santa Cruz (legacy)",
        estado=EstadoTenantEnum.ACTIVO,
        plan=PlanTenantEnum.STARTER,
        subscription_status=EstadoSuscripcionTenantEnum.TRIAL,
        created_at=now,
        updated_at=now,
    )
    db.add(t)
    await db.flush()
    return t


async def create_tenant(db: AsyncSession, data: dict) -> Tenant:
    slug = normalize_tenant_slug(data["slug"])
    dup = await get_tenant_by_slug(db, slug)
    if dup is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug de tenant ya existe")
    now = utc_now_naive()
    t = Tenant(
        slug=slug,
        nombre=data["nombre"],
        estado=EstadoTenantEnum.ACTIVO,
        plan=data.get("plan", PlanTenantEnum.STARTER),
        dominio_custom=data.get("dominio_custom"),
        subscription_status=EstadoSuscripcionTenantEnum.TRIAL,
        created_at=now,
        updated_at=now,
    )
    db.add(t)
    await db.flush()
    return t


async def link_stripe_customer(
    db: AsyncSession, tenant_id: int, stripe_customer_id: str
) -> Tenant:
    t = await get_tenant_by_id(db, tenant_id)
    t.stripe_customer_id = stripe_customer_id.strip()
    t.subscription_status = EstadoSuscripcionTenantEnum.ACTIVA
    t.updated_at = utc_now_naive()
    return t


async def update_tenant(db: AsyncSession, tenant_id: int, data: dict) -> Tenant:
    t = await get_tenant_by_id(db, tenant_id)
    for key, value in data.items():
        if value is not None:
            setattr(t, key, value)
    t.updated_at = utc_now_naive()
    return t
