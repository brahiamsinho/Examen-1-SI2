# app/modules/acceso/models.py
# =========================================================
# Modelos SQLAlchemy para el módulo de Acceso:
#   Roles, Permisos, RolPermiso, UsuarioRol, Sesiones
# =========================================================
import enum
from datetime import datetime
from sqlalchemy import (
    Integer, String, Text, ForeignKey, DateTime,
    Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


# ── ENUMs Python (espejo de los ENUMs PostgreSQL) ──────────
class EstadoSesionEnum(str, enum.Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    EXPIRADA = "EXPIRADA"
    REVOCADA = "REVOCADA"


# ── Modelo: Roles ───────────────────────────────────────────
class Rol(Base):
    """
    Tabla: roles
    Representa un grupo de permisos asignables a usuarios.
    Ejemplos: ADMIN, CLIENTE, TECNICO, TALLER_RESPONSABLE
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    rol_permisos: Mapped[list["RolPermiso"]] = relationship(back_populates="rol")
    usuario_roles: Mapped[list["UsuarioRol"]] = relationship(back_populates="rol")


# ── Modelo: Permisos ────────────────────────────────────────
class Permiso(Base):
    """
    Tabla: permisos
    Permiso atómico identificado por un código único.
    Ejemplos: usuarios:crear, vehiculos:leer, talleres:actualizar
    """
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    modulo: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    rol_permisos: Mapped[list["RolPermiso"]] = relationship(back_populates="permiso")


# ── Modelo: RolPermiso (tabla pivot roles ↔ permisos) ───────
class RolPermiso(Base):
    """
    Tabla: rol_permiso
    Asociación muchos-a-muchos entre Rol y Permiso.
    Constraint UNIQUE garantiza que no se duplique la asignación.
    """
    __tablename__ = "rol_permiso"
    __table_args__ = (
        UniqueConstraint("rol_id", "permiso_id", name="uq_rol_permiso"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    permiso_id: Mapped[int] = mapped_column(ForeignKey("permisos.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    rol: Mapped["Rol"] = relationship(back_populates="rol_permisos")
    permiso: Mapped["Permiso"] = relationship(back_populates="rol_permisos")


# ── Modelo: UsuarioRol (tabla pivot users ↔ roles) ──────────
class UsuarioRol(Base):
    """
    Tabla: usuario_rol
    Asociación muchos-a-muchos entre Usuario y Rol.
    Un usuario puede tener múltiples roles.
    """
    __tablename__ = "usuario_rol"
    __table_args__ = (
        UniqueConstraint("usuario_id", "rol_id", name="uq_usuario_rol"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    asignado_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    rol: Mapped["Rol"] = relationship(back_populates="usuario_roles")


# ── Modelo: Sesiones ────────────────────────────────────────
class Sesion(Base):
    """
    Tabla: sesiones
    Registra cada sesión activa del usuario.
    token_jti es el JWT ID — permite revocar tokens sin invalidar todos.
    Almacena IP, user-agent y plataforma para auditoría.
    """
    __tablename__ = "sesiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    token_jti: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    dispositivo: Mapped[str | None] = mapped_column(String(100))
    plataforma: Mapped[str | None] = mapped_column(String(50))
    iniciado_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cerrado_at: Mapped[datetime | None] = mapped_column(DateTime)
    expira_at: Mapped[datetime | None] = mapped_column(DateTime)
    estado: Mapped[EstadoSesionEnum] = mapped_column(
        SAEnum(EstadoSesionEnum, name="estado_sesion"), nullable=False
    )
