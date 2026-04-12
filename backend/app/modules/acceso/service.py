# app/modules/acceso/service.py
# =========================================================
# Lógica de negocio del módulo de Acceso
# =========================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, Request

from app.core.security import verify_password, create_access_token, create_refresh_token, hash_password
from app.core.config import settings
from app.modules.usuarios.models import Usuario
from app.modules.acceso.models import (
    Rol, Permiso, RolPermiso, UsuarioRol, Sesion,
    EstadoSesionEnum
)
from app.modules.bitacora.service import registrar_accion
from app.modules.bitacora.models import AccionBitacoraEnum


async def login(
    email: str,
    password: str,
    db: AsyncSession,
    request: Request,
) -> dict:
    """
    Autentica al usuario con email + password.
    
    Flujo:
    1. Busca usuario por email
    2. Verifica password con bcrypt
    3. Crea registro de sesión en BD con JTI único
    4. Genera access + refresh tokens JWT
    5. Registra acción en bitácora
    6. Actualiza ultimo_acceso_at
    """
    # 1. Buscar usuario
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if user.estado.value != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario {user.estado.value}. No puede iniciar sesión.",
        )

    # 2. Obtener roles del usuario
    roles_result = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == user.id)
    )
    roles = [r for (r,) in roles_result.fetchall()]

    # 3. JTI único para esta sesión (permite revocar tokens individualmente)
    jti = str(uuid.uuid4())

    # 4. Crear registro de sesión
    sesion = Sesion(
        usuario_id=user.id,
        token_jti=jti,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        dispositivo=request.headers.get("x-device-type"),
        plataforma=request.headers.get("x-platform"),
        iniciado_at=datetime.now(timezone.utc),
        expira_at=None,
        estado=EstadoSesionEnum.ACTIVA,
    )
    db.add(sesion)

    # 5. Actualizar ultimo_acceso_at
    await db.execute(
        update(Usuario)
        .where(Usuario.id == user.id)
        .values(ultimo_acceso_at=datetime.now(timezone.utc))
    )

    # 6. Registrar en bitácora
    await registrar_accion(
        db=db,
        usuario_id=user.id,
        modulo="acceso",
        entidad="sesiones",
        entidad_id=None,
        accion=AccionBitacoraEnum.INICIAR_SESION,
        descripcion=f"Inicio de sesión exitoso para {user.email}",
        ip_address=request.client.host if request.client else None,
    )

    # 7. Generar tokens
    access_token = create_access_token(
        subject=user.id,
        extra_claims={"jti": jti, "roles": roles},
    )
    refresh_token = create_refresh_token(subject=user.id, jti=jti)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def logout(usuario_id: int, jti: str, db: AsyncSession, request: Request) -> None:
    """Marca la sesión como CERRADA y registra en bitácora."""
    await db.execute(
        update(Sesion)
        .where(Sesion.token_jti == jti)
        .values(estado=EstadoSesionEnum.CERRADA, cerrado_at=datetime.now(timezone.utc))
    )
    await registrar_accion(
        db=db,
        usuario_id=usuario_id,
        modulo="acceso",
        entidad="sesiones",
        entidad_id=None,
        accion=AccionBitacoraEnum.CERRAR_SESION,
        descripcion="Cierre de sesión",
        ip_address=request.client.host if request.client else None,
    )


async def get_roles(db: AsyncSession) -> list[Rol]:
    result = await db.execute(select(Rol).order_by(Rol.nombre))
    return list(result.scalars().all())


async def create_rol(nombre: str, descripcion: str | None, db: AsyncSession) -> Rol:
    rol = Rol(
        nombre=nombre,
        descripcion=descripcion,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(rol)
    await db.flush()
    return rol


async def get_permisos(db: AsyncSession) -> list[Permiso]:
    result = await db.execute(select(Permiso).order_by(Permiso.modulo, Permiso.codigo))
    return list(result.scalars().all())


async def asignar_permisos_rol(rol_id: int, permiso_ids: list[int], db: AsyncSession) -> None:
    """Reemplaza todos los permisos del rol por los nuevos."""
    # Eliminar permisos actuales
    from sqlalchemy import delete
    await db.execute(delete(RolPermiso).where(RolPermiso.rol_id == rol_id))
    # Asignar nuevos
    for pid in permiso_ids:
        db.add(RolPermiso(
            rol_id=rol_id,
            permiso_id=pid,
            created_at=datetime.now(timezone.utc),
        ))


async def asignar_roles_usuario(usuario_id: int, rol_ids: list[int], db: AsyncSession) -> None:
    """Reemplaza todos los roles del usuario por los nuevos."""
    from sqlalchemy import delete
    await db.execute(delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id))
    for rid in rol_ids:
        db.add(UsuarioRol(
            usuario_id=usuario_id,
            rol_id=rid,
            asignado_at=datetime.now(timezone.utc),
        ))
