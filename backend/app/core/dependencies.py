# app/core/dependencies.py
# =========================================================
# Dependencias reutilizables de FastAPI:
#   - Extracción y validación del usuario autenticado
#   - Verificación de roles/permisos
# =========================================================
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_token
from app.core.tenant import AuthContext, is_platform_superadmin
from app.core.tenant_subscription import assert_tenant_subscription_write
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.acceso_y_administracion.permisos.models import Permiso
from app.modules.acceso_y_administracion.roles.models import Rol, RolPermiso, UsuarioRol

# Bearer token extractor — lee el header "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """
    Dependencia principal de autenticación.
    
    Extrae el token JWT del header, lo decodifica y devuelve el usuario activo.
    Si el token es inválido, lanza 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    if user.estado.value != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario en estado {user.estado.value}. Acceso denegado.",
        )

    try:
        payload = decode_token(credentials.credentials)
        roles: list[str] = list(payload.get("roles") or [])
        token_tenant = payload.get("tenant_id")
        tenant_id = user.tenant_id
        if tenant_id is None and token_tenant is not None:
            tenant_id = int(token_tenant)
        from app.core.tenant_context import set_request_auth_context

        set_request_auth_context(
            AuthContext(
                user=user,
                roles=roles,
                tenant_id=tenant_id,
                is_platform_superadmin=is_platform_superadmin(user, roles),
            )
        )
    except JWTError:
        pass

    return user


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: Usuario = Depends(get_current_user),
) -> AuthContext:
    """
    Usuario + roles + tenant_id del JWT, validado contra el registro en BD.
    Superadmin plataforma: rol ADMIN y usuario.tenant_id IS NULL.
    """
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    roles: list[str] = list(payload.get("roles") or [])
    token_tenant = payload.get("tenant_id")

    if token_tenant is not None and current_user.tenant_id is not None:
        if int(token_tenant) != int(current_user.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no coincide con el tenant del usuario",
            )

    tenant_id = current_user.tenant_id
    if tenant_id is None and token_tenant is not None:
        tenant_id = int(token_tenant)

    ctx = AuthContext(
        user=current_user,
        roles=roles,
        tenant_id=tenant_id,
        is_platform_superadmin=is_platform_superadmin(current_user, roles),
    )
    from app.core.tenant_context import set_request_auth_context

    set_request_auth_context(ctx)
    return ctx


def bind_auth_context(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
    """Guarda AuthContext en contextvar para get_db / RLS en la misma petición."""
    from app.core.tenant_context import set_request_auth_context

    set_request_auth_context(ctx)
    return ctx


async def require_platform_superadmin(
    ctx: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    if not ctx.is_platform_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere superadmin de plataforma (ADMIN sin tenant).",
        )
    return ctx


async def require_writable_tenant_subscription(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """Bloquea escrituras si la suscripción SaaS del tenant no está al día (superadmin exento)."""
    if ctx.is_platform_superadmin:
        return ctx
    if ctx.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin organización asignada.",
        )
    tenant = await tenants_service.get_tenant_by_id(db, ctx.tenant_id)
    assert_tenant_subscription_write(tenant)
    return ctx


async def get_current_user_permisos(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> tuple[Usuario, list[str]]:
    """
    Extiende get_current_user devolviendo también la lista de códigos de permiso.
    Útil para verificar acceso granular a recursos.
    """
    # Obtener roles del usuario
    roles_result = await db.execute(
        select(UsuarioRol.rol_id).where(UsuarioRol.usuario_id == current_user.id)
    )
    rol_ids = [r for (r,) in roles_result.fetchall()]

    if not rol_ids:
        return current_user, []

    # Obtener permisos de todos los roles
    permisos_result = await db.execute(
        select(Permiso.codigo)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .where(RolPermiso.rol_id.in_(rol_ids))
    )
    permisos = [p for (p,) in permisos_result.fetchall()]
    return current_user, list(set(permisos))


def require_permission(codigo_permiso: str):
    """
    Factory de dependencias para rutas que requieren un permiso específico.
    
    Uso:
        @router.get("/", dependencies=[Depends(require_permission("usuarios:leer"))])
    """
    async def check_permission(
        user_and_perms: tuple = Depends(get_current_user_permisos),
    ):
        _, permisos = user_and_perms
        if codigo_permiso not in permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {codigo_permiso}",
            )
    return check_permission
