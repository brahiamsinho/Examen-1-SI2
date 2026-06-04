# Contexto de tenant por petición (header X-Tenant-Slug + AuthContext) y SET LOCAL para RLS.
from __future__ import annotations

from contextvars import ContextVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import AuthContext

# Slug enviado por cliente (login móvil / API explícita)
request_tenant_slug: ContextVar[str | None] = ContextVar("request_tenant_slug", default=None)

# Contexto de auth resuelto en la petición (después del JWT)
request_auth_context: ContextVar[AuthContext | None] = ContextVar("request_auth_context", default=None)


def set_request_tenant_slug(slug: str | None) -> None:
    request_tenant_slug.set(slug.strip().lower() if slug else None)


def get_request_tenant_slug() -> str | None:
    return request_tenant_slug.get()


def set_request_auth_context(ctx: AuthContext | None) -> None:
    request_auth_context.set(ctx)


def get_request_auth_context() -> AuthContext | None:
    return request_auth_context.get()


async def apply_postgres_tenant_session(db: AsyncSession, ctx: AuthContext | None = None) -> None:
    """
    Aplica variables de sesión PostgreSQL para políticas RLS.
    Superadmin plataforma: bypass_rls=on. Usuario de tenant: app.tenant_id=<id>.
    """
    ctx = ctx or get_request_auth_context()
    if ctx is None:
        return
    if ctx.is_platform_superadmin:
        await db.execute(text("SELECT set_config('app.bypass_rls', 'on', true)"))
        return
    if ctx.tenant_id is not None:
        await db.execute(
            text("SELECT set_config('app.tenant_id', :tid, true)"),
            {"tid": str(ctx.tenant_id)},
        )


def effective_list_tenant_id(ctx: AuthContext | None, query_tenant_id: int | None = None) -> int | None:
    """Tenant para filtrar listados admin: superadmin puede pasar ?tenant_id=; resto usa el suyo."""
    if ctx is None:
        return query_tenant_id
    if ctx.is_platform_superadmin:
        return query_tenant_id
    return ctx.tenant_id
