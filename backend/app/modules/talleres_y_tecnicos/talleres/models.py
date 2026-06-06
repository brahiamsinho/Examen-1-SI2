# app/modules/talleres/models.py
# =========================================================
# Modelos SQLAlchemy para el módulo de Talleres:
#   Taller, EspecialidadTecnico, Tecnico
# =========================================================
import enum
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, Numeric, Time, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.acceso_y_administracion.usuarios.models import Usuario


# ── ENUMs ───────────────────────────────────────────────────
class EstadoTallerEnum(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    PENDIENTE = "PENDIENTE"


class EstadoTecnicoEnum(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


# ── Modelo: Taller ──────────────────────────────────────────
class Taller(Base):
    """
    Tabla: talleres
    Taller mecánico con un usuario responsable (FK a usuarios).
    usuario_responsable_id UNIQUE garantiza que un usuario solo
    puede ser responsable de un taller.
    """
    __tablename__ = "talleres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=True
    )
    usuario_responsable_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    nombre_comercial: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono_contacto: Mapped[str] = mapped_column(String(30), nullable=False)
    email_contacto: Mapped[str] = mapped_column(String(120), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoTallerEnum] = mapped_column(
        SAEnum(EstadoTallerEnum, name="estado_taller"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    tecnicos: Mapped[list["Tecnico"]] = relationship(back_populates="taller")
    horarios: Mapped[list["TallerHorario"]] = relationship(
        back_populates="taller", cascade="all, delete-orphan"
    )


# ── Modelo: TallerHorario ───────────────────────────────────
class TallerHorario(Base):
    """
    Tabla: taller_horarios
    Franja horaria de atención por día de la semana (0=lunes … 6=domingo, hora Bolivia).
    """
    __tablename__ = "taller_horarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"), nullable=False
    )
    dia_semana: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    hora_apertura: Mapped[time] = mapped_column(Time, nullable=False)
    hora_cierre: Mapped[time] = mapped_column(Time, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    taller: Mapped["Taller"] = relationship(back_populates="horarios")


# ── Modelo: EspecialidadTecnico ─────────────────────────────
class EspecialidadTecnico(Base):
    """
    Tabla: especialidades_tecnico
    Catálogo de especialidades: Motor, Electricidad, Carrocería, etc.
    """
    __tablename__ = "especialidades_tecnico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


# ── Modelo: Tecnico ─────────────────────────────────────────
class Tecnico(Base):
    """
    Tabla: tecnicos
    Técnico asociado a un Taller. Extensión de Usuario (patrón 1:1).
    especialidad_id es nullable — ON DELETE SET NULL.
    """
    __tablename__ = "tecnicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="RESTRICT"), nullable=False
    )
    especialidad_id: Mapped[int | None] = mapped_column(
        ForeignKey("especialidades_tecnico.id", ondelete="SET NULL")
    )
    documento_identidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
    disponibilidad: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estado: Mapped[EstadoTecnicoEnum] = mapped_column(
        SAEnum(EstadoTecnicoEnum, name="estado_tecnico"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    taller: Mapped["Taller"] = relationship(back_populates="tecnicos")
    especialidad: Mapped["EspecialidadTecnico | None"] = relationship()
    usuario: Mapped["Usuario"] = relationship(foreign_keys=[usuario_id])
