# app/modules/talleres/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.core.timeutil import utc_now_naive
from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico, EspecialidadTecnico
from app.modules.talleres_y_tecnicos.talleres.schemas import TallerProvisionIn, TallerProvisionRead, TallerRead
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.usuarios.models import Usuario, EstadoUsuarioEnum
from app.modules.acceso_y_administracion.usuarios import service as usuarios_service
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.roles.service import asignar_roles_usuario
from app.modules.talleres_y_tecnicos.taller_responsable.service import (
    _rol_id_by_nombre,
    _split_nombre_completo,
)


async def get_talleres(db: AsyncSession, list_tenant_id: int | None = None):
    stmt = select(Taller).order_by(Taller.nombre_comercial)
    if list_tenant_id is not None:
        stmt = stmt.where(Taller.tenant_id == list_tenant_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_taller_by_id(taller_id: int, db: AsyncSession) -> Taller:
    result = await db.execute(select(Taller).where(Taller.id == taller_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return t

async def validate_responsable_tenant(
    db: AsyncSession, *, usuario_id: int, tenant_id: int | None
) -> None:
    if tenant_id is None:
        return
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario responsable no encontrado")
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=400,
            detail="El responsable pertenece a otra organización (tenant).",
        )


async def create_taller(data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Taller:
    t = Taller(**data, created_at=utc_now_naive(), updated_at=utc_now_naive())
    db.add(t)
    await db.flush()
    await registrar_accion(db=db, usuario_id=ejecutor_id, modulo="talleres", entidad="talleres",
        entidad_id=t.id, accion=AccionBitacoraEnum.CREAR, descripcion=f"Taller creado: {t.nombre_comercial}")
    return t


async def provision_taller_con_responsable(
    body: TallerProvisionIn,
    db: AsyncSession,
    *,
    tenant_id: int,
    ejecutor_id: int,
) -> TallerProvisionRead:
    """Crea usuario ACTIVO + rol TALLER_RESPONSABLE + taller (admin SaaS, sin verificación email)."""
    await tenants_service.get_tenant_by_id(db, tenant_id)
    nombres, apellidos = _split_nombre_completo(body.responsable_nombre_completo)
    user = await usuarios_service.create_usuario(
        {
            "nombres": nombres,
            "apellidos": apellidos,
            "email": str(body.responsable_email),
            "telefono": body.responsable_telefono,
            "password": body.responsable_password,
            "username": None,
            "estado": EstadoUsuarioEnum.ACTIVO,
            "tenant_id": tenant_id,
        },
        db,
        ejecutor_id=ejecutor_id,
    )
    rid = await _rol_id_by_nombre(db, "TALLER_RESPONSABLE")
    await asignar_roles_usuario(user.id, [rid], db)
    taller = await create_taller(
        {
            "tenant_id": tenant_id,
            "usuario_responsable_id": user.id,
            "nombre_comercial": body.nombre_comercial,
            "telefono_contacto": body.telefono_contacto,
            "email_contacto": str(body.email_contacto),
            "direccion": body.direccion,
            "ciudad": body.ciudad,
            "descripcion": body.descripcion,
            "estado": body.estado,
        },
        db,
        ejecutor_id=ejecutor_id,
    )
    tenant = await tenants_service.get_tenant_by_id(db, tenant_id)
    base = TallerRead.model_validate(taller)
    return TallerProvisionRead(
        **base.model_dump(),
        responsable_email=user.email,
        tenant_slug=tenant.slug,
    )

async def update_taller(taller_id: int, data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Taller:
    t = await get_taller_by_id(taller_id, db)
    for k, v in data.items():
        if v is not None:
            setattr(t, k, v)
    t.updated_at = utc_now_naive()
    await registrar_accion(db=db, usuario_id=ejecutor_id, modulo="talleres", entidad="talleres",
        entidad_id=taller_id, accion=AccionBitacoraEnum.ACTUALIZAR, descripcion=f"Taller actualizado: {taller_id}")
    return t

async def get_especialidades(db: AsyncSession):
    result = await db.execute(select(EspecialidadTecnico).order_by(EspecialidadTecnico.nombre))
    return list(result.scalars().all())

async def create_especialidad(nombre: str, descripcion: str | None, db: AsyncSession) -> EspecialidadTecnico:
    e = EspecialidadTecnico(nombre=nombre, descripcion=descripcion)
    db.add(e)
    await db.flush()
    return e

async def get_tecnicos(db: AsyncSession, taller_id: int | None = None):
    query = select(Tecnico)
    if taller_id:
        query = query.where(Tecnico.taller_id == taller_id)
    result = await db.execute(query)
    return list(result.scalars().all())

async def create_tecnico(data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Tecnico:
    t = Tecnico(**data, created_at=utc_now_naive(), updated_at=utc_now_naive())
    db.add(t)
    await db.flush()
    await registrar_accion(db=db, usuario_id=ejecutor_id, modulo="talleres", entidad="tecnicos",
        entidad_id=t.id, accion=AccionBitacoraEnum.CREAR)
    return t

async def update_tecnico(tecnico_id: int, data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Tecnico:
    result = await db.execute(select(Tecnico).where(Tecnico.id == tecnico_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    for k, v in data.items():
        if v is not None:
            setattr(t, k, v)
    t.updated_at = utc_now_naive()
    return t
