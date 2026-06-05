from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.acceso_y_administracion.reportes.models import ReportTemplate


async def list_templates(
    db: AsyncSession,
    *,
    tenant_id: int | None,
    taller_id: int | None,
    is_system: bool | None = None,
) -> list[ReportTemplate]:
    stmt = select(ReportTemplate).where(
        or_(
            ReportTemplate.is_system_report.is_(True),
            ReportTemplate.tenant_id == tenant_id,
        )
    )
    if taller_id is not None:
        stmt = stmt.where(
            or_(
                ReportTemplate.is_system_report.is_(True),
                ReportTemplate.taller_id.is_(None),
                ReportTemplate.taller_id == taller_id,
            )
        )
    if is_system is True:
        stmt = stmt.where(ReportTemplate.is_system_report.is_(True))
    elif is_system is False:
        stmt = stmt.where(ReportTemplate.is_system_report.is_(False))
    stmt = stmt.order_by(ReportTemplate.is_system_report.desc(), ReportTemplate.nombre.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: int) -> ReportTemplate | None:
    result = await db.execute(select(ReportTemplate).where(ReportTemplate.id == template_id))
    return result.scalar_one_or_none()


async def create_template(db: AsyncSession, row: ReportTemplate) -> ReportTemplate:
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


async def delete_template(db: AsyncSession, row: ReportTemplate) -> None:
    await db.delete(row)
