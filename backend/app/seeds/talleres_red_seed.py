# Seed reutilizable: red mínima de talleres por tenant + horarios/disponibilidad default.
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.roles.service import asignar_roles_usuario
from app.modules.acceso_y_administracion.usuarios import service as usuarios_service
from app.modules.acceso_y_administracion.usuarios.models import EstadoUsuarioEnum, Usuario
from app.modules.atencion.taller_emergencias import repository as pt_repo
from app.modules.talleres_y_tecnicos.talleres import horarios_service
from app.modules.talleres_y_tecnicos.talleres import service as talleres_service
from app.modules.acceso_y_administracion.roles.models import Rol
from app.modules.talleres_y_tecnicos.talleres.models import EstadoTecnicoEnum, EstadoTallerEnum, Taller, Tecnico
from app.seeds.identidades_demo_sc import (
    CIUDAD_SANTA_CRUZ,
    DEMO_PASSWORD,
    TALLER3_DIRECCION,
    TALLER3_EMAIL,
    TALLER3_LAT,
    TALLER3_LNG,
    TALLER3_NOMBRE_COMERCIAL,
    TALLER3_RESPONSABLE_APELLIDOS,
    TALLER3_RESPONSABLE_NOMBRES,
    TALLER3_TELEFONO,
    TALLER4_DIRECCION,
    TALLER4_EMAIL,
    TALLER4_LAT,
    TALLER4_LNG,
    TALLER4_NOMBRE_COMERCIAL,
    TALLER4_RESPONSABLE_APELLIDOS,
    TALLER4_RESPONSABLE_NOMBRES,
    TALLER4_TELEFONO,
    TALLER5_DIRECCION,
    TALLER5_EMAIL,
    TALLER5_LAT,
    TALLER5_LNG,
    TALLER5_NOMBRE_COMERCIAL,
    TALLER5_RESPONSABLE_APELLIDOS,
    TALLER5_RESPONSABLE_NOMBRES,
    TALLER5_TELEFONO,
    TALLER6_DIRECCION,
    TALLER6_EMAIL,
    TALLER6_LAT,
    TALLER6_LNG,
    TALLER6_NOMBRE_COMERCIAL,
    TALLER6_RESPONSABLE_APELLIDOS,
    TALLER6_RESPONSABLE_NOMBRES,
    TALLER6_TELEFONO,
    TALLER2_DIRECCION,
    TALLER2_DESCRIPCION,
    TALLER2_EMAIL,
    TALLER2_LAT,
    TALLER2_LNG,
    TALLER2_NOMBRE_COMERCIAL,
    TALLER2_RESPONSABLE_APELLIDOS,
    TALLER2_RESPONSABLE_NOMBRES,
    TALLER2_TELEFONO,
    TALLER_EMAIL,
    TECNICO2_APELLIDOS,
    TECNICO2_EMAIL,
    TECNICO2_NOMBRES,
    TECNICO2_TELEFONO,
    TECNICO3_APELLIDOS,
    TECNICO3_EMAIL,
    TECNICO3_NOMBRES,
    TECNICO3_TELEFONO,
    TECNICO4_APELLIDOS,
    TECNICO4_EMAIL,
    TECNICO4_NOMBRES,
    TECNICO4_TELEFONO,
    TECNICO5_APELLIDOS,
    TECNICO5_EMAIL,
    TECNICO5_NOMBRES,
    TECNICO5_TELEFONO,
    TECNICO6_APELLIDOS,
    TECNICO6_EMAIL,
    TECNICO6_NOMBRES,
    TECNICO6_TELEFONO,
    TECNICO_APELLIDOS,
    TECNICO_EMAIL,
    TECNICO_NOMBRES,
    TECNICO_TELEFONO,
)

logger = logging.getLogger(__name__)

RED_MARKER = "[TALLERES-RED]"
MIN_TALLERES_POR_TENANT = 5


@dataclass(frozen=True)
class ExtraTallerDef:
    email: str
    telefono: str
    nombres: str
    apellidos: str
    nombre_comercial: str
    direccion: str
    ciudad: str
    lat: Decimal
    lng: Decimal
    descripcion: str
    password: str = DEMO_PASSWORD
    tecnico_email: str = ""
    tecnico_telefono: str = ""
    tecnico_nombres: str = "Técnico"
    tecnico_apellidos: str = "Red"


