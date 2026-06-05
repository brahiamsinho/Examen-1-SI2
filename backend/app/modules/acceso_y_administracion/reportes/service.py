from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.reportes import repository
from app.modules.acceso_y_administracion.reportes.models import ReportTemplate
from app.modules.acceso_y_administracion.reportes.schemas import (
    ReportExecuteIn,
    ReportTemplateCreate,
    ReportTemplateUpdate,
)
from app.modules.acceso_y_administracion.reportes.services.nl_translator import translate_nl_to_qbe
from app.modules.acceso_y_administracion.reportes.services.qbe_engine import (
    QBEEngine,
    QBEScope,
    QBESafeQueryError,
    validate_qbe_payload,
)


def _scope_for_taller(tenant_id: int | None, taller_id: int) -> QBEScope:
    return QBEScope(tenant_id=tenant_id, taller_id=taller_id)


def _can_access_template(row: ReportTemplate, *, tenant_id: int | None, taller_id: int) -> bool:
    if row.is_system_report:
        return True
    if row.tenant_id != tenant_id:
        return False
    return row.taller_id is None or row.taller_id == taller_id


async def list_plantillas(
    db: AsyncSession,
    *,
    tenant_id: int | None,
    taller_id: int,
    is_system: bool | None = None,
) -> list[ReportTemplate]:
    return await repository.list_templates(
        db, tenant_id=tenant_id, taller_id=taller_id, is_system=is_system
    )


async def get_plantilla_or_404(
    db: AsyncSession,
    template_id: int,
    *,
    tenant_id: int | None,
    taller_id: int,
) -> ReportTemplate:
    row = await repository.get_template(db, template_id)
    if row is None or not _can_access_template(row, tenant_id=tenant_id, taller_id=taller_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Plantilla no encontrada.')
    return row


async def create_plantilla(
    db: AsyncSession,
    body: ReportTemplateCreate,
    *,
    tenant_id: int | None,
    taller_id: int,
    user_id: int,
) -> ReportTemplate:
    payload = body.qbe_payload.model_dump()
    try:
        validate_qbe_payload(payload)
    except QBESafeQueryError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    now = utc_now_naive()
    row = ReportTemplate(
        tenant_id=tenant_id,
        taller_id=taller_id,
        nombre=body.nombre.strip(),
        descripcion=body.descripcion or '',
        qbe_payload=payload,
        is_system_report=False,
        created_by_id=user_id,
        created_at=now,
        updated_at=now,
    )
    return await repository.create_template(db, row)


async def update_plantilla(
    db: AsyncSession,
    row: ReportTemplate,
    body: ReportTemplateUpdate,
) -> ReportTemplate:
    if row.is_system_report:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Los reportes predefinidos no se pueden modificar.')
    data = body.model_dump(exclude_none=True)
    if 'qbe_payload' in data and data['qbe_payload'] is not None:
        payload = data['qbe_payload'].model_dump() if hasattr(data['qbe_payload'], 'model_dump') else data['qbe_payload']
        try:
            validate_qbe_payload(payload)
        except QBESafeQueryError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        row.qbe_payload = payload
    if 'nombre' in data:
        row.nombre = data['nombre'].strip()
    if 'descripcion' in data:
        row.descripcion = data['descripcion'] or ''
    row.updated_at = utc_now_naive()
    return row


async def delete_plantilla(db: AsyncSession, row: ReportTemplate) -> None:
    if row.is_system_report:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Los reportes predefinidos no se pueden eliminar.')
    await repository.delete_template(db, row)


async def execute_qbe(
    db: AsyncSession,
    body: ReportExecuteIn | dict[str, Any],
    *,
    tenant_id: int | None,
    taller_id: int,
) -> dict[str, Any]:
    payload = body.model_dump() if hasattr(body, 'model_dump') else dict(body)
    engine = QBEEngine(_scope_for_taller(tenant_id, taller_id))
    try:
        return await engine.execute(db, payload)
    except QBESafeQueryError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


async def run_plantilla(
    db: AsyncSession,
    row: ReportTemplate,
    *,
    tenant_id: int | None,
    taller_id: int,
) -> dict[str, Any]:
    payload = dict(row.qbe_payload or {})
    report = await execute_qbe(db, payload, tenant_id=tenant_id, taller_id=taller_id)
    return {'qbe': payload, 'report': report}


def nl_query(text: str, *, tenant_id: int | None, taller_id: int) -> dict[str, Any]:
    scope = _scope_for_taller(tenant_id, taller_id)
    try:
        return translate_nl_to_qbe(text, scope)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
