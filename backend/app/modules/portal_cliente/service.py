# Lógica portal móvil cliente — ciclo 1
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.acceso.models import Rol, UsuarioRol
from app.modules.acceso.service import asignar_roles_usuario
from app.modules.bitacora.models import AccionBitacoraEnum
from app.modules.bitacora.service import registrar_accion
from app.modules.usuarios.models import Cliente, EstadoUsuarioEnum, Usuario
from app.modules.usuarios import service as usuarios_service
from app.modules.vehiculos import service as vehiculos_service
from app.modules.vehiculos.schemas import VehiculoRead, VehiculoUpdate

from .schemas import (
    ClienteMiPerfilRead,
    ClienteMiPerfilUpdate,
    RegistroClienteMovilIn,
    VehiculoClienteCreateIn,
)


async def _rol_id_by_nombre(db: AsyncSession, nombre: str) -> int:
    r = await db.execute(select(Rol.id).where(Rol.nombre == nombre))
    row = r.scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rol '{nombre}' no configurado en el sistema.",
        )
    return int(row)


async def get_cliente_row_for_usuario(usuario_id: int, db: AsyncSession) -> Cliente:
    r = await db.execute(select(Cliente).where(Cliente.usuario_id == usuario_id))
    c = r.scalar_one_or_none()
    if c is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no tiene perfil de cliente.",
        )
    return c


async def require_cliente_rol(usuario_id: int, db: AsyncSession) -> None:
    r = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == usuario_id)
    )
    roles = {row[0] for row in r.fetchall()}
    if "CLIENTE" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo cuentas con rol CLIENTE pueden usar el portal móvil de cliente.",
        )


async def registro_cliente_publico(body: RegistroClienteMovilIn, db: AsyncSession) -> ClienteMiPerfilRead:
    user = await usuarios_service.create_usuario(
        {
            "nombres": body.nombres.strip(),
            "apellidos": body.apellidos.strip(),
            "email": str(body.email).lower().strip(),
            "telefono": body.telefono.strip(),
            "password": body.password,
            "username": None,
            "estado": EstadoUsuarioEnum.ACTIVO,
        },
        db,
        ejecutor_id=None,
    )
    cliente = await usuarios_service.create_cliente(
        {"usuario_id": user.id, "ciudad": None, "direccion": None},
        db,
    )
    rid = await _rol_id_by_nombre(db, "CLIENTE")
    await asignar_roles_usuario(user.id, [rid], db)
    await registrar_accion(
        db,
        "portal_cliente",
        "registro",
        AccionBitacoraEnum.CREAR,
        descripcion=f"Registro público de cliente móvil: {user.email}",
        usuario_id=user.id,
        entidad_id=cliente.id,
    )
    return await mi_perfil_read(user, cliente, db)


async def mi_perfil_read(user: Usuario, cliente: Cliente, db: AsyncSession) -> ClienteMiPerfilRead:
    _ = db
    return ClienteMiPerfilRead(
        usuario_id=user.id,
        cliente_id=cliente.id,
        nombres=user.nombres,
        apellidos=user.apellidos,
        email=user.email,
        telefono=user.telefono,
        ciudad=cliente.ciudad,
        direccion=cliente.direccion,
    )


async def get_mi_perfil(user: Usuario, db: AsyncSession) -> ClienteMiPerfilRead:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)
    return await mi_perfil_read(user, cliente, db)


async def update_mi_perfil(user: Usuario, body: ClienteMiPerfilUpdate, db: AsyncSession) -> ClienteMiPerfilRead:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)

    udata = {
        "nombres": body.nombres,
        "apellidos": body.apellidos,
        "telefono": body.telefono,
        "username": None,
        "estado": None,
    }
    udata = {k: v for k, v in udata.items() if v is not None}
    if udata:
        user = await usuarios_service.update_usuario(user.id, udata, db, ejecutor_id=user.id)
        await db.refresh(user)

    if body.ciudad is not None:
        cliente.ciudad = body.ciudad
    if body.direccion is not None:
        cliente.direccion = body.direccion
    cliente.updated_at = utc_now_naive()

    await registrar_accion(
        db,
        "portal_cliente",
        "clientes",
        AccionBitacoraEnum.ACTUALIZAR,
        descripcion="Actualización de perfil cliente (móvil)",
        usuario_id=user.id,
        entidad_id=cliente.id,
    )
    return await mi_perfil_read(user, cliente, db)


async def list_mis_vehiculos(user: Usuario, db: AsyncSession) -> list[VehiculoRead]:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)
    rows = await vehiculos_service.get_vehiculos(db, cliente_id=cliente.id)
    return [VehiculoRead.model_validate(v) for v in rows]


async def get_mi_vehiculo(user: Usuario, vehiculo_id: int, db: AsyncSession) -> VehiculoRead:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)
    v = await vehiculos_service.get_vehiculo_by_id(vehiculo_id, db)
    if v.cliente_id != cliente.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return VehiculoRead.model_validate(v)


async def crear_mi_vehiculo(user: Usuario, body: VehiculoClienteCreateIn, db: AsyncSession) -> VehiculoRead:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)
    data = {
        "cliente_id": cliente.id,
        "placa": body.placa.strip().upper(),
        "marca_id": body.marca_id,
        "modelo_id": body.modelo_id,
        "tipo_vehiculo_id": body.tipo_vehiculo_id,
        "anio": body.anio,
        "color": body.color,
    }
    v = await vehiculos_service.create_vehiculo(data, db, ejecutor_id=user.id)
    return VehiculoRead.model_validate(v)


async def actualizar_mi_vehiculo(
    user: Usuario,
    vehiculo_id: int,
    body: VehiculoUpdate,
    db: AsyncSession,
) -> VehiculoRead:
    await require_cliente_rol(user.id, db)
    cliente = await get_cliente_row_for_usuario(user.id, db)
    v = await vehiculos_service.get_vehiculo_by_id(vehiculo_id, db)
    if v.cliente_id != cliente.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    updated = await vehiculos_service.update_vehiculo(
        vehiculo_id,
        body.model_dump(exclude_none=True),
        db,
        user.id,
    )
    return VehiculoRead.model_validate(updated)
