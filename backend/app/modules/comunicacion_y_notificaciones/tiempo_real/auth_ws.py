# Autenticación y autorización para WebSocket por solicitud.
from __future__ import annotations

from fastapi import HTTPException, WebSocketException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.tenant import is_platform_superadmin
from app.modules.acceso_y_administracion.roles.models import Rol, UsuarioRol
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.atencion.taller_emergencias.models import SolicitudTallerBandeja
from app.modules.clientes_y_vehiculos.clientes.service import get_cliente_row_for_usuario
from app.modules.incidentes.emergencias.models import SolicitudEmergencia
from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico


async def authenticate_ws_token(token: str | None, db: AsyncSession) -> Usuario:
    if not token or not token.strip():
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token requerido")
    try:
        payload = decode_token(token.strip())
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "access":
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token inválido")
    except JWTError as exc:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Token inválido o expirado"
        ) from exc

    result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or user.estado.value != "ACTIVO":
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Usuario no autorizado")
    return user


async def assert_ws_access_to_solicitud(
    user: Usuario, solicitud_id: int, db: AsyncSession, *, roles: list[str] | None = None
) -> None:
    res = await db.execute(select(SolicitudEmergencia).where(SolicitudEmergencia.id == solicitud_id))
    sol = res.scalar_one_or_none()
    if sol is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Solicitud no encontrada")

    if roles is None:
        r = await db.execute(
            select(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == user.id)
        )
        roles = [row[0] for row in r.fetchall()]

    if is_platform_superadmin(user, roles):
        return

    if "CLIENTE" in roles:
        try:
            c = await get_cliente_row_for_usuario(user.id, db)
            if sol.cliente_id == c.id:
                return
        except HTTPException:
            pass

    if "TECNICO" in roles:
        t_res = await db.execute(select(Tecnico).where(Tecnico.usuario_id == user.id))
        t = t_res.scalar_one_or_none()
        if t is not None and sol.tecnico_id is not None and sol.tecnico_id == t.id:
            return

    if "TALLER_RESPONSABLE" in roles:
        t_res = await db.execute(select(Taller).where(Taller.usuario_responsable_id == user.id))
        taller = t_res.scalar_one_or_none()
        if taller is not None:
            if sol.taller_id == taller.id:
                return
            b_res = await db.execute(
                select(SolicitudTallerBandeja.id).where(
                    SolicitudTallerBandeja.solicitud_id == solicitud_id,
                    SolicitudTallerBandeja.taller_id == taller.id,
                )
            )
            if b_res.scalar_one_or_none() is not None:
                return

    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Sin acceso a esta solicitud")
