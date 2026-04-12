# app/modules/usuarios/service.py
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.modules.usuarios.models import Usuario, Cliente, EstadoUsuarioEnum
from app.modules.bitacora.service import registrar_accion
from app.modules.bitacora.models import AccionBitacoraEnum


async def get_usuarios(db: AsyncSession) -> list[Usuario]:
    result = await db.execute(select(Usuario).order_by(Usuario.apellidos))
    return list(result.scalars().all())


async def get_usuario_by_id(usuario_id: int, db: AsyncSession) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


async def create_usuario(data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Usuario:
    # Verificar duplicados
    existing = await db.execute(select(Usuario).where(Usuario.email == data["email"]))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    user = Usuario(
        nombres=data["nombres"],
        apellidos=data["apellidos"],
        email=data["email"],
        telefono=data["telefono"],
        username=data.get("username"),
        password_hash=hash_password(data["password"]),
        estado=data.get("estado", EstadoUsuarioEnum.ACTIVO),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()  # obtener ID sin commit

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=user.id,
        accion=AccionBitacoraEnum.CREAR,
        descripcion=f"Creación del usuario {user.email}",
    )
    return user


async def update_usuario(
    usuario_id: int, data: dict, db: AsyncSession, ejecutor_id: int | None = None
) -> Usuario:
    user = await get_usuario_by_id(usuario_id, db)
    for field, value in data.items():
        if value is not None:
            setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Actualización del usuario {usuario_id}",
    )
    return user


async def delete_usuario(usuario_id: int, db: AsyncSession, ejecutor_id: int | None = None) -> None:
    """No elimina físicamente — cambia estado a INACTIVO (soft delete)."""
    user = await get_usuario_by_id(usuario_id, db)
    user.estado = EstadoUsuarioEnum.INACTIVO
    user.updated_at = datetime.now(timezone.utc)
    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ELIMINAR,
        descripcion=f"Desactivación (soft delete) del usuario {usuario_id}",
    )


async def get_clientes(db: AsyncSession) -> list[Cliente]:
    result = await db.execute(select(Cliente))
    return list(result.scalars().all())


async def create_cliente(data: dict, db: AsyncSession) -> Cliente:
    cliente = Cliente(
        usuario_id=data["usuario_id"],
        ciudad=data.get("ciudad"),
        direccion=data.get("direccion"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(cliente)
    await db.flush()
    return cliente
