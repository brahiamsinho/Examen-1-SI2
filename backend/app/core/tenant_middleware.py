# Middleware: resuelve slug de tenant (header X-Tenant-Slug o subdominio del Host).
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.tenant_context import set_request_tenant_slug
from app.core.tenant_resolve import slug_from_host


class TenantSlugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        slug = request.headers.get("X-Tenant-Slug") or request.headers.get("x-tenant-slug")
        if not slug:
            host = request.headers.get("host") or request.url.hostname
            slug = slug_from_host(host, settings.SAAS_PLATFORM_BASE_DOMAIN)
        set_request_tenant_slug(slug)
        return await call_next(request)
