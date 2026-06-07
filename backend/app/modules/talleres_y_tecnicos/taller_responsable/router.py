# API portal web taller — ciclo 1 (registro público + sesión responsable).
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user_permisos, require_permission
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.acceso_y_administracion.roles.models import Rol, UsuarioRol
from app.modules.talleres_y_tecnicos.talleres.models import Taller

from . import service
from .schemas import (
    RegistroTallerIn,
    MiTallerRead,
    MiTallerUpdate,
    TecnicoPortalCreate,
    TecnicoPortalUpdate,
    TecnicoPortalRead,
    TallerDashboardRead,
    TallerSuscripcionRead,
    TallerSuscripcionCheckoutIn,
    TallerSuscripcionCheckoutOut,
    TallerSuscripcionConfirmIn,
    TallerBitacoraRead,
)
from . import subscription_service
from . import bitacora_service

from app.modules.talleres_y_tecnicos.talleres.horarios_schemas import (
    TallerHorariosRead,
    TallerHorariosUpdateIn,
)
from app.modules.talleres_y_tecnicos.talleres import horarios_service as taller_horarios_service

router = APIRouter(prefix="/app/taller", tags=["App taller (responsable)"])


async def require_taller_responsable(
    data: tuple[Usuario, list[str]] = Depends(get_current_user_permisos),
    db: AsyncSession = Depends(get_db),
) -> tuple[Usuario, Taller]:
    user, _perms = data
    r = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == user.id)
    )
    roles = {row[0] for row in r.fetchall()}
    if "TALLER_RESPONSABLE" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el responsable de taller puede usar el portal.",
        )
    t = await db.execute(select(Taller).where(Taller.usuario_responsable_id == user.id))
    taller = t.scalar_one_or_none()
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No hay taller asociado a tu cuenta.",
        )
    return user, taller


@router.post("/registro", response_model=MiTallerRead, status_code=status.HTTP_201_CREATED)
async def registro_taller(body: RegistroTallerIn, db: AsyncSession = Depends(get_db)):
    """Alta pública: usuario responsable + rol + taller pendiente de validación."""
    return await service.registro_taller_publico(body, db)


@router.get("/dashboard", response_model=TallerDashboardRead)
async def dashboard(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, _ = ctx
    return await service.dashboard_taller(user.id, db)


@router.get("/mi-taller", response_model=MiTallerRead)
async def mi_taller(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, _ = ctx
    return await service.get_mi_taller(user.id, db)


@router.put("/mi-taller", response_model=MiTallerRead)
async def actualizar_mi_taller(
    body: MiTallerUpdate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, _ = ctx
    return await service.update_mi_taller(user.id, body, db)


@router.get("/tecnicos", response_model=list[TecnicoPortalRead])
async def listar_tecnicos(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    return await service.list_tecnicos_portal(taller.id, db)


@router.get("/tecnicos/{tecnico_id}", response_model=TecnicoPortalRead)
async def obtener_tecnico(
    tecnico_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    _, taller = ctx
    return await service.get_tecnico_portal(tecnico_id, taller.id, db)


@router.post("/tecnicos", response_model=TecnicoPortalRead, status_code=status.HTTP_201_CREATED)
async def crear_tecnico(
    body: TecnicoPortalCreate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    return await service.create_tecnico_portal(taller.id, body, user.id, db)


@router.put("/tecnicos/{tecnico_id}", response_model=TecnicoPortalRead)
async def actualizar_tecnico(
    tecnico_id: int,
    body: TecnicoPortalUpdate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    return await service.update_tecnico_portal(tecnico_id, taller.id, body, user.id, db)


@router.post("/tecnicos/{tecnico_id}/desactivar", response_model=TecnicoPortalRead)
async def desactivar_tecnico(
    tecnico_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    return await service.desactivar_tecnico_portal(tecnico_id, taller.id, user.id, db)


@router.delete("/tecnicos/{tecnico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_tecnico(
    tecnico_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, taller = ctx
    await service.delete_tecnico_portal(tecnico_id, taller.id, user.id, db)


@router.get("/suscripcion", response_model=TallerSuscripcionRead)
async def suscripcion_portal(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, _ = ctx
    return await subscription_service.get_suscripcion_portal(db, user)


@router.post("/suscripcion/checkout", response_model=TallerSuscripcionCheckoutOut)
async def suscripcion_checkout(
    body: TallerSuscripcionCheckoutIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    user, _ = ctx
    return await subscription_service.crear_checkout_upgrade(
        db,
        user,
        plan_slug=body.plan_slug,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )


@router.post("/suscripcion/confirm", response_model=TallerSuscripcionRead)
async def suscripcion_confirm_checkout(
    body: TallerSuscripcionConfirmIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    """Confirma el pago tras volver de Stripe (alternativa al webhook en desarrollo local)."""
    user, _ = ctx
    return await subscription_service.confirmar_checkout_suscripcion(
        db,
        user,
        session_id=body.session_id,
    )


@router.get(
    "/bitacora",
    response_model=list[TallerBitacoraRead],
    dependencies=[Depends(require_permission("bitacora_taller:leer"))],
)
async def listar_bitacora_taller(
    usuario_id: Optional[int] = Query(None),
    modulo: Optional[str] = Query(None),
    accion: Optional[AccionBitacoraEnum] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    """Bitácora del equipo del taller (responsable + técnicos), sin datos de otros talleres ni clientes."""
    user, taller = ctx
    return await bitacora_service.listar_bitacora_taller(
        db,
        user,
        taller,
        usuario_id=usuario_id,
        modulo=modulo,
        accion=accion,
        desde=desde,
        hasta=hasta,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/horarios",
    response_model=TallerHorariosRead,
    dependencies=[Depends(require_permission("disponibilidad:gestionar"))],
)
async def get_horarios_taller(
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    """Horarios de atención semanal del taller (zona Bolivia)."""
    _, taller = ctx
    return await taller_horarios_service.obtener_horarios(db, taller.id)


@router.put(
    "/horarios",
    response_model=TallerHorariosRead,
    dependencies=[Depends(require_permission("disponibilidad:gestionar"))],
)
async def put_horarios_taller(
    body: TallerHorariosUpdateIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza franjas horarias por día (ej. Lun–Vie 08:00–18:00)."""
    _, taller = ctx
    return await taller_horarios_service.actualizar_horarios(db, taller.id, body)
