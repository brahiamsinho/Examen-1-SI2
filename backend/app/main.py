# app/main.py
# =========================================================
# Punto de entrada principal de la aplicación FastAPI
# Aquí se registran todos los routers y se configura CORS
# =========================================================
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.SEED_ADMIN_ON_START:
        from app.core.database import AsyncSessionLocal
        from app.seeds.dev_admin import ensure_dev_admin

        # Tras `docker compose up`, Postgres puede reiniciarse al terminar init.sql;
        # un intento único suele dar Connection refused aunque el healthcheck ya sea "healthy".
        last_err: BaseException | None = None
        for attempt in range(1, 9):
            try:
                async with AsyncSessionLocal() as session:
                    await ensure_dev_admin(session, require_enabled_flag=True)
                    await session.commit()
                break
            except Exception as e:
                last_err = e
                _log.warning(
                    "Seed admin intento %s/8: %s — reintento en 2s",
                    attempt,
                    e,
                )
                await asyncio.sleep(2)
        else:
            _log.error(
                "Seed administrador no pudo tras 8 intentos. "
                "Manual: docker compose exec backend python -m app.seeds",
                exc_info=last_err,
            )
    yield

# ── Importar todos los routers ────────────────────────────────
from app.modules.acceso.router import auth_router, roles_router, permisos_router
from app.modules.usuarios.router import router as usuarios_router, clientes_router
from app.modules.vehiculos.router import router as vehiculos_router
from app.modules.talleres.router import router, especialidades_router, tecnicos_router
from app.modules.bitacora.router import router as bitacora_router
from app.modules.portal_taller.router import router as portal_taller_router

# ── Crear aplicación ─────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
# En producción, CORS_ORIGINS debe ser solo el dominio del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar routers bajo el prefijo /api ─────────────────
# Modificado para remover el v1
PREFIX = settings.API_PREFIX

app.include_router(auth_router, prefix=PREFIX)
app.include_router(roles_router, prefix=PREFIX)
app.include_router(permisos_router, prefix=PREFIX)
app.include_router(usuarios_router, prefix=PREFIX)
app.include_router(clientes_router, prefix=PREFIX)
app.include_router(vehiculos_router, prefix=PREFIX)
app.include_router(router, prefix=PREFIX)           # talleres
app.include_router(especialidades_router, prefix=PREFIX)
app.include_router(tecnicos_router, prefix=PREFIX)
app.include_router(bitacora_router, prefix=PREFIX)
app.include_router(portal_taller_router, prefix=PREFIX)


# ── Health check ─────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint de verificación de salud — útil para load balancers y Docker healthcheck."""
    return {"status": "ok", "version": settings.VERSION, "environment": settings.ENVIRONMENT}


# ── Root ─────────────────────────────────────────────────────
@app.get("/", tags=["Sistema"])
async def root():
    return {
        "proyecto": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
