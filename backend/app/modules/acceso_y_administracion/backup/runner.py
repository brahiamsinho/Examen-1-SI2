"""CLI para el contenedor backup-scheduler (equivalente a manage.py backup_automatico)."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

import app.db_metadata  # noqa: F401 — registra todos los modelos ORM antes de usar la sesión

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.modules.acceso_y_administracion.backup import service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _main(force: bool) -> int:
    if not settings.BACKUP_ENABLED:
        logger.info("BACKUP_ENABLED=false — omitiendo ciclo.")
        return 0

    async with AsyncSessionLocal() as db:
        try:
            ok, err = await service.run_automatic_backups(db, force=force)
            await db.commit()
            logger.info("Backup automático: %s ok, %s errores", ok, err)
            return 0 if err == 0 else 1
        except Exception as exc:
            await db.rollback()
            logger.exception("Backup automático abortado: %s", exc)
            return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Backups automáticos EmergenciasViales")
    parser.add_argument("--force", action="store_true", help="Ignorar hora/frecuencia configurada")
    args = parser.parse_args()
    code = asyncio.run(_main(force=args.force))
    sys.exit(code)


if __name__ == "__main__":
    main()
