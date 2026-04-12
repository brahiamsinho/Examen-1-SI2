# app/main.py
# =========================================================
# Punto de entrada principal de la aplicación FastAPI
# Aquí se registran todos los routers y se configura CORS
# =========================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# ── Importar todos los routers ────────────────────────────────
from app.modules.acceso.router import auth_router, roles_router, permisos_router
from app.modules.usuarios.router import router as usuarios_router, clientes_router
from app.modules.vehiculos.router import router as vehiculos_router
from app.modules.talleres.router import router, especialidades_router, tecnicos_router
from app.modules.bitacora.router import router as bitacora_router

# ── Crear aplicación ─────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json",
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
