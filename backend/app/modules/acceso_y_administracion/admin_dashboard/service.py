from __future__ import annotations

import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.tenant_context import apply_postgres_tenant_session
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
    *,
    tenant_id: int | None = None,
) -> dict:
    """
    Conteos y bitácora en paralelo (mismo patrón que admin_finanzas).
    Cada consulta usa su propia AsyncSession.
    """

    async def usuarios_task() -> int:
        async with AsyncSessionLocal() as session:
            await apply_postgres_tenant_session(session)
            return await _count_usuarios(session, tenant_id)

    async def talleres_task() -> int:
        async with AsyncSessionLocal() as session:
            await apply_postgres_tenant_session(session)
            return await _count_talleres(session, tenant_id)

    async def roles_task() -> int:
        async with AsyncSessionLocal() as session:
            await apply_postgres_tenant_session(session)
            return await _count_roles(session)

    async def bitacora_task() -> list[Bitacora]:
        async with AsyncSessionLocal() as session:
            await apply_postgres_tenant_session(session)
            return await _bitacora_reciente(session, tenant_id)

    total_usuarios, total_talleres, total_roles, actividad = await asyncio.gather(
        usuarios_task(),
        talleres_task(),
        roles_task(),
        bitacora_task(),
    )
    return {
        "total_usuarios": total_usuarios,
        "total_talleres": total_talleres,
        "total_roles": total_roles,
        "actividad_reciente": actividad,
    }