@dataclass(frozen=True)
class TecnicoRedDef:
    """Técnico asignado a un taller identificado por email del responsable."""

    responsable_email: str
    email: str
    telefono: str
    nombres: str
    apellidos: str
    password: str = DEMO_PASSWORD


DEMO_SC_TECNICOS_RED: tuple[TecnicoRedDef, ...] = (
    TecnicoRedDef(
        TALLER_EMAIL,
        TECNICO_EMAIL,
        TECNICO_TELEFONO,
        TECNICO_NOMBRES,
        TECNICO_APELLIDOS,
    ),
    TecnicoRedDef(
        TALLER2_EMAIL,
        TECNICO2_EMAIL,
        TECNICO2_TELEFONO,
        TECNICO2_NOMBRES,
        TECNICO2_APELLIDOS,
    ),
    TecnicoRedDef(
        TALLER3_EMAIL,
        TECNICO3_EMAIL,
        TECNICO3_TELEFONO,
        TECNICO3_NOMBRES,
        TECNICO3_APELLIDOS,
    ),
    TecnicoRedDef(
        TALLER4_EMAIL,
        TECNICO4_EMAIL,
        TECNICO4_TELEFONO,
        TECNICO4_NOMBRES,
        TECNICO4_APELLIDOS,
    ),
    TecnicoRedDef(
        TALLER5_EMAIL,
        TECNICO5_EMAIL,
        TECNICO5_TELEFONO,
        TECNICO5_NOMBRES,
        TECNICO5_APELLIDOS,
    ),
    TecnicoRedDef(
        TALLER6_EMAIL,
        TECNICO6_EMAIL,
        TECNICO6_TELEFONO,
        TECNICO6_NOMBRES,
        TECNICO6_APELLIDOS,
    ),
)


DEMO_SC_EXTRA_TALLERES: tuple[ExtraTallerDef, ...] = (
    ExtraTallerDef(
        TALLER2_EMAIL,
        TALLER2_TELEFONO,
        TALLER2_RESPONSABLE_NOMBRES,
        TALLER2_RESPONSABLE_APELLIDOS,
        TALLER2_NOMBRE_COMERCIAL,
        TALLER2_DIRECCION,
        CIUDAD_SANTA_CRUZ,
        TALLER2_LAT,
        TALLER2_LNG,
        f"{RED_MARKER} {TALLER2_DESCRIPCION}",
        tecnico_email=TECNICO2_EMAIL,
        tecnico_telefono=TECNICO2_TELEFONO,
        tecnico_nombres=TECNICO2_NOMBRES,
        tecnico_apellidos=TECNICO2_APELLIDOS,
    ),
    ExtraTallerDef(
        TALLER3_EMAIL,
        TALLER3_TELEFONO,
        TALLER3_RESPONSABLE_NOMBRES,
        TALLER3_RESPONSABLE_APELLIDOS,
        TALLER3_NOMBRE_COMERCIAL,
        TALLER3_DIRECCION,
        CIUDAD_SANTA_CRUZ,
        TALLER3_LAT,
        TALLER3_LNG,
        f"{RED_MARKER} Auxilio zona sur y Piraí.",
        tecnico_email=TECNICO3_EMAIL,
        tecnico_telefono=TECNICO3_TELEFONO,
        tecnico_nombres=TECNICO3_NOMBRES,
        tecnico_apellidos=TECNICO3_APELLIDOS,
    ),
    ExtraTallerDef(
        TALLER4_EMAIL,
        TALLER4_TELEFONO,
        TALLER4_RESPONSABLE_NOMBRES,
        TALLER4_RESPONSABLE_APELLIDOS,
        TALLER4_NOMBRE_COMERCIAL,
        TALLER4_DIRECCION,
        CIUDAD_SANTA_CRUZ,
        TALLER4_LAT,
        TALLER4_LNG,
        f"{RED_MARKER} Cobertura Urubó y zona este.",
        tecnico_email=TECNICO4_EMAIL,
        tecnico_telefono=TECNICO4_TELEFONO,
        tecnico_nombres=TECNICO4_NOMBRES,
        tecnico_apellidos=TECNICO4_APELLIDOS,
    ),
    ExtraTallerDef(
        TALLER5_EMAIL,
        TALLER5_TELEFONO,
        TALLER5_RESPONSABLE_NOMBRES,
        TALLER5_RESPONSABLE_APELLIDOS,
        TALLER5_NOMBRE_COMERCIAL,
        TALLER5_DIRECCION,
        CIUDAD_SANTA_CRUZ,
        TALLER5_LAT,
        TALLER5_LNG,
        f"{RED_MARKER} Grúas y auxilio Palermo norte.",
        tecnico_email=TECNICO5_EMAIL,
        tecnico_telefono=TECNICO5_TELEFONO,
        tecnico_nombres=TECNICO5_NOMBRES,
        tecnico_apellidos=TECNICO5_APELLIDOS,
    ),
    ExtraTallerDef(
        TALLER6_EMAIL,
        TALLER6_TELEFONO,
        TALLER6_RESPONSABLE_NOMBRES,
        TALLER6_RESPONSABLE_APELLIDOS,
        TALLER6_NOMBRE_COMERCIAL,
        TALLER6_DIRECCION,
        CIUDAD_SANTA_CRUZ,
        TALLER6_LAT,
        TALLER6_LNG,
        f"{RED_MARKER} Cobertura céntrica 2do anillo.",
        tecnico_email=TECNICO6_EMAIL,
        tecnico_telefono=TECNICO6_TELEFONO,
        tecnico_nombres=TECNICO6_NOMBRES,
        tecnico_apellidos=TECNICO6_APELLIDOS,
    ),
)


