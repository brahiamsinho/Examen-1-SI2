# app/modules/talleres/models.py
# =========================================================
# Modelos SQLAlchemy para el módulo de Talleres:
#   Taller, EspecialidadTecnico, Tecnico
# =========================================================
import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


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
    usuario_responsable_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    nombre_comercial: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono_contacto: Mapped[str] = mapped_column(String(30), nullable=False)
    email_contacto: Mapped[str] = mapped_column(String(120), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoTallerEnum] = mapped_column(
        SAEnum(EstadoTallerEnum, name="estado_taller"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    tecnicos: Mapped[list["Tecnico"]] = relationship(back_populates="taller")


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
    estado: Mapped[EstadoTecnicoEnum] = mapped_column(
        SAEnum(EstadoTecnicoEnum, name="estado_tecnico"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    taller: Mapped["Taller"] = relationship(back_populates="tecnicos")
    especialidad: Mapped["EspecialidadTecnico | None"] = relationship()
