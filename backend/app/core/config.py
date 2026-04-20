# app/core/config.py
# =========================================================
# Configuración central (pydantic-settings).
# Prioridad: variables de entorno del proceso > .env raíz repo > backend/.env
# =========================================================
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_DIR.parent


def _env_files() -> tuple[str, ...]:
    """Solo archivos existentes; raíz del repo tiene precedencia sobre backend/.env."""
    paths = [_BACKEND_DIR / ".env", _REPO_ROOT / ".env"]
    return tuple(str(p) for p in paths if p.is_file())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files() or None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── API ──────────────────────────────────────────────
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Plataforma Inteligente de Emergencias Vehiculares"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API REST para gestión de emergencias vehiculares — Ciclo 1"

    # ── Base de datos ─────────────────────────────────────
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:port/db

    # ── Seguridad / JWT ───────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS (lista separada por coma en .env raíz) ───────
    CORS_ORIGINS: str = "http://localhost:4200,http://localhost:80"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ── Entorno ────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Seed admin (desarrollo; nunca activar en prod sin control explícito) ──
    SEED_ADMIN_ON_START: bool = False
    SEED_ADMIN_EMAIL: str | None = None
    SEED_ADMIN_PASSWORD: str | None = None
    SEED_ADMIN_TELEFONO: str | None = None
    SEED_ADMIN_NOMBRES: str = "Administrador"
    SEED_ADMIN_APELLIDOS: str = "Sistema"
    SEED_ADMIN_USERNAME: str | None = "admin"

    # ── Seed cliente demo (app móvil / portal cliente) ─────────
    SEED_CLIENTE_ON_START: bool = False
    SEED_CLIENTE_EMAIL: str | None = "cli@test.com"
    SEED_CLIENTE_PASSWORD: str | None = "cli123"
    SEED_CLIENTE_TELEFONO: str | None = "+5917000002"
    SEED_CLIENTE_NOMBRES: str = "Cliente"
    SEED_CLIENTE_APELLIDOS: str = "Demo"
    SEED_CLIENTE_CIUDAD: str | None = None
    SEED_CLIENTE_DIRECCION: str | None = None

    # ── Seed taller demo (portal taller / responsable) ───────
    SEED_TALLER_ON_START: bool = False
    SEED_TALLER_EMAIL: str | None = "taller@test.com"
    SEED_TALLER_PASSWORD: str | None = "taller123"
    SEED_TALLER_TELEFONO: str | None = "+5917000003"
    SEED_TALLER_RESPONSABLE_NOMBRES: str = "Responsable"
    SEED_TALLER_RESPONSABLE_APELLIDOS: str = "Taller Demo"
    SEED_TALLER_NOMBRE_COMERCIAL: str = "Taller Demo Emergencias"
    SEED_TALLER_CIUDAD: str = "La Paz"
    SEED_TALLER_DIRECCION: str = "Av. Seed 100"
    SEED_TALLER_DESCRIPCION: str | None = "Taller de demostración (seed desarrollo)."

    # ── Seed técnico demo (app móvil técnico; requiere un taller) ─
    SEED_TECNICO_ON_START: bool = False
    SEED_TECNICO_EMAIL: str | None = "tec@test.com"
    SEED_TECNICO_PASSWORD: str | None = "tec123"
    SEED_TECNICO_TELEFONO: str | None = "+5917000004"
    SEED_TECNICO_NOMBRES: str = "Técnico"
    SEED_TECNICO_APELLIDOS: str = "Seed"

    # ── Pagos CU20 — simulación local; desactivar autocmpletar para flujo tipo pasarela (2 pasos) ──
    PAGO_SIMULADO_AUTOCOMPLETE: bool = True
    PAGO_PROVEEDOR_DEFAULT: str = "SIMULADO"
    # Stripe (opcional). Nunca reutilices el nombre SECRET_KEY aquí: en FastAPI es el JWT.
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None

    @property
    def stripe_enabled(self) -> bool:
        return bool(self.STRIPE_SECRET_KEY and self.STRIPE_SECRET_KEY.strip())

    # ── Firebase Cloud Messaging (CU19) — opcional; ruta al JSON de cuenta de servicio ──
    FCM_ENABLED: bool = False
    FIREBASE_CREDENTIALS_PATH: str | None = None  # ej. firebase-credentials.json (relativo a backend/)

    @property
    def firebase_credentials_file(self) -> Path | None:
        if not self.FIREBASE_CREDENTIALS_PATH:
            return None
        p = Path(self.FIREBASE_CREDENTIALS_PATH)
        if p.is_file():
            return p
        cand = _BACKEND_DIR / self.FIREBASE_CREDENTIALS_PATH
        if cand.is_file():
            return cand
        return None


settings = Settings()
