# app/modules/bitacora/router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import bind_auth_context, get_current_user
from app.core.tenant import AuthContext
from app.core.tenant_context import effective_list_tenant_id
from app.modules.acceso_y_administracion.bitacora.models import Bitacora, AccionBitacoraEnum
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.acceso_y_administracion.bitacora.schemas import BitacoraRead

router = APIRouter(prefix="/bitacora", tags=["Bitácora"])


@router.get("/", response_model=list[BitacoraRead])
async def listar_bitacora(
    usuario_id: Optional[int] = Query(None),
    modulo: Optional[str] = Query(None),
    accion: Optional[AccionBitacoraEnum] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    tenant_id: Optional[int] = Query(None, description="Filtro tenant (solo superadmin)"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    ctx: AuthContext = Depends(bind_auth_context),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Consulta la bitácora con filtros opcionales.
    Solo lectura — la bitácora nunca se modifica desde la API.
    """
    query = select(Bitacora).order_by(Bitacora.created_at.desc())
    scope = effective_list_tenant_id(ctx, tenant_id)
    if scope is not None:
        query = query.join(Usuario, Bitacora.usuario_id == Usuario.id).where(
            Usuario.tenant_id == scope
        )

    if usuario_id:
        query = query.where(Bitacora.usuario_id == usuario_id)
    if modulo:
        query = query.where(Bitacora.modulo == modulo)
    if accion:
        query = query.where(Bitacora.accion == accion)
    if desde:
        query = query.where(Bitacora.created_at >= desde)
    if hasta:
        query = query.where(Bitacora.created_at <= hasta)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())