def multi_org_extra_taller_defs(
    *,
    slug: str,
    ciudad: str,
    base_lat: Decimal,
    base_lng: Decimal,
    org_idx: int,
    password: str,
) -> tuple[ExtraTallerDef, ...]:
    """Cuatro talleres adicionales por organización (sucursales)."""
    offsets = (
        (Decimal("0.0120"), Decimal("-0.0180"), "Sucursal Norte", "taller-norte"),
        (Decimal("-0.0150"), Decimal("0.0220"), "Sucursal Sur", "taller-sur"),
        (Decimal("0.0080"), Decimal("0.0300"), "Sucursal Este", "taller-este"),
        (Decimal("-0.0100"), Decimal("-0.0250"), "Sucursal Oeste", "taller-oeste"),
    )
    defs: list[ExtraTallerDef] = []
    for j, (dlat, dlng, suffix, local) in enumerate(offsets, start=2):
        tel = f"+5917704{org_idx:01d}{j:02d}"
        tecnico_local = local.replace("taller-", "tecnico-")
        tecnico_tel = f"+5917705{org_idx:01d}{j:02d}"
        sucursal = suffix.replace("Sucursal ", "")
        defs.append(
            ExtraTallerDef(
                email=f"{local}@{slug}.demo.test",
                telefono=tel,
                nombres="Responsable",
                apellidos=suffix.replace(" ", ""),
                nombre_comercial=f"{suffix} — {slug}",
                direccion=f"{RED_MARKER} {suffix}, {ciudad}",
                ciudad=ciudad,
                lat=base_lat + dlat,
                lng=base_lng + dlng,
                descripcion=f"{RED_MARKER} Red multi-sucursal ({suffix}).",
                password=password,
                tecnico_email=f"{tecnico_local}@{slug}.demo.test",
                tecnico_telefono=tecnico_tel,
                tecnico_nombres="Técnico",
                tecnico_apellidos=sucursal,
            )
        )
    return tuple(defs)


async def _rol_tecnico_id(db: AsyncSession) -> int | None:
    r = await db.execute(select(Rol.id).where(Rol.nombre == "TECNICO"))
    row = r.scalar_one_or_none()
    if row is None:
        logger.error("Talleres red: falta rol TECNICO.")
        return None
    return int(row)


async def _find_taller_by_responsable_email(
    db: AsyncSession,
    *,
    responsable_email: str,
    tenant_id: int,
) -> Taller | None:
    email = responsable_email.strip().lower()
    ur = await db.execute(select(Usuario).where(Usuario.email == email))
    user = ur.scalar_one_or_none()
    if user is None:
        return None
    tr = await db.execute(
        select(Taller).where(
            Taller.usuario_responsable_id == user.id,
            Taller.tenant_id == tenant_id,
        )
    )
    return tr.scalar_one_or_none()


