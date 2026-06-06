# Sesión 2026-06-04 — Técnicos por taller + credenciales demo

## Objetivo
Completar la red demo con **1 técnico móvil por cada taller/sucursal** y documentar todas las credenciales.

## Cambios backend
- `talleres_red_seed.py`: `TALLER2` en `DEMO_SC_EXTRA_TALLERES`; técnicos idempotentes por responsable.
- `identidades_demo_sc.py`: coords `TALLER2_LAT/LNG`.
- `dev_talleres_red.py`: `min_count=6` para demo-sc.
- `dev_multi_orgs.py`: `ensure_tecnicos_red_for_extra_defs` tras sucursales.

## Documentación
- `docs/CREDENCIALES_DEMO.md`: matriz demo-sc (6 filas) + detalle multi-org (6 orgs × sucursales + técnicos).

## Verificación
```powershell
docker compose exec backend python -m app.seeds
docker compose exec db psql -U emergencias_user -d emergencias_db -c "SELECT t.nombre_comercial, COUNT(te.id) FROM talleres t JOIN tenants tn ON tn.id=t.tenant_id LEFT JOIN tecnicos te ON te.taller_id=t.id WHERE tn.slug='demo-sc' AND t.estado='ACTIVO' GROUP BY t.id, t.nombre_comercial;"
```
Resultado esperado: **6 talleres**, **1 técnico** cada uno en demo-sc.
