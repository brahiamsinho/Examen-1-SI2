from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.bitacora.models import Bitacora
from app.modules.acceso_y_administracion.roles.models import Rol
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.talleres_y_tecnicos.talleres.models import Taller


async def _count_usuarios(db: AsyncSession, tenant_id: int | None) -> int:
    stmt = select(func.count()).select_from(Usuario)
    if tenant_id is not None:
        stmt = stmt.where(Usuario.tenant_id == tenant_id)
    return int((await db.execute(stmt)).scalar_one() or 0)


async def _count_talleres(db: AsyncSession, tenant_id: int | None) -> int:
    stmt = select(func.count()).select_from(Taller)
    if tenant_id is not None:
        stmt = stmt.where(Taller.tenant_id == tenant_id)
    return int((await db.execute(stmt)).scalar_one() or 0)


async def _count_roles(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Rol)
    return int((await db.execute(stmt)).scalar_one() or 0)


async def _bitacora_reciente(
    db: AsyncSession, tenant_id: int | None, *, limit: int = 8
) -> list[Bitacora]:
    query = select(Bitacora).order_by(Bitacora.created_at.desc()).limit(limit)
    if tenant_id is not None:
        query = query.join(Usuario, Bitacora.usuario_id == Usuario.id).where(
            Usuario.tenant_id == tenant_id
        )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_panel_overview(
    db: AsyncSession,
    *,
    tenant_id: int | None = None,
) -> dict:
    # Consultas secuenciales en la misma sesión (AsyncSession no admite execute concurrente).
    total_usuarios = await _count_usuarios(db, tenant_id)
    total_talleres = await _count_talleres(db, tenant_id)
    total_roles = await _count_roles(db)
    actividad = await _bitacora_reciente(db, tenant_id)
    return {
        "total_usuarios": total_usuarios,
        "total_talleres": total_talleres,
        "total_roles": total_roles,
        "actividad_reciente": actividad,
    }
