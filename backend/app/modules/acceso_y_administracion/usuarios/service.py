# app/modules/usuarios/service.py
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.core.timeutil import utc_now_naive
from app.modules.clientes_y_vehiculos.clientes.models import Cliente
from app.modules.acceso_y_administracion.usuarios.models import Usuario, EstadoUsuarioEnum
from app.modules.acceso_y_administracion.usuarios.schemas import UsuarioListRead, UsuarioRead
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.roles.models import Rol, UsuarioRol


async def get_usuarios(db: AsyncSession, list_tenant_id: int | None = None) -> list[Usuario]:
    stmt = select(Usuario).order_by(Usuario.apellidos)
    if list_tenant_id is not None:
        stmt = stmt.where(Usuario.tenant_id == list_tenant_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_usuarios_admin(
    db: AsyncSession, list_tenant_id: int | None = None
) -> list[UsuarioListRead]:
    users = await get_usuarios(db, list_tenant_id=list_tenant_id)
    res = await db.execute(
        select(UsuarioRol.usuario_id, Rol.nombre).join(Rol, Rol.id == UsuarioRol.rol_id)
    )
    roles_by_user: defaultdict[int, list[str]] = defaultdict(list)
    for uid, nombre in res.fetchall():
        roles_by_user[uid].append(nombre)
    out: list[UsuarioListRead] = []
    for u in users:
        rnames = roles_by_user.get(u.id, [])
        if "CLIENTE" in rnames:
            continue
        base = UsuarioRead.model_validate(u)
        out.append(UsuarioListRead(**base.model_dump(), roles=rnames))
    return out


async def get_usuario_by_id(usuario_id: int, db: AsyncSession) -> Usuario:
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


async def get_usuario_list_read(usuario_id: int, db: AsyncSession) -> UsuarioListRead:
    u = await get_usuario_by_id(usuario_id, db)
    res = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == usuario_id)
    )
    roles = [row[0] for row in res.fetchall()]
    base = UsuarioRead.model_validate(u)
    return UsuarioListRead(**base.model_dump(), roles=roles)


async def _email_taken(db: AsyncSession, email: str, tenant_id: int | None) -> bool:
    em = email.strip().lower()
    stmt = select(Usuario.id).where(func.lower(Usuario.email) == em)
    if tenant_id is None:
        stmt = stmt.where(Usuario.tenant_id.is_(None))
    else:
        stmt = stmt.where(Usuario.tenant_id == tenant_id)
    r = await db.execute(stmt.limit(1))
    return r.scalar_one_or_none() is not None


async def _telefono_taken(db: AsyncSession, telefono: str, tenant_id: int | None) -> bool:
    stmt = select(Usuario.id).where(Usuario.telefono == telefono)
    if tenant_id is None:
        stmt = stmt.where(Usuario.tenant_id.is_(None))
    else:
        stmt = stmt.where(Usuario.tenant_id == tenant_id)
    r = await db.execute(stmt.limit(1))
    return r.scalar_one_or_none() is not None


async def create_usuario(data: dict, db: AsyncSession, ejecutor_id: int | None = None) -> Usuario:
    tenant_id = data.get("tenant_id")
    if await _email_taken(db, data["email"], tenant_id):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    if await _telefono_taken(db, data["telefono"], tenant_id):
        raise HTTPException(status_code=409, detail="El teléfono ya está registrado")

    user = Usuario(
        nombres=data["nombres"],
        apellidos=data["apellidos"],
        email=data["email"],
        telefono=data["telefono"],
        username=data.get("username"),
        password_hash=hash_password(data["password"]),
        estado=data.get("estado", EstadoUsuarioEnum.ACTIVO),
        tenant_id=data.get("tenant_id"),
        created_at=utc_now_naive(),
        updated_at=utc_now_naive(),
    )
    db.add(user)
    await db.flush()  # obtener ID sin commit

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=user.id,
        accion=AccionBitacoraEnum.CREAR,
        descripcion=f"Creación del usuario {user.email}",
    )
    return user