async def _ensure_tecnico_for_taller(
    db: AsyncSession,
    *,
    tenant_id: int,
    taller_id: int,
    rol_tecnico_id: int,
    email: str,
    telefono: str,
    nombres: str,
    apellidos: str,
    password: str = DEMO_PASSWORD,
) -> None:
    now = utc_now_naive()
    email_norm = email.strip().lower()
    ur = await db.execute(select(Usuario).where(Usuario.email == email_norm))
    user = ur.scalar_one_or_none()
    if user is None:
        user = await usuarios_service.create_usuario(
            {
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email_norm,
                "telefono": telefono,
                "password": password,
                "username": None,
                "estado": EstadoUsuarioEnum.ACTIVO,
                "tenant_id": tenant_id,
            },
            db,
            ejecutor_id=None,
        )
    else:
        if not verify_password(password, user.password_hash):
            user.password_hash = hash_password(password)
        user.estado = EstadoUsuarioEnum.ACTIVO
        user.tenant_id = tenant_id
        user.nombres = nombres
        user.apellidos = apellidos
        user.telefono = telefono
        user.updated_at = now
    await asignar_roles_usuario(user.id, [rol_tecnico_id], db)

    ex = (await db.execute(select(Tecnico).where(Tecnico.usuario_id == user.id))).scalar_one_or_none()
    if ex is not None:
        if ex.taller_id != taller_id:
            ex.taller_id = taller_id
            ex.updated_at = now
        if ex.estado != EstadoTecnicoEnum.ACTIVO:
            ex.estado = EstadoTecnicoEnum.ACTIVO
            ex.updated_at = now
        await db.flush()
        return

    await talleres_service.create_tecnico(
        {
            "usuario_id": user.id,
            "taller_id": taller_id,
            "especialidad_id": None,
            "estado": EstadoTecnicoEnum.ACTIVO,
        },
        db,
        ejecutor_id=user.id,
    )
    logger.info("Talleres red: técnico %s → taller_id=%s", email_norm, taller_id)


async def ensure_tecnicos_red(
    db: AsyncSession,
    *,
    tenant_id: int,
    defs: tuple[TecnicoRedDef, ...],
) -> None:
    rol_id = await _rol_tecnico_id(db)
    if rol_id is None:
        return
    for item in defs:
        taller = await _find_taller_by_responsable_email(
            db, responsable_email=item.responsable_email, tenant_id=tenant_id
        )
        if taller is None:
            logger.warning(
                "Talleres red: sin taller para responsable %s (técnico %s omitido).",
                item.responsable_email,
                item.email,
            )
            continue
        await _ensure_tecnico_for_taller(
            db,
            tenant_id=tenant_id,
            taller_id=taller.id,
            rol_tecnico_id=rol_id,
            email=item.email,
            telefono=item.telefono,
            nombres=item.nombres,
            apellidos=item.apellidos,
            password=item.password,
        )


async def _ensure_tecnico_from_extra_def(
    db: AsyncSession,
    *,
    tenant_id: int,
    taller_id: int,
    defn: ExtraTallerDef,
) -> None:
    if not defn.tecnico_email:
        return
    rol_id = await _rol_tecnico_id(db)
    if rol_id is None:
        return
    await _ensure_tecnico_for_taller(
        db,
        tenant_id=tenant_id,
        taller_id=taller_id,
        rol_tecnico_id=rol_id,
        email=defn.tecnico_email,
        telefono=defn.tecnico_telefono,
        nombres=defn.tecnico_nombres,
        apellidos=defn.tecnico_apellidos,
        password=defn.password,
    )


async def _count_talleres_tenant(db: AsyncSession, tenant_id: int) -> int:
    r = await db.execute(
        select(func.count(Taller.id)).where(
            Taller.tenant_id == tenant_id,
            Taller.estado == EstadoTallerEnum.ACTIVO,
        )
    )
    return int(r.scalar_one() or 0)


