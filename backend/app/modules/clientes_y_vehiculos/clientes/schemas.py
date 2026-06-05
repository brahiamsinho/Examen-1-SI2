# Schemas Pydantic — administración de clientes (API `/clientes` vía `usuarios.router`).
# Contratos app móvil: `schemas_movil.py`.
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.acceso_y_administracion.usuarios.models import EstadoUsuarioEnum


class ClienteCreate(BaseModel):
    usuario_id: int
    ciudad: Optional[str] = None
    direccion: Optional[str] = None


class ClienteAdminCreate(BaseModel):
    """Alta manual desde panel taller / admin (usuario + perfil cliente)."""

    nombres: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telefono: str = Field(..., min_length=5, max_length=30)
    password: str = Field(..., min_length=4, max_length=128)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    estado: EstadoUsuarioEnum = EstadoUsuarioEnum.ACTIVO


class ClienteAdminUpdate(BaseModel):
    nombres: Optional[str] = Field(default=None, max_length=100)
    apellidos: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length=30)
    ciudad: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = None
    estado: Optional[EstadoUsuarioEnum] = None


class ClienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    ciudad: Optional[str]
    direccion: Optional[str]
    created_at: Optional[datetime]


class ClienteListRead(BaseModel):
    """Cliente con datos de identidad del usuario (listados admin / portal taller)."""

    id: int
    usuario_id: int
    nombres: str
    apellidos: str
    email: str
    telefono: str
    estado: str
    ciudad: Optional[str]
    direccion: Optional[str]
    created_at: Optional[datetime]
