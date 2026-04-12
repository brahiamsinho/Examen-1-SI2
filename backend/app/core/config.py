# app/core/config.py
# =========================================================
# Configuración central de la aplicación usando pydantic-settings
# Lee variables de entorno o del archivo .env
# =========================================================
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
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

    # ── CORS ──────────────────────────────────────────────
    # Lista de orígenes permitidos, separados por coma en el .env
    CORS_ORIGINS: str = "http://localhost:4200"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ── Entorno ────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global — importada en toda la app
settings = Settings()
