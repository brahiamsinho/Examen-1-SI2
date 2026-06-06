# Sesión — Limpieza `.env` (2026-06-05)

## Objetivo
Eliminar duplicados y alinear variables con Docker dev + seeds multi-org.

## Cambios
- `.env`: `RUN_SEEDS_IN_LIFESPAN=false`, `SEED_MULTI_ORGS_*`, Stripe/Gemini/IA sin duplicar.
- `.gitignore`: `.env` activo en ambos bloques.

## Nota
Si `.env` estuvo alguna vez en Git, rotar `GEMINI_API_KEY` y claves Stripe test.
