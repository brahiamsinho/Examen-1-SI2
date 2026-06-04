from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.tenant_resolve import slug_from_host
from app.modules.acceso_y_administracion.public_tenants.schemas import (
    PublicTenantByHost,
    PublicTenantItem,
)
from app.modules.acceso_y_administracion.tenants.models import EstadoTenantEnum, Tenant

router = APIRouter(prefix="/public", tags=["Público — Organizaciones"])


@router.get("/tenants", response_model=list[PublicTenantItem])
async def listar_tenants_publicos(db: AsyncSession = Depends(get_db)) -> list[PublicTenantItem]:
    """Organizaciones activas visibles en login móvil/web (slug + nombre)."""
    r = await db.execute(
        select(Tenant.slug, Tenant.nombre)
        .where(Tenant.estado == EstadoTenantEnum.ACTIVO)
        .order_by(Tenant.nombre)
    )
    return [PublicTenantItem(slug=slug, nombre=nombre) for slug, nombre in r.all()]


@router.get("/tenant-by-host", response_model=PublicTenantByHost)
async def tenant_por_host(
    host: str = Query(..., min_length=3, max_length=255),
    db: AsyncSession = Depends(get_db),
) -> PublicTenantByHost:
    slug = slug_from_host(host, settings.SAAS_PLATFORM_BASE_DOMAIN)
    if not slug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host sin tenant")
    r = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.estado == EstadoTenantEnum.ACTIVO)
    )
    t = r.scalar_one_or_none()
    if t is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
    return PublicTenantByHost(slug=t.slug, nombre=t.nombre, id=t.id)
