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


settings = Settings()
