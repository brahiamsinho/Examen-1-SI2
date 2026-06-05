# app/main.py
# =========================================================
# Punto de entrada principal de la aplicación FastAPI
# Aquí se registran todos los routers y se configura CORS
# =========================================================
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.tenant_middleware import TenantSlugMiddleware

_log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.RUN_SEEDS_IN_LIFESPAN:
        from app.seeds.runner import run_startup_seeds, seeds_enabled_for_startup

        if seeds_enabled_for_startup():
            await run_startup_seeds()
    yield

# ── Importar todos los routers si ────────────────────────────────
from app.modules.acceso_y_administracion.auth.router import auth_router
from app.modules.acceso_y_administracion.permisos.router import permisos_router
from app.modules.acceso_y_administracion.roles.router import roles_router
from app.modules.acceso_y_administracion.usuarios.router import router as usuarios_router, clientes_router
from app.modules.clientes_y_vehiculos.vehiculos.router import router as vehiculos_router
from app.modules.talleres_y_tecnicos.talleres.router import router, especialidades_router, tecnicos_router
from app.modules.acceso_y_administracion.bitacora.router import router as bitacora_router
from app.modules.acceso_y_administracion.admin_finanzas.router import (
    router as admin_finanzas_router,
)
from app.modules.acceso_y_administracion.admin_dashboard.router import (
    router as admin_dashboard_router,
)
from app.modules.acceso_y_administracion.tenants.router import router as tenants_router
from app.modules.acceso_y_administracion.public_tenants.router import router as public_tenants_router
from app.modules.acceso_y_administracion.pricing_plans.router import (
    admin_router as pricing_plans_admin_router,
    public_router as pricing_public_router,
)
from app.modules.acceso_y_administracion.billing.router import router as billing_webhooks_router
from app.modules.talleres_y_tecnicos.taller_responsable.router import router as taller_responsable_router
from app.modules.atencion.taller_emergencias.router import router as taller_emergencias_router
from app.modules.clientes_y_vehiculos.clientes.router import router as clientes_app_router
from app.modules.incidentes.emergencias.router import router as emergencias_router
from app.modules.comunicacion_y_notificaciones.comunicaciones.router import (
    cliente_router as comunicaciones_cliente_router,
    emergencias_mensajes_cliente_router,
    tecnico_router as comunicaciones_tecnico_router,
    taller_router as comunicaciones_taller_router,
)
from app.modules.talleres_y_tecnicos.tecnico.router import router as tecnico_router
from app.modules.pagos_y_comisiones.pagos.router import emergencias_pagos_cliente_router
from app.modules.ai.router import router as ai_router

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

# ── Tenant slug (X-Tenant-Slug) antes de CORS ─────────────────
app.add_middleware(TenantSlugMiddleware)

# ── CORS ──────────────────────────────────────────────────────
# En producción, CORS_ORIGINS debe ser solo el dominio del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Tenant-Slug"],
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
app.include_router(admin_finanzas_router, prefix=PREFIX)
app.include_router(admin_dashboard_router, prefix=PREFIX)
app.include_router(tenants_router, prefix=PREFIX)
app.include_router(public_tenants_router, prefix=PREFIX)
app.include_router(pricing_plans_admin_router, prefix=PREFIX)
app.include_router(pricing_public_router, prefix=PREFIX)
app.include_router(billing_webhooks_router, prefix=PREFIX)
app.include_router(taller_responsable_router, prefix=PREFIX)
app.include_router(taller_emergencias_router, prefix=PREFIX)
app.include_router(clientes_app_router, prefix=PREFIX)
app.include_router(emergencias_router, prefix=PREFIX)
app.include_router(comunicaciones_cliente_router, prefix=PREFIX)
app.include_router(emergencias_mensajes_cliente_router, prefix=PREFIX)
app.include_router(comunicaciones_tecnico_router, prefix=PREFIX)
app.include_router(comunicaciones_taller_router, prefix=PREFIX)
app.include_router(tecnico_router, prefix=PREFIX)
app.include_router(emergencias_pagos_cliente_router, prefix=PREFIX)
app.include_router(ai_router, prefix=PREFIX)

# Archivos de evidencia (foto/audio) servidos en HTTPS/HTTP según el entorno. si
_evid_dir = settings.evidencias_upload_dir
_evid_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    f"{PREFIX}/media/evidencias",
    StaticFiles(directory=str(_evid_dir)),
    name="evidencias_media",
)


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
