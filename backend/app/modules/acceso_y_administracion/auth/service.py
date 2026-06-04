# app/modules/auth/service.py
import uuid
from fastapi import HTTPException, Request, status
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.auth.models import EstadoSesionEnum, Sesion
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.roles.models import Rol, UsuarioRol
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.usuarios.models import EstadoUsuarioEnum, Usuario


async def _login_rls_bypass(db: AsyncSession) -> None:
    """Login debe ver usuarios de cualquier tenant; solo dura la transacción."""
    await db.execute(text("SELECT set_config('app.bypass_rls', 'on', true)"))


async def login(
    email: str,
    password: str,
    db: AsyncSession,
    request: Request,
    tenant_slug: str | None = None,
) -> dict:
    """
    Autentica al usuario con email + password.
    Si viene X-Tenant-Slug, el usuario debe pertenecer a ese tenant (salvo superadmin sin tenant).
    """
    await _login_rls_bypass(db)
    result = await db.execute(select(Usuario).where(Usuario.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if tenant_slug:
        tenant = await tenants_service.get_tenant_by_slug(db, tenant_slug.strip().lower())
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
        if user.tenant_id is not None and user.tenant_id != tenant.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

    if user.estado == EstadoUsuarioEnum.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta pendiente de verificación. Revisa tu correo y abre el enlace de activación.",
        )
    if user.estado != EstadoUsuarioEnum.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario {user.estado.value}. No puede iniciar sesión.",
        )

    roles_result = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == user.id)
    )
    roles = [r for (r,) in roles_result.fetchall()]

    jti = str(uuid.uuid4())

    sesion = Sesion(
        usuario_id=user.id,
        token_jti=jti,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        dispositivo=request.headers.get("x-device-type"),
        plataforma=request.headers.get("x-platform"),
        iniciado_at=utc_now_naive(),
        expira_at=None,
        estado=EstadoSesionEnum.ACTIVA,
    )
    db.add(sesion)

    await db.execute(
        update(Usuario)
        .where(Usuario.id == user.id)
        .values(ultimo_acceso_at=utc_now_naive())
    )

    await registrar_accion(
        db=db,
        usuario_id=user.id,
        modulo="auth",
        entidad="sesiones",
        entidad_id=None,
        accion=AccionBitacoraEnum.INICIAR_SESION,
        descripcion=f"Inicio de sesión exitoso para {user.email}",
        ip_address=request.client.host if request.client else None,
    )

    access_token = create_access_token(
        subject=user.id,
        extra_claims={
            "jti": jti,
            "roles": roles,
            "tenant_id": user.tenant_id,
        },
    )
    refresh_token = create_refresh_token(subject=user.id, jti=jti)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def solicitar_recuperacion_contrasena(email: str, db: AsyncSession) -> None:
    from sqlalchemy import func

    from app.modules.acceso_y_administracion.auth.email_tokens import crear_y_enviar_reset_password

    em = email.strip().lower()
    if not em:
        return
    result = await db.execute(select(Usuario).where(func.lower(Usuario.email) == em))
    user = result.scalar_one_or_none()
    if user is None or user.estado == EstadoUsuarioEnum.BLOQUEADO:
        return
    await crear_y_enviar_reset_password(db, user)


async def restablecer_contrasena_con_token(token: str, password: str, db: AsyncSession) -> None:
    from app.modules.acceso_y_administracion.auth.email_tokens import consumir_token_reset_password

    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La contraseña debe tener al menos 6 caracteres.",
        )
    u = await consumir_token_reset_password(db, token.strip(), password)
    if u is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enlace inválido o expirado. Solicita uno nuevo desde «Olvidé mi contraseña».",
        )


async def logout(usuario_id: int, jti: str, db: AsyncSession, request: Request) -> None:
    await db.execute(
        update(Sesion)
        .where(Sesion.token_jti == jti)
        .values(estado=EstadoSesionEnum.CERRADA, cerrado_at=utc_now_naive())
    )
    await registrar_accion(
        db=db,
        usuario_id=usuario_id,
        modulo="auth",
        entidad="sesiones",
        entidad_id=None,
        accion=AccionBitacoraEnum.CERRAR_SESION,
        descripcion="Cierre de sesión",
        ip_address=request.client.host if request.client else None,
    )
