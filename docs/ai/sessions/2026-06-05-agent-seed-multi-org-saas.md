# Sesión 2026-06-05 — Seed multi-org SaaS (6 organizaciones)

## Objetivo
Ampliar datos demo: 6 organizaciones con planes distintos, cada una con taller, 2 técnicos y 2 clientes (+ vehículos).

## Organizaciones

| Slug | Plan comercial | Taller |
|------|----------------|--------|
| `org-free-equipetrol` | Free | Taller Equipetrol Express |
| `org-free-urbari` | Free | Urbari Mecánica Rápida |
| `org-pro-anillo` | Pro | Auxilio Vial 4to Anillo Pro |
| `org-pro-plan3000` | Pro | Taller Plan 3000 Pro |
| `org-max-centro` | Max | Centro Max Asistencia Vial |
| `org-max-el-torno` | Max | El Torno Max Vial |

## Credenciales (todas)

- **Password:** `scdemo1`
- **Email patrón:** `{local}@{slug}.demo.test`
  - Responsable: `responsable@org-free-equipetrol.demo.test`
  - Técnicos: `tecnico1@…`, `tecnico2@…`
  - Clientes: `cliente1@…`, `cliente2@…`

## Archivos

- `backend/app/seeds/identidades_multi_org.py` — definiciones
- `backend/app/seeds/dev_multi_orgs.py` — `ensure_multi_orgs_seed()`
- `backend/app/seeds/runner.py` — incluido en `python -m app.seeds`
- Flag: `SEED_MULTI_ORGS_ON_START` (activo en `docker-compose.override.yml` dev)

## Cargar

```powershell
docker compose exec backend python -m app.seeds
```

O reiniciar backend con `SEED_MULTI_ORGS_ON_START=true`.
