# app/modules/acceso/schemas.py
# =========================================================
# Schemas Pydantic para el módulo de Acceso
# =========================================================
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from app.modules.acceso.models import EstadoSesionEnum


# ── LOGIN ────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    """Credenciales para iniciar sesión. Acepta email o username."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Respuesta exitosa de autenticación."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class SolicitarRecuperacionIn(BaseModel):
    """Solicitud de correo con enlace para restablecer contraseña."""

    email: str


class RestablecerPasswordIn(BaseModel):
    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6, max_length=128)


# ── ROLES ────────────────────────────────────────────────────
class RolCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str]
    created_at: Optional[datetime]


class RolPermisosRead(BaseModel):
    """IDs de permisos asignados al rol (para panel admin)."""

    rol_id: int
    permiso_ids: list[int]


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


# ── PERMISOS ─────────────────────────────────────────────────
class PermisoCreate(BaseModel):
    codigo: str
    nombre: str
    modulo: str
    descripcion: Optional[str] = None


class PermisoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    modulo: str
    descripcion: Optional[str]


# ── ASIGNACIONES ─────────────────────────────────────────────
class AsignarPermisosARol(BaseModel):
    permiso_ids: list[int]


class AsignarRolesAUsuario(BaseModel):
    rol_ids: list[int]


# ── SESIONES ─────────────────────────────────────────────────
class SesionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    ip_address: Optional[str]
    dispositivo: Optional[str]
    plataforma: Optional[str]
    iniciado_at: datetime
    cerrado_at: Optional[datetime]
    estado: EstadoSesionEnum


# ── ME (usuario autenticado) ─────────────────────────────────
class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    email: str
    username: Optional[str]
    roles: list[str] = []
    permisos: list[str] = []
