from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.core.database import get_db
from app.modules.acceso_y_administracion.billing import service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe-saas", status_code=status.HTTP_204_NO_CONTENT)
async def webhook_stripe_saas(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Eventos de suscripción SaaS (Stripe Billing). Configurar endpoint en dashboard Stripe."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    await service.procesar_webhook_stripe_saas(db, payload, sig)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
