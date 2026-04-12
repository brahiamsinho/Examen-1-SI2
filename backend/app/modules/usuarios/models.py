# app/modules/usuarios/models.py
# =========================================================
# Modelos SQLAlchemy para el módulo de Usuarios:
#   Usuario, Cliente
# =========================================================
import enum
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


# ── ENUMs ───────────────────────────────────────────────────
class EstadoUsuarioEnum(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"
    PENDIENTE = "PENDIENTE"


# ── Modelo: Usuario ─────────────────────────────────────────
class Usuario(Base):
    """
    Tabla: usuarios
    Entidad central del sistema — toda persona con acceso hereda de aquí.
    Clientes, técnicos y responsables de talleres son extensiones de Usuario.
    
    password_hash: NUNCA se almacena el password en texto plano.
    estado: controla si puede iniciar sesión.
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str | None] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoUsuarioEnum] = mapped_column(
        SAEnum(EstadoUsuarioEnum, name="estado_usuario"), nullable=False
    )
    ultimo_acceso_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    cliente: Mapped["Cliente | None"] = relationship(back_populates="usuario", uselist=False)


# ── Modelo: Cliente ─────────────────────────────────────────
class Cliente(Base):
    """
    Tabla: clientes
    Extensión de Usuario para clientes del sistema.
    Patrón: un Usuario tiene UN Cliente (relación 1:1).
    
    usuario_id: FK única — garantiza que un usuario solo sea cliente una vez.
    """
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    ciudad: Mapped[str | None] = mapped_column(String(100))
    direccion: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relaciones
    usuario: Mapped["Usuario"] = relationship(back_populates="cliente")
    vehiculos: Mapped[list["Vehiculo"]] = relationship(back_populates="cliente")  # type: ignore
