# app/modules/acceso/router.py
# =========================================================
# Router FastAPI para el módulo de Acceso
# Prefijo: /api/v1/auth  y  /api/v1/roles  y  /api/v1/permisos
# =========================================================
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_permisos
from app.core.security import decode_token
from app.modules.acceso import service
from app.modules.acceso.schemas import (
    LoginRequest, TokenResponse, RolCreate, RolRead, RolUpdate,
    PermisoCreate, PermisoRead, AsignarPermisosARol, AsignarRolesAUsuario, MeResponse
)
from app.modules.usuarios.models import Usuario

# ── Router de autenticación ─────────────────────────────────
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Inicia sesión con email y contraseña. Devuelve access + refresh token."""
    return await service.login(body.email, body.password, db, request)


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cierra la sesión actual invalidando el token en BD."""
    from fastapi.security import HTTPBearer
    # Extraer JTI del token actual para marcarlo como CERRADO
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido")
    await service.logout(current_user.id, jti, db, request)


@auth_router.get("/me", response_model=MeResponse)
async def me(
    user_and_perms: tuple = Depends(get_current_user_permisos),
    db: AsyncSession = Depends(get_db),
):
    """Devuelve el usuario autenticado con sus roles y permisos."""
    user, permisos = user_and_perms
    # Obtener nombres de roles
    from sqlalchemy import select
    from app.modules.acceso.models import Rol, UsuarioRol
    roles_result = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == user.id)
    )
    roles = [r for (r,) in roles_result.fetchall()]
    return MeResponse(
        id=user.id,
        nombres=user.nombres,
        apellidos=user.apellidos,
        email=user.email,
        username=user.username,
        roles=roles,
        permisos=permisos,
    )


# ── Router de Roles ─────────────────────────────────────────
roles_router = APIRouter(prefix="/roles", tags=["Roles"])

@roles_router.get("/", response_model=list[RolRead])
async def listar_roles(db: AsyncSession = Depends(get_db)):
    return await service.get_roles(db)


@roles_router.post("/", response_model=RolRead, status_code=status.HTTP_201_CREATED)
async def crear_rol(body: RolCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_rol(body.nombre, body.descripcion, db)


@roles_router.put("/{rol_id}/permisos", status_code=status.HTTP_204_NO_CONTENT)
async def asignar_permisos(
    rol_id: int,
    body: AsignarPermisosARol,
    db: AsyncSession = Depends(get_db),
):
    await service.asignar_permisos_rol(rol_id, body.permiso_ids, db)


# ── Router de Permisos ──────────────────────────────────────
permisos_router = APIRouter(prefix="/permisos", tags=["Permisos"])

@permisos_router.get("/", response_model=list[PermisoRead])
async def listar_permisos(db: AsyncSession = Depends(get_db)):
    return await service.get_permisos(db)
