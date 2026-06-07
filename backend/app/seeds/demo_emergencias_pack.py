# Paquete idempotente de solicitudes demo por taller (bandeja, mis solicitudes, historial, comisiones).
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_now_naive
from app.modules.atencion.taller_emergencias import repository as pt_repo
from app.modules.atencion.taller_emergencias.models import (
    ComisionTaller,
    EstadoAsignacionTecnicoEnum,
    EstadoBandejaTallerEnum,
    EstadoComisionTallerEnum,
    SolicitudTallerBandeja,
)
from app.modules.incidentes.emergencias import repository as em_repo
from app.modules.incidentes.emergencias.models import (
    EstadoSolicitudSeguimientoEnum,
    SolicitudEmergencia,
)
from app.modules.pagos_y_comisiones.pagos.models import EstadoPagoEnum, MetodoPagoEnum, Pago

logger = logging.getLogger(__name__)


async def _count_marker(db: AsyncSession, *, marker: str, taller_id: int) -> int:
    r = await db.execute(
        select(func.count())
        .select_from(SolicitudEmergencia)
        .where(
            SolicitudEmergencia.taller_id == taller_id,
            SolicitudEmergencia.descripcion_texto.like(f"{marker}%"),
        )
    )
    return int(r.scalar_one() or 0)


async def _hist(
    db: AsyncSession,
    *,
    solicitud_id: int,
    ant: EstadoSolicitudSeguimientoEnum | None,
    nuevo: EstadoSolicitudSeguimientoEnum,
    when: datetime,
    usuario_id: int | None,
    obs: str | None,
) -> None:
    await em_repo.insert_historial_estado(
        db,
        solicitud_id=solicitud_id,
        estado_anterior=ant,
        estado_nuevo=nuevo,
        usuario_id=usuario_id,
        observacion=obs,
        created_at=when,
    )


async def _bandeja(
    db: AsyncSession,
    *,
    solicitud_id: int,
    taller_id: int,
    estado: EstadoBandejaTallerEnum,
    creado_at: datetime,
    respondido_at: datetime | None,
) -> None:
    db.add(
        SolicitudTallerBandeja(
            solicitud_id=solicitud_id,
            taller_id=taller_id,
            estado=estado,
            creado_at=creado_at,
            respondido_at=respondido_at,
        )
    )
    await db.flush()


async def _pago_comision(
    db: AsyncSession,
    *,
    solicitud_id: int,
    cliente_id: int,
    taller_id: int,
    monto: Decimal,
    when: datetime,
    ref_suffix: str,
) -> None:
    pct = Decimal("10.00")
    com = (monto * Decimal("0.10")).quantize(Decimal("0.01"))
    neto = (monto - com).quantize(Decimal("0.01"))
    p = Pago(
        solicitud_id=solicitud_id,
        cliente_id=cliente_id,
        monto=monto,
        moneda="BOB",
        metodo=MetodoPagoEnum.QR,
        estado=EstadoPagoEnum.PAGADO,
        referencia_externa=f"DEMO-{ref_suffix}-{solicitud_id}",
        proveedor="SIMULADO",
        metadata_json={"seed": "demo_emergencias_pack"},
        created_at=when,
        pagado_at=when,
    )
    db.add(p)
    await db.flush()
    db.add(
        ComisionTaller(
            solicitud_id=solicitud_id,
            taller_id=taller_id,
            pago_id=p.id,
            porcentaje_plataforma=pct,
            monto_servicio=monto,
            monto_comision=com,
            monto_taller_neto=neto,
            estado=EstadoComisionTallerEnum.CALCULADA,
            calculado_at=when,
            liquidado_at=None,
        )
    )
    await db.flush()


async def seed_emergencias_operativas_taller(
    db: AsyncSession,
    *,
    marker: str,
    tenant_id: int,
    taller_id: int,
    tecnico_id: int,
    cliente_id: int,
    uid_cliente: int,
    uid_resp: int,
    vehiculo_ids: list[int],
    lat: Decimal,
    lng: Decimal,
    min_existing: int = 5,
) -> int:
    """
    Inserta 5 solicitudes demo por taller: bandeja pendiente, en curso, técnico asignado,
    finalizada con comisión e historial. Idempotente por marcador + taller_id.
    """
    if not vehiculo_ids or tecnico_id <= 0:
        return 0
    if await _count_marker(db, marker=marker, taller_id=taller_id) >= min_existing:
        return 0

    now = utc_now_naive()
    v0 = vehiculo_ids[0]
    v1 = vehiculo_ids[min(1, len(vehiculo_ids) - 1)]

    def desc(texto: str) -> str:
        return f"{marker} {texto}"

    inserted = 0

    # 1) Bandeja disponible (PENDIENTE)
    t1 = now - timedelta(days=1)
    s1 = await em_repo.insert_solicitud(
        db,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        vehiculo_id=v0,
        descripcion_texto=desc("Auxilio vial — llanta baja en vía pública (demo bandeja)."),
        estado=EstadoSolicitudSeguimientoEnum.REGISTRADA,
        created_at=t1,
        updated_at=t1,
    )
    await _hist(db, solicitud_id=s1.id, ant=None, nuevo=EstadoSolicitudSeguimientoEnum.REGISTRADA, when=t1, usuario_id=uid_cliente, obs=None)
    await pt_repo.insert_bandeja_pendiente_por_cada_taller(db, solicitud_id=s1.id, creado_at=t1, tenant_id=tenant_id)
    await em_repo.insert_ubicacion(
        db,
        solicitud_id=s1.id,
        latitud=lat,
        longitud=lng,
        precision_metros=Decimal("15"),
        direccion_referencia="Zona demo Santa Cruz",
        es_actual=True,
        registrado_at=t1,
    )
    inserted += 1

    # 2) Mis solicitudes — taller asignado, bandeja aceptada
    t2 = now - timedelta(days=4)
    s2 = await em_repo.insert_solicitud(
        db,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        vehiculo_id=v1,
        descripcion_texto=desc("Batería descargada — taller en curso (demo)."),
        estado=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
        created_at=t2,
        updated_at=t2,
    )
    s2.taller_id = taller_id
    await _hist(db, solicitud_id=s2.id, ant=None, nuevo=EstadoSolicitudSeguimientoEnum.REGISTRADA, when=t2, usuario_id=uid_cliente, obs=None)
    await _hist(
        db,
        solicitud_id=s2.id,
        ant=EstadoSolicitudSeguimientoEnum.REGISTRADA,
        nuevo=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
        when=t2 + timedelta(minutes=20),
        usuario_id=uid_resp,
        obs="Taller aceptó asistencia (demo).",
    )
    await _bandeja(db, solicitud_id=s2.id, taller_id=taller_id, estado=EstadoBandejaTallerEnum.ACEPTADA, creado_at=t2, respondido_at=t2 + timedelta(minutes=20))
    inserted += 1

    # 3) Servicios asignados — técnico asignado
    t3 = now - timedelta(days=7)
    s3 = await em_repo.insert_solicitud(
        db,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        vehiculo_id=v0,
        descripcion_texto=desc("Falla eléctrica — técnico en ruta (demo)."),
        estado=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
        created_at=t3,
        updated_at=t3,
    )
    s3.taller_id = taller_id
    s3.tecnico_id = tecnico_id
    s3.tecnico_asignado_at = t3 + timedelta(minutes=25)
    await _hist(db, solicitud_id=s3.id, ant=None, nuevo=EstadoSolicitudSeguimientoEnum.REGISTRADA, when=t3, usuario_id=uid_cliente, obs=None)
    await _hist(db, solicitud_id=s3.id, ant=EstadoSolicitudSeguimientoEnum.REGISTRADA, nuevo=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO, when=t3 + timedelta(minutes=10), usuario_id=uid_resp, obs=None)
    await _hist(
        db,
        solicitud_id=s3.id,
        ant=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO,
        nuevo=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO,
        when=t3 + timedelta(minutes=25),
        usuario_id=uid_resp,
        obs="Técnico asignado (demo).",
    )
    await _bandeja(db, solicitud_id=s3.id, taller_id=taller_id, estado=EstadoBandejaTallerEnum.ACEPTADA, creado_at=t3, respondido_at=t3 + timedelta(minutes=10))
    await pt_repo.insert_asignacion_tecnico(
        db,
        solicitud_id=s3.id,
        taller_id=taller_id,
        tecnico_id=tecnico_id,
        estado=EstadoAsignacionTecnicoEnum.ASIGNADO,
        asignado_por_usuario_id=uid_resp,
        observacion="Demo seed",
        created_at=t3 + timedelta(minutes=25),
    )
    inserted += 1

    # 4) Historial + comisiones — finalizada
    t4 = now - timedelta(days=15)
    m4 = Decimal("750.00")
    s4 = await em_repo.insert_solicitud(
        db,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        vehiculo_id=v1,
        descripcion_texto=desc("Cambio de aceite y revisión — servicio cerrado (demo)."),
        estado=EstadoSolicitudSeguimientoEnum.FINALIZADA,
        created_at=t4,
        updated_at=t4,
    )
    s4.taller_id = taller_id
    s4.tecnico_id = tecnico_id
    s4.tecnico_asignado_at = t4 + timedelta(minutes=8)
    s4.presupuesto_bob = m4
    s4.presupuesto_registrado_at = t4 + timedelta(hours=1)
    s4.finalizada_at = t4 + timedelta(hours=3)
    await _hist(db, solicitud_id=s4.id, ant=None, nuevo=EstadoSolicitudSeguimientoEnum.REGISTRADA, when=t4, usuario_id=uid_cliente, obs=None)
    await _hist(db, solicitud_id=s4.id, ant=EstadoSolicitudSeguimientoEnum.REGISTRADA, nuevo=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO, when=t4 + timedelta(minutes=5), usuario_id=uid_resp, obs=None)
    await _hist(db, solicitud_id=s4.id, ant=EstadoSolicitudSeguimientoEnum.TALLER_ASIGNADO, nuevo=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO, when=t4 + timedelta(minutes=8), usuario_id=uid_resp, obs=None)
    await _hist(db, solicitud_id=s4.id, ant=EstadoSolicitudSeguimientoEnum.TECNICO_ASIGNADO, nuevo=EstadoSolicitudSeguimientoEnum.FINALIZADA, when=t4 + timedelta(hours=3), usuario_id=uid_resp, obs="Cerrado demo.")
    await _bandeja(db, solicitud_id=s4.id, taller_id=taller_id, estado=EstadoBandejaTallerEnum.ACEPTADA, creado_at=t4, respondido_at=t4 + timedelta(minutes=5))
    await pt_repo.insert_asignacion_tecnico(
        db,
        solicitud_id=s4.id,
        taller_id=taller_id,
        tecnico_id=tecnico_id,
        estado=EstadoAsignacionTecnicoEnum.ASIGNADO,
        asignado_por_usuario_id=uid_resp,
        observacion=None,
        created_at=t4 + timedelta(minutes=8),
    )
    await _pago_comision(
        db,
        solicitud_id=s4.id,
        cliente_id=cliente_id,
        taller_id=taller_id,
        monto=m4,
        when=t4 + timedelta(hours=2),
        ref_suffix=marker.replace("[", "").replace("]", "").replace(" ", "-")[:24],
    )
    inserted += 1

    # 5) Segunda bandeja pendiente
    t5 = now - timedelta(hours=6)
    s5 = await em_repo.insert_solicitud(
        db,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        vehiculo_id=v0,
        descripcion_texto=desc("Pinchazo en avenida — pendiente de respuesta del taller (demo)."),
        estado=EstadoSolicitudSeguimientoEnum.REGISTRADA,
        created_at=t5,
        updated_at=t5,
    )
    await _hist(db, solicitud_id=s5.id, ant=None, nuevo=EstadoSolicitudSeguimientoEnum.REGISTRADA, when=t5, usuario_id=uid_cliente, obs=None)
    await pt_repo.insert_bandeja_pendiente_por_cada_taller(db, solicitud_id=s5.id, creado_at=t5, tenant_id=tenant_id)
    inserted += 1

    logger.info("Demo emergencias: %s solicitudes para taller_id=%s (%s).", inserted, taller_id, marker)
    return inserted