async def update_usuario(
    usuario_id: int, data: dict, db: AsyncSession, ejecutor_id: int | None = None
) -> Usuario:
    user = await get_usuario_by_id(usuario_id, db)
    if "email" in data and data["email"] is not None:
        stmt = (
            select(Usuario.id)
            .where(func.lower(Usuario.email) == data["email"].strip().lower())
            .where(Usuario.id != usuario_id)
        )
        if user.tenant_id is None:
            stmt = stmt.where(Usuario.tenant_id.is_(None))
        else:
            stmt = stmt.where(Usuario.tenant_id == user.tenant_id)
        if (await db.execute(stmt.limit(1))).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="El email ya está registrado")
    if "telefono" in data and data["telefono"] is not None:
        stmt = (
            select(Usuario.id)
            .where(Usuario.telefono == data["telefono"])
            .where(Usuario.id != usuario_id)
        )
        if user.tenant_id is None:
            stmt = stmt.where(Usuario.tenant_id.is_(None))
        else:
            stmt = stmt.where(Usuario.tenant_id == user.tenant_id)
        if (await db.execute(stmt.limit(1))).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="El teléfono ya está registrado")
    for field, value in data.items():
        if value is not None:
            setattr(user, field, value)
    user.updated_at = utc_now_naive()

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Actualización del usuario {usuario_id}",
    )
    if "estado" in data and data["estado"] is not None:
        await _sync_tecnico_estado_on_usuario(usuario_id, user.estado, db)
    return user


async def asignar_roles_usuario(
    usuario_id: int,
    rol_ids: list[int],
    db: AsyncSession,
    ejecutor_id: int,
) -> None:
    await get_usuario_by_id(usuario_id, db)
    from app.modules.acceso_y_administracion.roles import service as roles_service

    await roles_service.asignar_roles_usuario(usuario_id, rol_ids, db)
    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="roles",
        entidad="usuario_rol",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Asignación de roles al usuario {usuario_id}",
    )


async def delete_usuario(usuario_id: int, db: AsyncSession, ejecutor_id: int | None = None) -> None:
    """No elimina físicamente — cambia estado a INACTIVO (soft delete)."""
    user = await get_usuario_by_id(usuario_id, db)
    user.estado = EstadoUsuarioEnum.INACTIVO
    user.updated_at = utc_now_naive()
    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ELIMINAR,
        descripcion=f"Desactivación (soft delete) del usuario {usuario_id}",
    )


async def _assert_usuario_staff_in_tenant(
    usuario_id: int,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
) -> Usuario:
    user = await get_usuario_by_id(usuario_id, db)
    if tenant_id is not None and user.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    res = await db.execute(
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == usuario_id)
    )
    roles = {row[0] for row in res.fetchall()}
    if "CLIENTE" in roles:
        raise HTTPException(
            status_code=400,
            detail="Gestiona clientes desde la pantalla Cuentas clientes.",
        )
    if ejecutor_id is not None and usuario_id == ejecutor_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes desactivar ni eliminar tu propia cuenta.",
        )
    return user


async def _sync_tecnico_estado_on_usuario(
    usuario_id: int, estado: EstadoUsuarioEnum, db: AsyncSession
) -> None:
    from app.modules.talleres_y_tecnicos.talleres.models import EstadoTecnicoEnum, Tecnico

    res = await db.execute(select(Tecnico).where(Tecnico.usuario_id == usuario_id))
    tecnico = res.scalar_one_or_none()
    if not tecnico:
        return
    if estado == EstadoUsuarioEnum.INACTIVO:
        tecnico.estado = EstadoTecnicoEnum.INACTIVO
    elif estado == EstadoUsuarioEnum.ACTIVO:
        tecnico.estado = EstadoTecnicoEnum.ACTIVO
    tecnico.updated_at = utc_now_naive()


async def desactivar_usuario_admin(
    usuario_id: int,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
) -> UsuarioListRead:
    await _assert_usuario_staff_in_tenant(usuario_id, tenant_id, db, ejecutor_id)
    await _sync_tecnico_estado_on_usuario(usuario_id, EstadoUsuarioEnum.INACTIVO, db)
    await delete_usuario(usuario_id, db, ejecutor_id=ejecutor_id)
    return await get_usuario_list_read(usuario_id, db)


async def hard_delete_usuario_admin(
    usuario_id: int,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
) -> None:
    from sqlalchemy import delete as sql_delete

    from app.modules.acceso_y_administracion.auth.models import Sesion
    from app.modules.atencion.taller_emergencias.models import SolicitudAsignacionTecnico
    from app.modules.incidentes.emergencias.models import SolicitudEmergencia
    from app.modules.talleres_y_tecnicos.talleres.models import Taller, Tecnico

    await _assert_usuario_staff_in_tenant(usuario_id, tenant_id, db, ejecutor_id)

    if (await db.execute(select(Taller).where(Taller.usuario_responsable_id == usuario_id))).scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: es responsable de un taller. Desactívalo en su lugar.",
        )

    tech_res = await db.execute(select(Tecnico).where(Tecnico.usuario_id == usuario_id))
    tecnico = tech_res.scalar_one_or_none()
    if tecnico:
        asig = int(
            (
                await db.execute(
                    select(func.count())
                    .select_from(SolicitudAsignacionTecnico)
                    .where(SolicitudAsignacionTecnico.tecnico_id == tecnico.id)
                )
            ).scalar_one()
            or 0
        )
        sol = int(
            (
                await db.execute(
                    select(func.count())
                    .select_from(SolicitudEmergencia)
                    .where(SolicitudEmergencia.tecnico_id == tecnico.id)
                )
            ).scalar_one()
            or 0
        )
        if asig or sol:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar: el usuario tiene historial de atenciones como técnico. Desactívalo.",
            )
        await db.execute(sql_delete(Tecnico).where(Tecnico.id == tecnico.id))

    await db.execute(sql_delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id))
    await db.execute(sql_delete(Sesion).where(Sesion.usuario_id == usuario_id))
    await db.execute(sql_delete(Usuario).where(Usuario.id == usuario_id))

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="usuarios",
        entidad="usuarios",
        entidad_id=usuario_id,
        accion=AccionBitacoraEnum.ELIMINAR,
        descripcion=f"Eliminación física del usuario {usuario_id}",
    )


async def get_clientes(db: AsyncSession, list_tenant_id: int | None = None) -> list[Cliente]:
    stmt = select(Cliente).order_by(Cliente.id.desc())
    if list_tenant_id is not None:
        stmt = stmt.where(Cliente.tenant_id == list_tenant_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_clientes_admin(
    db: AsyncSession, list_tenant_id: int | None = None
) -> list:
    from app.modules.clientes_y_vehiculos.clientes.schemas import ClienteListRead

    stmt = (
        select(Cliente, Usuario)
        .join(Usuario, Usuario.id == Cliente.usuario_id)
        .order_by(Usuario.apellidos, Usuario.nombres)
    )
    if list_tenant_id is not None:
        stmt = stmt.where(Cliente.tenant_id == list_tenant_id)
    rows = (await db.execute(stmt)).all()
    out = []
    for cliente, usuario in rows:
        out.append(
            ClienteListRead(
                id=cliente.id,
                usuario_id=cliente.usuario_id,
                nombres=usuario.nombres,
                apellidos=usuario.apellidos,
                email=usuario.email,
                telefono=usuario.telefono,
                estado=usuario.estado.value if hasattr(usuario.estado, "value") else str(usuario.estado),
                ciudad=cliente.ciudad,
                direccion=cliente.direccion,
                created_at=cliente.created_at,
            )
        )
    return out


async def create_cliente(data: dict, db: AsyncSession) -> Cliente:
    cliente = Cliente(
        usuario_id=data["usuario_id"],
        tenant_id=data.get("tenant_id"),
        ciudad=data.get("ciudad"),
        direccion=data.get("direccion"),
        created_at=utc_now_naive(),
        updated_at=utc_now_naive(),
    )
    db.add(cliente)
    await db.flush()
    return cliente


async def _get_cliente_in_tenant(cliente_id: int, tenant_id: int | None, db: AsyncSession) -> Cliente:
    stmt = select(Cliente).where(Cliente.id == cliente_id)
    if tenant_id is not None:
        stmt = stmt.where(Cliente.tenant_id == tenant_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return row


async def _cliente_list_read_from_row(cliente: Cliente, usuario: Usuario):
    from app.modules.clientes_y_vehiculos.clientes.schemas import ClienteListRead

    return ClienteListRead(
        id=cliente.id,
        usuario_id=cliente.usuario_id,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        email=usuario.email,
        telefono=usuario.telefono,
        estado=usuario.estado.value if hasattr(usuario.estado, "value") else str(usuario.estado),
        ciudad=cliente.ciudad,
        direccion=cliente.direccion,
        created_at=cliente.created_at,
    )


async def create_cliente_admin(
    data: dict,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
):
    from app.modules.acceso_y_administracion.roles.service import asignar_roles_usuario
    from app.modules.acceso_y_administracion.roles.models import Rol

    user = await create_usuario(
        {
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "email": str(data["email"]).lower().strip(),
            "telefono": data["telefono"].strip(),
            "password": data["password"],
            "username": None,
            "estado": data.get("estado", EstadoUsuarioEnum.ACTIVO),
            "tenant_id": tenant_id,
        },
        db,
        ejecutor_id=ejecutor_id,
    )
    cliente = await create_cliente(
        {
            "usuario_id": user.id,
            "tenant_id": tenant_id,
            "ciudad": data.get("ciudad"),
            "direccion": data.get("direccion"),
        },
        db,
    )
    rid = await db.execute(select(Rol.id).where(Rol.nombre == "CLIENTE"))
    rol_id = rid.scalar_one()
    await asignar_roles_usuario(user.id, [rol_id], db)
    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="clientes",
        entidad="clientes",
        entidad_id=cliente.id,
        accion=AccionBitacoraEnum.CREAR,
        descripcion=f"Alta manual de cliente: {user.email}",
    )
    return await _cliente_list_read_from_row(cliente, user)


async def update_cliente_admin(
    cliente_id: int,
    data: dict,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
):
    cliente = await _get_cliente_in_tenant(cliente_id, tenant_id, db)
    user = await get_usuario_by_id(cliente.usuario_id, db)

    udata = {}
    for field in ("nombres", "apellidos", "email", "telefono", "estado"):
        if field in data and data[field] is not None:
            udata[field] = data[field]
    if udata:
        user = await update_usuario(cliente.usuario_id, udata, db, ejecutor_id=ejecutor_id)

    if "ciudad" in data and data["ciudad"] is not None:
        cliente.ciudad = data["ciudad"]
    if "direccion" in data and data["direccion"] is not None:
        cliente.direccion = data["direccion"]
    cliente.updated_at = utc_now_naive()

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="clientes",
        entidad="clientes",
        entidad_id=cliente_id,
        accion=AccionBitacoraEnum.ACTUALIZAR,
        descripcion=f"Actualización de cliente {cliente_id}",
    )
    return await _cliente_list_read_from_row(cliente, user)


async def desactivar_cliente_admin(
    cliente_id: int,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
):
    cliente = await _get_cliente_in_tenant(cliente_id, tenant_id, db)
    await delete_usuario(cliente.usuario_id, db, ejecutor_id=ejecutor_id)
    user = await get_usuario_by_id(cliente.usuario_id, db)
    return await _cliente_list_read_from_row(cliente, user)


async def hard_delete_cliente_admin(
    cliente_id: int,
    tenant_id: int | None,
    db: AsyncSession,
    ejecutor_id: int | None = None,
) -> None:
    from sqlalchemy import delete as sql_delete

    from app.modules.clientes_y_vehiculos.vehiculos.models import Vehiculo
    from app.modules.incidentes.emergencias.models import SolicitudEmergencia
    from app.modules.pagos_y_comisiones.pagos.models import Pago
    from app.modules.acceso_y_administracion.roles.models import UsuarioRol
    from app.modules.acceso_y_administracion.auth.models import Sesion

    cliente = await _get_cliente_in_tenant(cliente_id, tenant_id, db)

    sol_count = int(
        (
            await db.execute(
                select(func.count()).select_from(SolicitudEmergencia).where(
                    SolicitudEmergencia.cliente_id == cliente_id
                )
            )
        ).scalar_one()
        or 0
    )
    if sol_count:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el cliente tiene solicitudes de emergencia. Desactívalo en su lugar.",
        )

    pagos_count = int(
        (
            await db.execute(
                select(func.count()).select_from(Pago).where(Pago.cliente_id == cliente_id)
            )
        ).scalar_one()
        or 0
    )
    if pagos_count:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el cliente tiene pagos registrados. Desactívalo en su lugar.",
        )

    veh_count = int(
        (
            await db.execute(
                select(func.count()).select_from(Vehiculo).where(Vehiculo.cliente_id == cliente_id)
            )
        ).scalar_one()
        or 0
    )
    if veh_count:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el cliente tiene vehículos registrados. Desactívalo en su lugar.",
        )

    uid = cliente.usuario_id
    await db.execute(sql_delete(UsuarioRol).where(UsuarioRol.usuario_id == uid))
    await db.execute(sql_delete(Sesion).where(Sesion.usuario_id == uid))
    await db.execute(sql_delete(Cliente).where(Cliente.id == cliente_id))
    await db.execute(sql_delete(Usuario).where(Usuario.id == uid))

    await registrar_accion(
        db=db,
        usuario_id=ejecutor_id,
        modulo="clientes",
        entidad="clientes",
        entidad_id=cliente_id,
        accion=AccionBitacoraEnum.ELIMINAR,
        descripcion=f"Eliminación física de cliente {cliente_id}",
    )
