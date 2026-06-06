# Seed idempotente: 6 organizaciones SaaS (2 Free, 2 Pro, 2 Max) con taller, técnicos y clientes.
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.roles.models import Rol
from app.modules.acceso_y_administracion.roles.service import (
    asignar_roles_usuario,
    asignar_roles_usuario_seed,
)
from app.modules.acceso_y_administracion.tenants import service as tenants_service
from app.modules.acceso_y_administracion.tenants.models import EstadoTenantEnum, Tenant
from app.modules.acceso_y_administracion.usuarios import service as usuarios_service
from app.modules.acceso_y_administracion.usuarios.models import EstadoUsuarioEnum, Usuario
from app.modules.clientes_y_vehiculos.clientes.models import Cliente
from app.modules.clientes_y_vehiculos.vehiculos import service as vehiculos_service
from app.modules.clientes_y_vehiculos.vehiculos.models import MarcaVehiculo, ModeloVehiculo, TipoVehiculo, Vehiculo
from app.modules.talleres_y_tecnicos.talleres import service as talleres_service
from app.modules.talleres_y_tecnicos.talleres.models import EstadoTallerEnum, EstadoTecnicoEnum, Taller, Tecnico
from app.seeds.identidades_multi_org import MULTI_ORG_PASSWORD, MULTI_ORGS, OrgSeed, PersonaSeed

logger = logging.getLogger(__name__)

DEMO_MARKER = "[MULTI-ORG]"


async def _rol_id(db: AsyncSession, nombre: str) -> int | None:
    r = await db.execute(select(Rol.id).where(Rol.nombre == nombre))
    row = r.scalar_one_or_none()
    if row is None:
        logger.error("Seed multi-org: falta rol %s (migrations/init.sql).", nombre)
        return None
    return int(row)


async def _vehicle_catalog_ids(db: AsyncSession) -> tuple[int, int, int] | None:
    tr = await db.execute(select(TipoVehiculo).where(TipoVehiculo.nombre == "Sedán"))
    tipo = tr.scalar_one_or_none()
    mr = await db.execute(select(MarcaVehiculo).where(MarcaVehiculo.nombre == "Toyota"))
    marca = mr.scalar_one_or_none()
    if tipo is None or marca is None:
        logger.warning("Seed multi-org: catálogo vehículo incompleto (corré ensure_catalogos_vehiculo_demo).")
        return None
    modr = await db.execute(
        select(ModeloVehiculo).where(
            ModeloVehiculo.marca_id == marca.id,
            ModeloVehiculo.nombre == "Corolla",
        )
    )
    modelo = modr.scalar_one_or_none()
    if modelo is None:
        return None
    return tipo.id, marca.id, modelo.id


async def _ensure_tenant(db: AsyncSession, org: OrgSeed) -> Tenant:
    existing = await tenants_service.get_tenant_by_slug(db, org.slug)
    now = utc_now_naive()
    if existing is not None:
        changed = False
        if existing.nombre != org.nombre:
            existing.nombre = org.nombre
            changed = True
        if existing.plan != org.plan:
            existing.plan = org.plan
            changed = True
        if existing.estado != EstadoTenantEnum.ACTIVO:
            existing.estado = EstadoTenantEnum.ACTIVO
            changed = True
        if changed:
            existing.updated_at = now
        return existing
    return await tenants_service.create_tenant(
        db,
        {"slug": org.slug, "nombre": org.nombre, "plan": org.plan},
    )


async def _ensure_staff_user(
    db: AsyncSession,
    *,
    email: str,
    telefono: str,
    nombres: str,
    apellidos: str,
    tenant_id: int,
    rol_id: int,
    password: str,
) -> Usuario:
    now = utc_now_naive()
    res = await db.execute(select(Usuario).where(Usuario.email == email))
    user = res.scalar_one_or_none()
    if user is None:
        user = await usuarios_service.create_usuario(
            {
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email,
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
    await asignar_roles_usuario(user.id, [rol_id], db)
    return user


async def _ensure_taller(
    db: AsyncSession,
    *,
    org: OrgSeed,
    responsable: Usuario,
    tenant_id: int,
) -> Taller:
    now = utc_now_naive()
    t_res = await db.execute(select(Taller).where(Taller.usuario_responsable_id == responsable.id))
    taller = t_res.scalar_one_or_none()
    payload = {
        "tenant_id": tenant_id,
        "usuario_responsable_id": responsable.id,
        "nombre_comercial": org.taller_nombre,
        "telefono_contacto": responsable.telefono,
        "email_contacto": responsable.email,
        "direccion": org.taller_direccion,
        "ciudad": org.ciudad,
        "latitud": org.lat,
        "longitud": org.lng,
        "descripcion": f"{DEMO_MARKER} {org.taller_descripcion}",
        "estado": EstadoTallerEnum.ACTIVO,
    }
    if taller is not None:
        for key, value in payload.items():
            setattr(taller, key, value)
        taller.updated_at = now
        return taller

    async with db.begin_nested():
        try:
            taller = await talleres_service.create_taller(payload, db, ejecutor_id=responsable.id)
        except IntegrityError:
            logger.warning("Seed multi-org: carrera al crear taller %s", org.slug)
            t_res2 = await db.execute(
                select(Taller).where(Taller.usuario_responsable_id == responsable.id)
            )
            taller = t_res2.scalar_one_or_none()
            if taller is None:
                raise
    return taller


async def _ensure_tecnico(
    db: AsyncSession,
    *,
    persona: PersonaSeed,
    org: OrgSeed,
    tenant_id: int,
    taller_id: int,
    rol_tecnico_id: int,
    password: str,
) -> None:
    email = org.email(persona)
    user = await _ensure_staff_user(
        db,
        email=email,
        telefono=persona.telefono,
        nombres=persona.nombres,
        apellidos=persona.apellidos,
        tenant_id=tenant_id,
        rol_id=rol_tecnico_id,
        password=password,
    )
    ex = (await db.execute(select(Tecnico).where(Tecnico.usuario_id == user.id))).scalar_one_or_none()
    if ex is not None:
        if ex.taller_id != taller_id:
            ex.taller_id = taller_id
            ex.updated_at = utc_now_naive()
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


async def _ensure_cliente(
    db: AsyncSession,
    *,
    persona: PersonaSeed,
    org: OrgSeed,
    tenant_id: int,
    placa: str,
    rol_cliente_id: int,
    password: str,
    catalog: tuple[int, int, int] | None,
) -> None:
    tipo_id, marca_id, modelo_id = (catalog or (0, 0, 0))
    email = org.email(persona)
    now = utc_now_naive()
    res = await db.execute(select(Usuario).where(Usuario.email == email))
    user = res.scalar_one_or_none()
    if user is None:
        user = await usuarios_service.create_usuario(
            {
                "nombres": persona.nombres,
                "apellidos": persona.apellidos,
                "email": email,
                "telefono": persona.telefono,
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
        user.updated_at = now

    c_res = await db.execute(select(Cliente).where(Cliente.usuario_id == user.id))
    cliente = c_res.scalar_one_or_none()
    if cliente is None:
        cliente = await usuarios_service.create_cliente(
            {
                "usuario_id": user.id,
                "tenant_id": tenant_id,
                "ciudad": org.ciudad,
                "direccion": f"{DEMO_MARKER} Cliente demo {org.slug}",
            },
            db,
        )
    else:
        cliente.tenant_id = tenant_id
        cliente.ciudad = org.ciudad
        cliente.updated_at = now

    await asignar_roles_usuario_seed(user.id, [rol_cliente_id], db)

    if catalog is None:
        return

    v_res = await db.execute(
        select(Vehiculo).where(Vehiculo.cliente_id == cliente.id, Vehiculo.placa == placa)
    )
    if v_res.scalar_one_or_none() is not None:
        return

    existing_placa = await db.execute(
        select(Vehiculo).where(Vehiculo.tenant_id == tenant_id, Vehiculo.placa == placa)
    )
    if existing_placa.scalar_one_or_none() is not None:
        return

    await vehiculos_service.create_vehiculo(
        {
            "cliente_id": cliente.id,
            "tenant_id": tenant_id,
            "placa": placa,
            "marca_id": marca_id,
            "modelo_id": modelo_id,
            "tipo_vehiculo_id": tipo_id,
            "anio": 2019,
            "color": "Plata",
        },
        db,
        ejecutor_id=user.id,
    )


async def _seed_one_org(
    db: AsyncSession,
    org: OrgSeed,
    *,
    rol_responsable_id: int,
    rol_tecnico_id: int,
    rol_cliente_id: int,
    catalog: tuple[int, int, int] | None,
    password: str,
) -> None:
    tenant = await _ensure_tenant(db, org)
    tenant_id = tenant.id

    responsable = await _ensure_staff_user(
        db,
        email=org.email(org.responsable),
        telefono=org.responsable.telefono,
        nombres=org.responsable.nombres,
        apellidos=org.responsable.apellidos,
        tenant_id=tenant_id,
        rol_id=rol_responsable_id,
        password=password,
    )
    taller = await _ensure_taller(db, org=org, responsable=responsable, tenant_id=tenant_id)

    for persona in org.tecnicos:
        await _ensure_tecnico(
            db,
            persona=persona,
            org=org,
            tenant_id=tenant_id,
            taller_id=taller.id,
            rol_tecnico_id=rol_tecnico_id,
            password=password,
        )

    for persona, placa in zip(org.clientes, org.placas, strict=True):
        await _ensure_cliente(
            db,
            persona=persona,
            org=org,
            tenant_id=tenant_id,
            placa=placa,
            rol_cliente_id=rol_cliente_id,
            password=password,
            catalog=catalog,
        )

    logger.info(
        "Seed multi-org OK: %s (%s) — taller=%s, tecnicos=%s, clientes=%s",
        org.slug,
        org.plan.value,
        org.taller_nombre,
        len(org.tecnicos),
        len(org.clientes),
    )


async def ensure_multi_orgs_seed(
    db: AsyncSession,
    *,
    require_enabled_flag: bool = True,
) -> None:
    """6 tenants demo: 2 Free, 2 Pro, 2 Max; cada uno con taller + 2 técnicos + 2 clientes + vehículos."""
    if require_enabled_flag and not settings.SEED_MULTI_ORGS_ON_START:
        return

    password = (settings.SEED_MULTI_ORGS_PASSWORD or MULTI_ORG_PASSWORD or "").strip()
    if not password:
        logger.warning("Seed multi-org omitido: SEED_MULTI_ORGS_PASSWORD vacío.")
        return

    rol_responsable_id = await _rol_id(db, "TALLER_RESPONSABLE")
    rol_tecnico_id = await _rol_id(db, "TECNICO")
    rol_cliente_id = await _rol_id(db, "CLIENTE")
    if rol_responsable_id is None or rol_tecnico_id is None or rol_cliente_id is None:
        return

    catalog = await _vehicle_catalog_ids(db)
    if catalog is None:
        logger.warning("Seed multi-org: sin catálogo vehículo; clientes sin vehículos.")

    for org in MULTI_ORGS:
        await _seed_one_org(
            db,
            org,
            rol_responsable_id=rol_responsable_id,
            rol_tecnico_id=rol_tecnico_id,
            rol_cliente_id=rol_cliente_id,
            catalog=catalog,
            password=password,
        )

    logger.info("Seed multi-org: %s organizaciones aseguradas.", len(MULTI_ORGS))
