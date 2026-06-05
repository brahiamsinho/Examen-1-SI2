"""API portal taller — reportes personalizados QBE + voz + exportación."""
from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.acceso_y_administracion.reportes import service
from app.modules.acceso_y_administracion.reportes.schemas import (
    NlQueryIn,
    NlQueryOut,
    ReportExecuteIn,
    ReportExecuteOut,
    ReportRunTemplateOut,
    ReportTemplateCreate,
    ReportTemplateRead,
    ReportTemplateUpdate,
    VoiceQueryOut,
)
from app.modules.acceso_y_administracion.reportes.services.export_engine import (
    qbe_result_to_csv_bytes,
    qbe_result_to_excel_bytes,
    qbe_result_to_pdf_bytes,
)
from app.modules.acceso_y_administracion.usuarios.models import Usuario
from app.modules.ai.services import inference_client
from app.modules.talleres_y_tecnicos.taller_responsable.router import require_taller_responsable
from app.modules.talleres_y_tecnicos.talleres.models import Taller

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/app/taller/reportes", tags=["App taller - Reportes"])

_EXPORT_BUILDERS = {
    'excel': (qbe_result_to_excel_bytes, 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'pdf': (qbe_result_to_pdf_bytes, 'pdf', 'application/pdf'),
    'csv': (qbe_result_to_csv_bytes, 'csv', 'text/csv; charset=utf-8'),
}


def _slugify(value: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9_-]+', '-', value.strip().lower())
    return s.strip('-') or 'reporte'


def _ctx(db: AsyncSession, user_taller: tuple[Usuario, Taller]) -> tuple[int | None, int, Usuario, Taller]:
    user, taller = user_taller
    tenant_id = user.tenant_id or taller.tenant_id
    return tenant_id, taller.id, user, taller


@router.get(
    '/plantillas',
    response_model=list[ReportTemplateRead],
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def listar_plantillas(
    is_system_report: bool | None = Query(default=None),
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    rows = await service.list_plantillas(
        db, tenant_id=tenant_id, taller_id=taller_id, is_system=is_system_report
    )
    return [ReportTemplateRead.model_validate(r) for r in rows]


@router.post(
    '/plantillas',
    response_model=ReportTemplateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission('reportes:crear'))],
)
async def crear_plantilla(
    body: ReportTemplateCreate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, user, _ = _ctx(db, ctx)
    row = await service.create_plantilla(
        db, body, tenant_id=tenant_id, taller_id=taller_id, user_id=user.id
    )
    await db.commit()
    await db.refresh(row)
    return ReportTemplateRead.model_validate(row)


@router.get(
    '/plantillas/{template_id}',
    response_model=ReportTemplateRead,
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def obtener_plantilla(
    template_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    row = await service.get_plantilla_or_404(
        db, template_id, tenant_id=tenant_id, taller_id=taller_id
    )
    return ReportTemplateRead.model_validate(row)


@router.put(
    '/plantillas/{template_id}',
    response_model=ReportTemplateRead,
    dependencies=[Depends(require_permission('reportes:actualizar'))],
)
async def actualizar_plantilla(
    template_id: int,
    body: ReportTemplateUpdate,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    row = await service.get_plantilla_or_404(
        db, template_id, tenant_id=tenant_id, taller_id=taller_id
    )
    row = await service.update_plantilla(db, row, body)
    await db.commit()
    await db.refresh(row)
    return ReportTemplateRead.model_validate(row)


@router.delete(
    '/plantillas/{template_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission('reportes:eliminar'))],
)
async def eliminar_plantilla(
    template_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    row = await service.get_plantilla_or_404(
        db, template_id, tenant_id=tenant_id, taller_id=taller_id
    )
    await service.delete_plantilla(db, row)
    await db.commit()


@router.post(
    '/plantillas/{template_id}/run',
    response_model=ReportRunTemplateOut,
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def ejecutar_plantilla(
    template_id: int,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    row = await service.get_plantilla_or_404(
        db, template_id, tenant_id=tenant_id, taller_id=taller_id
    )
    result = await service.run_plantilla(db, row, tenant_id=tenant_id, taller_id=taller_id)
    return ReportRunTemplateOut(
        qbe=result['qbe'],
        report=ReportExecuteOut.model_validate(result['report']),
    )


@router.post(
    '/execute',
    response_model=ReportExecuteOut,
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def ejecutar_qbe(
    body: ReportExecuteIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    result = await service.execute_qbe(db, body, tenant_id=tenant_id, taller_id=taller_id)
    return ReportExecuteOut.model_validate(result)


@router.post(
    '/nl-query',
    response_model=NlQueryOut,
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def consulta_nl(
    body: NlQueryIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    result = service.nl_query(body.query, tenant_id=tenant_id, taller_id=taller_id)
    return NlQueryOut.model_validate(result)


@router.post(
    '/voice',
    response_model=VoiceQueryOut,
    dependencies=[Depends(require_permission('reportes:leer'))],
)
async def consulta_voz(
    file: UploadFile = File(...),
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    if not settings.AI_ENABLED and not settings.AI_INFERENCE_STUB:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Transcripción por voz requiere IA habilitada (AI_ENABLED) o use el micrófono del navegador.',
        )
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    raw = await file.read()
    if len(raw) > settings.AI_MAX_AUDIO_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='Audio demasiado grande.')
    try:
        data = await inference_client.call_transcribe_audio(
            raw,
            file.filename or 'audio.bin',
            file.content_type or 'application/octet-stream',
        )
    except Exception as exc:
        _log.exception('reportes voice transcribe')
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f'No se pudo transcribir el audio: {exc!s}',
        ) from exc

    text = str(data.get('text') or '').strip()
    if not text:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='No se detectó texto en el audio.')
    conf = float(data.get('confidence') or 0.0)
    conf = max(0.0, min(1.0, conf))
    nl = service.nl_query(text, tenant_id=tenant_id, taller_id=taller_id)
    return VoiceQueryOut(transcripcion=text, confianza=conf, **nl)


@router.post(
    '/export/{fmt}',
    dependencies=[Depends(require_permission('reportes:exportar'))],
)
async def exportar_reporte(
    fmt: str,
    body: ReportExecuteIn,
    ctx: tuple[Usuario, Taller] = Depends(require_taller_responsable),
    db: AsyncSession = Depends(get_db),
):
    fmt_norm = fmt.lower().strip()
    if fmt_norm not in _EXPORT_BUILDERS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Formato no soportado. Use excel, pdf o csv.')
    tenant_id, taller_id, _, _ = _ctx(db, ctx)
    result = await service.execute_qbe(db, body, tenant_id=tenant_id, taller_id=taller_id)
    builder, ext, content_type = _EXPORT_BUILDERS[fmt_norm]
    buffer = builder(result)
    model_slug = _slugify(str(result.get('meta', {}).get('model') or 'reporte'))
    filename = f'reporte-{model_slug}.{ext}'
    return Response(
        content=buffer.getvalue(),
        media_type=content_type,
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )
