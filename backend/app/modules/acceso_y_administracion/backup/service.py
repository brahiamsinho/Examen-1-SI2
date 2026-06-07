"""Servicio de backup/restore — pg_dump (plataforma) y export CSV por tenant."""
from __future__ import annotations

import csv
import gzip
import io
import json
import logging
import os
import subprocess
import tarfile
from datetime import datetime, timedelta, time
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutil import utc_now_naive
from app.modules.acceso_y_administracion.backup.models import (
    BackupConfig,
    BackupRegistro,
    EstadoBackupEnum,
    TallerBackupConfig,
    TipoBackupEnum,
)
from app.modules.acceso_y_administracion.bitacora.models import AccionBitacoraEnum
from app.modules.acceso_y_administracion.bitacora.service import registrar_accion
from app.modules.acceso_y_administracion.tenants.models import Tenant
from app.modules.talleres_y_tecnicos.talleres.models import Taller

logger = logging.getLogger(__name__)

# Tablas con filtro directo o indirecto por tenant (shared schema, no django-tenants).
TENANT_EXPORT_TABLES: list[tuple[str, str]] = [
    ("tenants", "id = {tid}"),
    ("usuarios", "tenant_id = {tid}"),
    ("talleres", "tenant_id = {tid}"),
    ("clientes", "tenant_id = {tid}"),
    ("vehiculos", "tenant_id = {tid}"),
    ("solicitudes_emergencia", "tenant_id = {tid}"),
    ("tecnicos", "taller_id IN (SELECT id FROM talleres WHERE tenant_id = {tid})"),
    (
        "solicitud_taller_bandeja",
        "taller_id IN (SELECT id FROM talleres WHERE tenant_id = {tid})",
    ),
    (
        "comisiones_taller",
        "taller_id IN (SELECT id FROM talleres WHERE tenant_id = {tid})",
    ),
]

TALLER_EXPORT_TABLES: list[tuple[str, str]] = [
    ("talleres", "id = {tid}"),
    ("taller_disponibilidad", "taller_id = {tid}"),
    # Cuentas de login de técnicos (necesarias para restaurar tecnicos tras hard-delete).
    (
        "usuarios",
        "id IN (SELECT usuario_id FROM tecnicos WHERE taller_id = {tid})",
    ),
    (
        "usuario_rol",
        "usuario_id IN (SELECT usuario_id FROM tecnicos WHERE taller_id = {tid})",
    ),
    ("tecnicos", "taller_id = {tid}"),
    ("solicitud_taller_bandeja", "taller_id = {tid}"),
    (
        "solicitud_asignaciones_tecnico",
        "taller_id = {tid}",
    ),
    ("comisiones_taller", "taller_id = {tid}"),
    (
        "solicitudes_emergencia",
        "id IN (SELECT solicitud_id FROM solicitud_taller_bandeja WHERE taller_id = {tid})",
    ),
]

TALLER_RESTORE_INSERT_ORDER = [
    "taller_disponibilidad",
    "tecnicos",
    "solicitudes_emergencia",
    "solicitud_taller_bandeja",
    "solicitud_asignaciones_tecnico",
    "comisiones_taller",
]

# Columnas del taller que se restauran con UPDATE (el registro base siempre existe).
TALLER_RESTORE_UPDATE_COLUMNS = (
    "nombre_comercial",
    "telefono_contacto",
    "email_contacto",
    "direccion",
    "ciudad",
    "latitud",
    "longitud",
    "descripcion",
    "estado",
)


def _app_now() -> datetime:
    """Hora local del contenedor (TZ en docker-compose, ej. America/La_Paz) para backups a las 03:00."""
    tz_name = os.environ.get("TZ", "UTC")
    try:
        return datetime.now(ZoneInfo(tz_name)).replace(tzinfo=None)
    except Exception:
        return utc_now_naive()


def _parse_database_url() -> dict[str, str]:
    raw = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(raw)
    return {
        "PGHOST": parsed.hostname or "localhost",
        "PGPORT": str(parsed.port or 5432),
        "PGUSER": unquote(parsed.username or ""),
        "PGPASSWORD": unquote(parsed.password or ""),
        "PGDATABASE": (parsed.path or "/").lstrip("/"),
    }


def _pg_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(_parse_database_url())
    return env


def _storage_root() -> Path:
    root = settings.backup_storage_path
    root.mkdir(parents=True, exist_ok=True)
    return root


def _relative_path(full: Path) -> str:
    root = _storage_root()
    try:
        return str(full.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(full)


def _resolve_file(relative: str) -> Path:
    root = _storage_root().resolve()
    target = (root / relative).resolve()
    if not str(target).startswith(str(root)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de backup inválida.")
    return target


def _run_cmd(cmd: list[str], *, input_text: str | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    timeout = timeout or settings.BACKUP_TIMEOUT_SECONDS
    return subprocess.run(
        cmd,
        env=_pg_env(),
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _exec_sql(sql: str) -> None:
    proc = _run_cmd(["psql", "-v", "ON_ERROR_STOP=1", "-c", sql])
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "psql failed").strip()
        raise RuntimeError(err)


def _copy_csv_into_table(table: str, csv_text: str) -> None:
    proc = _run_cmd(
        ["psql", "-v", "ON_ERROR_STOP=1", "-c", f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)"],
        input_text=csv_text,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or f"COPY {table} failed").strip()
        raise RuntimeError(err)


def _query_id_set(sql: str) -> set[int]:
    proc = _run_cmd(["psql", "-t", "-A", "-c", sql])
    if proc.returncode != 0:
        return set()
    return {int(line.strip()) for line in (proc.stdout or "").splitlines() if line.strip().isdigit()}


def _csv_has_data_rows(csv_text: str) -> bool:
    reader = csv.DictReader(io.StringIO(csv_text))
    return next(reader, None) is not None


def _filter_csv_rows(csv_text: str, *, keep_row) -> tuple[str, int]:
    """Filtra filas de un CSV; devuelve (csv_filtrado, filas_omitidas)."""
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        return csv_text, 0
    fieldnames = reader.fieldnames
    kept: list[dict[str, str]] = []
    skipped = 0
    for row in reader:
        if keep_row(row):
            kept.append(row)
        else:
            skipped += 1
    if skipped == 0:
        return csv_text, 0
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(kept)
    return output.getvalue(), skipped


def _restore_taller_staff_from_csv(
    usuarios_csv: str | None,
    usuario_rol_csv: str | None,
    *,
    taller_id: int,
) -> None:
    """Recrea cuentas de técnicos antes de insertar filas en tecnicos."""
    if not usuarios_csv or not usuarios_csv.strip() or not _csv_has_data_rows(usuarios_csv):
        return

    user_ids: list[int] = []
    for row in csv.DictReader(io.StringIO(usuarios_csv)):
        uid = (row.get("id") or "").strip()
        if uid.isdigit():
            user_ids.append(int(uid))
    if not user_ids:
        return

    responsable_rows = _query_id_set(f"SELECT usuario_responsable_id FROM talleres WHERE id = {taller_id}")
    responsable_id = next(iter(responsable_rows), None)
    safe_ids = [uid for uid in user_ids if uid != responsable_id]
    if not safe_ids:
        return

    ids_sql = ",".join(str(uid) for uid in safe_ids)
    _exec_sql(f"DELETE FROM sesiones WHERE usuario_id IN ({ids_sql})")
    _exec_sql(f"DELETE FROM usuario_rol WHERE usuario_id IN ({ids_sql})")
    _exec_sql(f"DELETE FROM usuarios WHERE id IN ({ids_sql})")
    _copy_csv_into_table("usuarios", usuarios_csv)

    if usuario_rol_csv and usuario_rol_csv.strip() and _csv_has_data_rows(usuario_rol_csv):
        _copy_csv_into_table("usuario_rol", usuario_rol_csv)


def _restore_table_from_csv(table: str, csv_text: str, *, taller_id: int) -> None:
    if table == "tecnicos":
        existing_users = _query_id_set("SELECT id FROM usuarios")
        csv_text, skipped = _filter_csv_rows(
            csv_text,
            keep_row=lambda row: (row.get("usuario_id") or "").strip().isdigit()
            and int(row["usuario_id"]) in existing_users,
        )
        if skipped:
            logger.warning(
                "Restore taller %s: omitidos %s técnicos sin cuenta de usuario (backup antiguo sin usuarios.csv)",
                taller_id,
                skipped,
            )
    elif table == "solicitud_asignaciones_tecnico":
        existing_tecnicos = _query_id_set(f"SELECT id FROM tecnicos WHERE taller_id = {taller_id}")
        csv_text, skipped = _filter_csv_rows(
            csv_text,
            keep_row=lambda row: (row.get("tecnico_id") or "").strip().isdigit()
            and int(row["tecnico_id"]) in existing_tecnicos,
        )
        if skipped:
            logger.warning(
                "Restore taller %s: omitidas %s asignaciones con técnico inexistente",
                taller_id,
                skipped,
            )

    if not _csv_has_data_rows(csv_text):
        return
    _copy_csv_into_table(table, csv_text)


def _sql_literal(value: str | None) -> str:
    if value is None or value == "":
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def _restore_taller_row_from_csv(csv_text: str, *, taller_id: int) -> None:
    """Actualiza la fila del taller existente; no hace INSERT (evita talleres_pkey)."""
    reader = csv.DictReader(io.StringIO(csv_text))
    row = next(reader, None)
    if not row:
        return
    if str(row.get("id", "")).strip() != str(taller_id):
        raise RuntimeError("El CSV del taller no corresponde a este taller.")

    assignments: list[str] = []
    for column in TALLER_RESTORE_UPDATE_COLUMNS:
        if column not in row:
            continue
        raw = (row[column] or "").strip()
        if column in {"latitud", "longitud"} and not raw:
            assignments.append(f"{column} = NULL")
        else:
            assignments.append(f"{column} = {_sql_literal(raw or None)}")
    assignments.append("updated_at = NOW()")

    sql = f"UPDATE talleres SET {', '.join(assignments)} WHERE id = {taller_id}"
    _exec_sql(sql)


def _create_taller_export(taller: Taller) -> tuple[str, float]:
    """Export lógico de un taller (CSV en tar.gz) — panel responsable."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = f"taller-{taller.id}"
    rel = f"talleres/{taller.id}/{timestamp}_{slug}.tar.gz"
    target = _storage_root() / rel
    target.parent.mkdir(parents=True, exist_ok=True)

    tid = taller.id
    manifest = {
        "format": "taller-csv-v1",
        "taller_id": tid,
        "tenant_id": taller.tenant_id,
        "taller_nombre": taller.nombre_comercial,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tables": [t[0] for t in TALLER_EXPORT_TABLES],
    }

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, io.BytesIO(manifest_bytes))

        for table, where_tpl in TALLER_EXPORT_TABLES:
            where = where_tpl.format(tid=tid)
            try:
                csv_data = _export_table_csv(table, where)
            except RuntimeError as exc:
                logger.warning("Omitiendo tabla %s en export taller %s: %s", table, tid, exc)
                continue
            if not csv_data.strip():
                continue
            info = tarfile.TarInfo(name=f"{table}.csv")
            info.size = len(csv_data)
            tar.addfile(info, io.BytesIO(csv_data))

    data = buf.getvalue()
    size_mb = len(data) / (1024 * 1024)
    if size_mb > settings.BACKUP_MAX_SIZE_MB:
        raise RuntimeError(f"Export taller demasiado grande: {size_mb:.2f} MB")

    target.write_bytes(data)
    return rel, round(size_mb, 2)


def _restore_taller_export(relative_path: str, *, taller_id: int, tenant_id: int) -> None:
    path = _resolve_file(relative_path)
    if not path.is_file():
        raise RuntimeError("Archivo de backup no encontrado")

    table_csv: dict[str, str] = {}
    manifest: dict | None = None
    with tarfile.open(path, mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            raw = tar.extractfile(member)
            if raw is None:
                continue
            content = raw.read().decode("utf-8")
            if member.name == "manifest.json":
                manifest = json.loads(content)
            elif member.name.endswith(".csv"):
                table_csv[member.name.replace(".csv", "")] = content

    if not manifest or manifest.get("format") != "taller-csv-v1":
        raise RuntimeError("Manifest inválido o formato no soportado.")
    if int(manifest.get("taller_id", 0)) != taller_id:
        raise RuntimeError("El backup no corresponde a este taller.")

    solicitud_ids: list[int] = []
    bandeja_csv = table_csv.get("solicitud_taller_bandeja")
    if bandeja_csv:
        lines = bandeja_csv.strip().splitlines()
        if len(lines) > 1:
            header = lines[0].split(",")
            try:
                idx = header.index("solicitud_id")
            except ValueError:
                idx = None
            if idx is not None:
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) > idx and parts[idx].isdigit():
                        solicitud_ids.append(int(parts[idx]))

    _exec_sql(f"DELETE FROM comisiones_taller WHERE taller_id = {taller_id}")
    _exec_sql(f"DELETE FROM solicitud_asignaciones_tecnico WHERE taller_id = {taller_id}")
    _exec_sql(f"DELETE FROM solicitud_taller_bandeja WHERE taller_id = {taller_id}")
    if solicitud_ids:
        ids_sql = ",".join(str(i) for i in solicitud_ids)
        _exec_sql(
            f"DELETE FROM solicitudes_emergencia WHERE tenant_id = {tenant_id} AND id IN ({ids_sql})"
        )
    _exec_sql(f"DELETE FROM taller_disponibilidad WHERE taller_id = {taller_id}")
    _exec_sql(f"DELETE FROM tecnicos WHERE taller_id = {taller_id}")

    taller_csv = table_csv.get("talleres")
    if taller_csv and taller_csv.strip():
        _restore_taller_row_from_csv(taller_csv, taller_id=taller_id)

    _restore_taller_staff_from_csv(
        table_csv.get("usuarios"),
        table_csv.get("usuario_rol"),
        taller_id=taller_id,
    )

    for table in TALLER_RESTORE_INSERT_ORDER:
        csv_text = table_csv.get(table)
        if not csv_text or not csv_text.strip():
            continue
        _restore_table_from_csv(table, csv_text, taller_id=taller_id)


def _create_platform_dump() -> tuple[str, float]:
    """pg_dump completo de la BD (adaptación de Oftalmologia schema-dump → plataforma shared schema)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel = f"plataforma/{timestamp}_plataforma.sql.gz"
    target = _storage_root() / rel
    target.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pg_dump",
        "--no-owner",
        "--no-privileges",
        "--clean",
        "--if-exists",
    ]
    proc = _run_cmd(cmd)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "pg_dump failed").strip()
        raise RuntimeError(err)

    compressed = gzip.compress(proc.stdout.encode("utf-8"))
    max_mb = settings.BACKUP_MAX_SIZE_MB
    size_mb = len(compressed) / (1024 * 1024)
    if size_mb > max_mb:
        raise RuntimeError(f"Backup demasiado grande: {size_mb:.2f} MB (máx {max_mb} MB)")

    target.write_bytes(compressed)
    return rel, round(size_mb, 2)


def _export_table_csv(table: str, where_sql: str) -> bytes:
    sql = f"COPY (SELECT * FROM {table} WHERE {where_sql}) TO STDOUT WITH (FORMAT csv, HEADER true)"
    proc = _run_cmd(["psql", "-c", sql])
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or f"export {table} failed").strip()
        raise RuntimeError(f"Export {table}: {err}")
    return proc.stdout.encode("utf-8")


def _create_tenant_export(tenant: Tenant) -> tuple[str, float]:
    """Export lógico por tenant_id (CSV en tar.gz) — shared schema vs schema-per-tenant en Oftalmologia."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = tenant.slug or f"tenant-{tenant.id}"
    rel = f"tenants/{tenant.id}/{timestamp}_{slug}.tar.gz"
    target = _storage_root() / rel
    target.parent.mkdir(parents=True, exist_ok=True)

    tid = tenant.id
    manifest = {
        "tenant_id": tid,
        "tenant_slug": slug,
        "tenant_nombre": tenant.nombre,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "format": "csv-v1",
        "tables": [t[0] for t in TENANT_EXPORT_TABLES],
    }

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, io.BytesIO(manifest_bytes))

        for table, where_tpl in TENANT_EXPORT_TABLES:
            where = where_tpl.format(tid=tid)
            try:
                csv_data = _export_table_csv(table, where)
            except RuntimeError as exc:
                logger.warning("Omitiendo tabla %s en export tenant %s: %s", table, tid, exc)
                continue
            if not csv_data.strip():
                continue
            info = tarfile.TarInfo(name=f"{table}.csv")
            info.size = len(csv_data)
            tar.addfile(info, io.BytesIO(csv_data))

    data = buf.getvalue()
    size_mb = len(data) / (1024 * 1024)
    if size_mb > settings.BACKUP_MAX_SIZE_MB:
        raise RuntimeError(f"Export tenant demasiado grande: {size_mb:.2f} MB")

    target.write_bytes(data)
    return rel, round(size_mb, 2)


def _create_evidencias_archive() -> tuple[str, float]:
    src = settings.evidencias_upload_dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel = f"evidencias/{timestamp}_evidencias.tar.gz"
    target = _storage_root() / rel
    target.parent.mkdir(parents=True, exist_ok=True)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        if src.is_dir():
            for path in src.rglob("*"):
                if path.is_file():
                    arc = path.relative_to(src.parent).as_posix()
                    tar.add(path, arcname=arc)
        else:
            info = tarfile.TarInfo(name="README.txt")
            msg = b"No hay directorio de evidencias.\n"
            info.size = len(msg)
            tar.addfile(info, io.BytesIO(msg))

    data = buf.getvalue()
    size_mb = len(data) / (1024 * 1024)
    target.write_bytes(data)
    return rel, round(size_mb, 2)


def _restore_platform_dump(relative_path: str) -> None:
    path = _resolve_file(relative_path)
    if not path.is_file():
        raise RuntimeError("Archivo de backup no encontrado")

    raw = gzip.decompress(path.read_bytes()).decode("utf-8")
    proc = _run_cmd(["psql", "-v", "ON_ERROR_STOP=1"], input_text=raw)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "psql restore failed").strip()
        raise RuntimeError(err)


async def get_or_create_config(db: AsyncSession) -> BackupConfig:
    r = await db.execute(select(BackupConfig).order_by(BackupConfig.id).limit(1))
    cfg = r.scalar_one_or_none()
    if cfg:
        return cfg
    now = utc_now_naive()
    cfg = BackupConfig(
        backup_automatico=True,
        hora_backup=time(3, 0),
        frecuencia="daily",
        retencion_dias=settings.BACKUP_RETENTION_DAYS_DEFAULT,
        incluir_evidencias=True,
        actualizado_en=now,
    )
    db.add(cfg)
    await db.flush()
    return cfg


async def get_or_create_taller_config(db: AsyncSession, taller_id: int) -> TallerBackupConfig:
    r = await db.execute(select(TallerBackupConfig).where(TallerBackupConfig.taller_id == taller_id))
    cfg = r.scalar_one_or_none()
    if cfg:
        return cfg
    now = _app_now()
    cfg = TallerBackupConfig(
        taller_id=taller_id,
        backup_automatico=True,
        hora_backup=time(3, 0),
        frecuencia="daily",
        retencion_dias=min(7, settings.BACKUP_RETENTION_DAYS_DEFAULT),
        ultimo_backup_auto=None,
        actualizado_en=now,
    )
    db.add(cfg)
    await db.flush()
    return cfg


async def list_backups(
    db: AsyncSession,
    *,
    tenant_id: int | None = None,
    taller_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[BackupRegistro]:
    stmt = select(BackupRegistro).order_by(BackupRegistro.creado_en.desc()).limit(limit).offset(offset)
    if tenant_id is not None:
        stmt = stmt.where(BackupRegistro.tenant_id == tenant_id)
    if taller_id is not None:
        stmt = stmt.where(BackupRegistro.taller_id == taller_id)
    return list((await db.execute(stmt)).scalars().all())


async def get_backup(db: AsyncSession, backup_id: int) -> BackupRegistro:
    r = await db.execute(select(BackupRegistro).where(BackupRegistro.id == backup_id))
    row = r.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup no encontrado.")
    return row


async def _assert_no_operation_in_progress(db: AsyncSession) -> None:
    r = await db.execute(
        select(BackupRegistro.id).where(BackupRegistro.estado == EstadoBackupEnum.EN_PROGRESO).limit(1)
    )
    if r.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay una operación de backup en progreso.",
        )


async def get_backup_for_taller(db: AsyncSession, backup_id: int, taller_id: int) -> BackupRegistro:
    reg = await get_backup(db, backup_id)
    if reg.taller_id != taller_id or reg.tipo != TipoBackupEnum.TALLER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup no encontrado.")
    return reg


async def create_backup(
    db: AsyncSession,
    *,
    tipo: TipoBackupEnum,
    usuario_id: int | None,
    tenant_id: int | None = None,
    taller_id: int | None = None,
    incluir_evidencias: bool = False,
) -> BackupRegistro:
    await _assert_no_operation_in_progress(db)

    tenant: Tenant | None = None
    taller: Taller | None = None

    if tipo == TipoBackupEnum.TALLER:
        if taller_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="taller_id es obligatorio para backup TALLER.",
            )
        tr = await db.execute(select(Taller).where(Taller.id == taller_id))
        taller = tr.scalar_one_or_none()
        if not taller:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taller no encontrado.")
        tenant_id = taller.tenant_id
        cfg = await get_or_create_taller_config(db, taller_id)
        expira = _app_now() + timedelta(days=cfg.retencion_dias)
    elif tipo == TipoBackupEnum.TENANT:
        cfg = await get_or_create_config(db)
        expira = _app_now() + timedelta(days=cfg.retencion_dias)
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tenant_id es obligatorio para backup TENANT.",
            )
        tr = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tr.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant no encontrado.")
    else:
        cfg = await get_or_create_config(db)
        expira = _app_now() + timedelta(days=cfg.retencion_dias)

    reg = BackupRegistro(
        tenant_id=tenant_id if tipo in (TipoBackupEnum.TENANT, TipoBackupEnum.TALLER) else None,
        taller_id=taller_id if tipo == TipoBackupEnum.TALLER else None,
        tipo=tipo,
        archivo="",
        tamano_mb=None,
        estado=EstadoBackupEnum.EN_PROGRESO,
        incluye_evidencias=incluir_evidencias,
        creado_en=_app_now(),
        expira_en=expira,
        creado_por_usuario_id=usuario_id,
    )
    db.add(reg)
    await db.flush()

    try:
        if tipo == TipoBackupEnum.PLATAFORMA:
            rel, size = _create_platform_dump()
        elif tipo == TipoBackupEnum.TENANT:
            assert tenant is not None
            rel, size = _create_tenant_export(tenant)
        elif tipo == TipoBackupEnum.TALLER:
            assert taller is not None
            rel, size = _create_taller_export(taller)
        elif tipo == TipoBackupEnum.EVIDENCIAS:
            rel, size = _create_evidencias_archive()
        else:
            raise RuntimeError(f"Tipo no soportado: {tipo}")

        reg.archivo = rel
        reg.tamano_mb = size
        reg.estado = EstadoBackupEnum.COMPLETADO

        if incluir_evidencias and tipo == TipoBackupEnum.PLATAFORMA:
            ev_rel, ev_size = _create_evidencias_archive()
            ev_reg = BackupRegistro(
                tenant_id=None,
                tipo=TipoBackupEnum.EVIDENCIAS,
                archivo=ev_rel,
                tamano_mb=ev_size,
                estado=EstadoBackupEnum.COMPLETADO,
                incluye_evidencias=True,
                creado_en=utc_now_naive(),
                expira_en=expira,
                creado_por_usuario_id=usuario_id,
            )
            db.add(ev_reg)

        await registrar_accion(
            db,
            modulo="backup",
            entidad="backups",
            accion=AccionBitacoraEnum.CREAR,
            descripcion=f"Backup {tipo.value} completado ({size} MB)",
            usuario_id=usuario_id,
            entidad_id=reg.id,
        )
    except Exception as exc:
        reg.estado = EstadoBackupEnum.FALLIDO
        reg.error_mensaje = str(exc)[:2000]
        await registrar_accion(
            db,
            modulo="backup",
            entidad="backups",
            accion=AccionBitacoraEnum.CREAR,
            descripcion=f"Backup {tipo.value} fallido: {exc}",
            usuario_id=usuario_id,
            entidad_id=reg.id,
        )
        logger.exception("Backup fallido id=%s", reg.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando backup: {exc}",
        ) from exc

    return reg


async def restore_backup(
    db: AsyncSession,
    backup_id: int,
    *,
    usuario_id: int,
    motivo: str,
    taller_id: int | None = None,
    tenant_id: int | None = None,
) -> BackupRegistro:
    reg = await get_backup(db, backup_id)
    if taller_id is not None:
        if reg.taller_id != taller_id or reg.tipo != TipoBackupEnum.TALLER:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup no encontrado.")
    if reg.tipo not in (TipoBackupEnum.PLATAFORMA, TipoBackupEnum.TALLER):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede restaurar backup PLATAFORMA o TALLER.",
        )
    if reg.estado not in (EstadoBackupEnum.COMPLETADO, EstadoBackupEnum.RESTAURADO):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden restaurar backups completados.",
        )

    await _assert_no_operation_in_progress(db)
    reg.estado = EstadoBackupEnum.EN_PROGRESO
    await db.flush()

    try:
        if reg.tipo == TipoBackupEnum.PLATAFORMA:
            _restore_platform_dump(reg.archivo)
        else:
            assert reg.taller_id is not None
            tid = tenant_id or reg.tenant_id
            if tid is None:
                tr = await db.execute(select(Taller).where(Taller.id == reg.taller_id))
                trow = tr.scalar_one_or_none()
                tid = trow.tenant_id if trow else None
            if tid is None:
                raise RuntimeError("No se pudo determinar tenant_id para restore.")
            _restore_taller_export(reg.archivo, taller_id=reg.taller_id, tenant_id=tid)

        reg.estado = EstadoBackupEnum.RESTAURADO
        reg.restaurado_en = _app_now()
        reg.restaurado_por_usuario_id = usuario_id
        reg.motivo_restore = motivo
        await registrar_accion(
            db,
            modulo="backup",
            entidad="backups",
            accion=AccionBitacoraEnum.ACTUALIZAR,
            descripcion=f"Restore {reg.tipo.value} backup_id={reg.id}. Motivo: {motivo}",
            usuario_id=usuario_id,
            entidad_id=reg.id,
        )
    except Exception as exc:
        reg.estado = EstadoBackupEnum.FALLIDO
        reg.error_mensaje = str(exc)[:2000]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restaurando backup: {exc}",
        ) from exc

    return reg


async def delete_backup(db: AsyncSession, backup_id: int, *, usuario_id: int | None) -> None:
    reg = await get_backup(db, backup_id)
    try:
        path = _resolve_file(reg.archivo)
        if path.is_file():
            path.unlink()
    except OSError as exc:
        logger.warning("No se pudo borrar archivo %s: %s", reg.archivo, exc)

    await registrar_accion(
        db,
        modulo="backup",
        entidad="backups",
        accion=AccionBitacoraEnum.ELIMINAR,
        descripcion=f"Backup eliminado id={reg.id}",
        usuario_id=usuario_id,
        entidad_id=reg.id,
    )
    await db.delete(reg)


def read_backup_bytes(relative: str) -> tuple[bytes, str, str]:
    path = _resolve_file(relative)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
    name = path.name
    if name.endswith(".sql.gz"):
        media = "application/gzip"
    elif name.endswith(".tar.gz"):
        media = "application/gzip"
    else:
        media = "application/octet-stream"
    return path.read_bytes(), name, media


async def cleanup_expired(db: AsyncSession) -> int:
    now = utc_now_naive()
    r = await db.execute(
        select(BackupRegistro).where(
            BackupRegistro.expira_en.is_not(None),
            BackupRegistro.expira_en < now,
            BackupRegistro.estado.in_(
                [EstadoBackupEnum.COMPLETADO, EstadoBackupEnum.RESTAURADO]
            ),
        )
    )
    rows = list(r.scalars().all())
    count = 0
    for reg in rows:
        try:
            path = _resolve_file(reg.archivo)
            if path.is_file():
                path.unlink()
        except (HTTPException, OSError):
            pass
        reg.estado = EstadoBackupEnum.EXPIRADO
        count += 1
    return count


def _already_ran_today(cfg: TallerBackupConfig, now: datetime) -> bool:
    if cfg.ultimo_backup_auto is None:
        return False
    return cfg.ultimo_backup_auto.date() == now.date()


def _should_run_automatic(now: datetime, cfg: BackupConfig | TallerBackupConfig, *, force: bool) -> bool:
    if not cfg.backup_automatico:
        return False
    if force:
        return True
    hora = cfg.hora_backup
    if isinstance(hora, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                hora = datetime.strptime(hora.strip(), fmt).time()
                break
            except ValueError:
                continue
        else:
            hora = time(3, 0)
    current = now.time().replace(second=0, microsecond=0)
    target = hora.replace(second=0, microsecond=0)
    diff = abs((current.hour * 60 + current.minute) - (target.hour * 60 + target.minute))
    if diff > 1:
        return False
    if cfg.frecuencia == "weekly" and now.weekday() != 6:
        return False
    return True


async def run_automatic_backups(db: AsyncSession, *, force: bool = False) -> tuple[int, int]:
    """Backups automáticos plataforma + cada taller con config activa (hora local TZ, ej. 03:00)."""
    now = _app_now()
    ok = 0
    err = 0

    cfg = await get_or_create_config(db)
    if _should_run_automatic(now, cfg, force=force):
        try:
            await create_backup(
                db,
                tipo=TipoBackupEnum.PLATAFORMA,
                usuario_id=None,
                incluir_evidencias=cfg.incluir_evidencias,
            )
            ok += 1
        except HTTPException:
            err += 1
        except Exception as exc:
            logger.error("Backup automático plataforma falló: %s", exc)
            err += 1

    tr = await db.execute(
        select(TallerBackupConfig).where(TallerBackupConfig.backup_automatico.is_(True))
    )
    for tcfg in tr.scalars().all():
        if not _should_run_automatic(now, tcfg, force=force):
            continue
        if not force and _already_ran_today(tcfg, now):
            continue
        try:
            await create_backup(
                db,
                tipo=TipoBackupEnum.TALLER,
                taller_id=tcfg.taller_id,
                usuario_id=None,
            )
            tcfg.ultimo_backup_auto = now
            tcfg.actualizado_en = now
            ok += 1
        except HTTPException:
            err += 1
        except Exception as exc:
            logger.error("Backup automático taller %s falló: %s", tcfg.taller_id, exc)
            err += 1

    cleaned = await cleanup_expired(db)
    if cleaned:
        logger.info("Backups expirados marcados: %s", cleaned)
    return ok, err
