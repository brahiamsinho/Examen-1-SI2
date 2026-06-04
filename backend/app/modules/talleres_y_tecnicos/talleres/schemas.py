# app/modules/talleres/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from typing import Optional
from datetime import datetime
from app.modules.talleres_y_tecnicos.talleres.models import EstadoTallerEnum, EstadoTecnicoEnum


class EspecialidadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    descripcion: Optional[str]

class EspecialidadCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class TallerCreate(BaseModel):
    tenant_id: Optional[int] = None
    usuario_responsable_id: int
    nombre_comercial: str
    telefono_contacto: str
    email_contacto: EmailStr
    direccion: str
    ciudad: str
    descripcion: Optional[str] = None
    estado: EstadoTallerEnum = EstadoTallerEnum.PENDIENTE

class TallerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: Optional[int] = None
    usuario_responsable_id: int
    nombre_comercial: str
    telefono_contacto: str
    email_contacto: str
    direccion: str
    ciudad: str
    descripcion: Optional[str]
    estado: EstadoTallerEnum
    created_at: Optional[datetime]

class TallerUpdate(BaseModel):
    nombre_comercial: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoTallerEnum] = None


class TallerProvisionIn(BaseModel):
    """Alta admin: taller + usuario responsable (login /taller) en una operación."""

    tenant_id: Optional[int] = None
    nombre_comercial: str = Field(..., min_length=2, max_length=150)
    telefono_contacto: str = Field(..., min_length=5, max_length=30)
    email_contacto: EmailStr
    direccion: str = Field(..., min_length=3)
    ciudad: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None
    estado: EstadoTallerEnum = EstadoTallerEnum.ACTIVO
    responsable_nombre_completo: str = Field(..., min_length=3, max_length=200)
    responsable_email: EmailStr
    responsable_telefono: str = Field(..., min_length=5, max_length=30)
    responsable_password: str = Field(..., min_length=4, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def fill_contact_from_responsable(cls, data):
        """Si contacto del taller está vacío o es demasiado corto, reutiliza datos del responsable."""
        if not isinstance(data, dict):
            return data
        tel = str(data.get("telefono_contacto") or "").strip()
        rtel = str(data.get("responsable_telefono") or "").strip()
        if len(tel) < 5 and len(rtel) >= 5:
            data["telefono_contacto"] = rtel
        email = str(data.get("email_contacto") or "").strip()
        remail = str(data.get("responsable_email") or "").strip()
        if not email and remail:
            data["email_contacto"] = remail
        return data


class TallerProvisionRead(TallerRead):
    responsable_email: str
    tenant_slug: str


class TecnicoCreate(BaseModel):
    usuario_id: int
    taller_id: int
    especialidad_id: Optional[int] = None
    documento_identidad: Optional[str] = None
    disponibilidad: Optional[str] = None
    estado: EstadoTecnicoEnum = EstadoTecnicoEnum.ACTIVO

class TecnicoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    taller_id: int
    especialidad_id: Optional[int]
    estado: EstadoTecnicoEnum
    created_at: Optional[datetime]

class TecnicoUpdate(BaseModel):
    taller_id: Optional[int] = None
    especialidad_id: Optional[int] = None
    documento_identidad: Optional[str] = None
    disponibilidad: Optional[str] = None
    estado: Optional[EstadoTecnicoEnum] = None
