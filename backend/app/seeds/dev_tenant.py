# Seed idempotente: tenant demo-sc (organización SaaS por defecto).
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.tenants import service as tenants_service

logger = logging.getLogger(__name__)


async def ensure_default_tenant(db: AsyncSession) -> int:
    """Crea tenant demo-sc si no existe; devuelve su id."""
    t = await tenants_service.ensure_default_tenant(db)
    logger.info("Tenant demo asegurado: slug=%s id=%s", t.slug, t.id)
    return t.id