async def _ensure_extra_taller(
    db: AsyncSession,
    *,
    tenant_id: int,
    rol_id: int,
    defn: ExtraTallerDef,
) -> Taller | None:
    now = utc_now_naive()
    email = defn.email.strip().lower()
    ur = await db.execute(select(Usuario).where(Usuario.email == email))
    user = ur.scalar_one_or_none()

    if user is None:
        user = await usuarios_service.create_usuario(
            {
                "nombres": defn.nombres,
                "apellidos": defn.apellidos,
                "email": email,
                "telefono": defn.telefono,
                "password": defn.password,
                "username": None,
                "estado": EstadoUsuarioEnum.ACTIVO,
                "tenant_id": tenant_id,
            },
            db,
            ejecutor_id=None,
        )
        await asignar_roles_usuario(user.id, [rol_id], db)
    else:
        if not verify_password(defn.password, user.password_hash):
            user.password_hash = hash_password(defn.password)
        user.estado = EstadoUsuarioEnum.ACTIVO
        user.tenant_id = tenant_id
        user.updated_at = now
        await asignar_roles_usuario(user.id, [rol_id], db)

    tr = await db.execute(select(Taller).where(Taller.usuario_responsable_id == user.id))
    taller = tr.scalar_one_or_none()
    payload = {
        "tenant_id": tenant_id,
        "usuario_responsable_id": user.id,
        "nombre_comercial": defn.nombre_comercial,
        "telefono_contacto": defn.telefono,
        "email_contacto": email,
        "direccion": defn.direccion,
        "ciudad": defn.ciudad,
        "latitud": defn.lat,
        "longitud": defn.lng,
        "descripcion": defn.descripcion,
        "estado": EstadoTallerEnum.ACTIVO,
    }

    if taller is None:
        async with db.begin_nested():
            try:
                taller = await talleres_service.create_taller(payload, db, ejecutor_id=user.id)
            except IntegrityError:
                logger.warning("Talleres red: carrera al crear %s", email)
        tr2 = await db.execute(select(Taller).where(Taller.usuario_responsable_id == user.id))
        taller = tr2.scalar_one_or_none()
    if taller is None:
        logger.error("Talleres red: no se pudo asegurar taller para %s", email)
        return None

    for key, value in payload.items():
        setattr(taller, key, value)
    taller.updated_at = now
    await db.flush()

    await horarios_service.ensure_default_horarios(db, taller.id)
    disp = await pt_repo.get_disponibilidad(db, taller_id=taller.id)
    if disp is None:
        await pt_repo.insert_disponibilidad_default(db, taller_id=taller.id, updated_at=now)
    await _ensure_tecnico_from_extra_def(db, tenant_id=tenant_id, taller_id=taller.id, defn=defn)
    return taller


async def ensure_min_talleres_red(
    db: AsyncSession,
    *,
    tenant_id: int,
    rol_taller_responsable_id: int,
    extra_defs: tuple[ExtraTallerDef, ...],
    min_count: int = MIN_TALLERES_POR_TENANT,
) -> int:
    """Asegura al menos `min_count` talleres ACTIVO en el tenant. Devuelve total final."""
    for defn in extra_defs:
        current = await _count_talleres_tenant(db, tenant_id)
        if current >= min_count:
            break
        t = await _ensure_extra_taller(
            db,
            tenant_id=tenant_id,
            rol_id=rol_taller_responsable_id,
            defn=defn,
        )
        if t is not None:
            logger.info(
                "Talleres red: taller id=%s (%s) tenant_id=%s",
                t.id,
                t.nombre_comercial,
                tenant_id,
            )

    total = await _count_talleres_tenant(db, tenant_id)
    if total < min_count:
        logger.warning(
            "Talleres red: tenant_id=%s tiene %s talleres (meta %s). Revisa seeds previos.",
            tenant_id,
            total,
            min_count,
        )
    return total


async def ensure_tecnicos_red_for_extra_defs(
    db: AsyncSession,
    *,
    tenant_id: int,
    extra_defs: tuple[ExtraTallerDef, ...],
) -> None:
    """Asegura técnicos en sucursales ya creadas (idempotente)."""
    for defn in extra_defs:
        if not defn.tecnico_email:
            continue
        taller = await _find_taller_by_responsable_email(
            db, responsable_email=defn.email, tenant_id=tenant_id
        )
        if taller is None:
            continue
        await _ensure_tecnico_from_extra_def(
            db, tenant_id=tenant_id, taller_id=taller.id, defn=defn
        )


async def ensure_horarios_y_disponibilidad_tenant(db: AsyncSession, tenant_id: int) -> None:
    """Backfill horarios/disponibilidad en todos los talleres del tenant."""
    r = await db.execute(select(Taller.id).where(Taller.tenant_id == tenant_id))
    now = utc_now_naive()
    for (tid,) in r.fetchall():
        await horarios_service.ensure_default_horarios(db, int(tid))
        disp = await pt_repo.get_disponibilidad(db, taller_id=int(tid))
        if disp is None:
            await pt_repo.insert_disponibilidad_default(db, taller_id=int(tid), updated_at=now)
