# Ejecutar desde carpeta backend: python -m app.seeds
# Requiere DATABASE_URL y mismas vars que seed (sin depender de SEED_ADMIN_ON_START).
import logging

from app.seeds.runner import run_startup_seeds_sync

logging.basicConfig(level=logging.INFO)


def main() -> None:
    run_startup_seeds_sync(run_all=True)


if __name__ == "__main__":
    main()
