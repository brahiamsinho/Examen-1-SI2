# Sesión 2026-06-04 — Red talleres + horarios por tenant

## Objetivo
- Mínimo **5 talleres ACTIVO** por organización/tenant (red de talleres).
- **Horarios de atención** configurables por taller (ej. 08:00–18:00); fuera de horario no se recomienda ni acepta emergencias.

## Backend
- Migración `0026_taller_horarios.sql` — tabla `taller_horarios` (día 0=lunes … 6=domingo, franja TIME, `activo`).
- Modelo `TallerHorario` + `horarios_service.py` (zona `America/La_Paz`, default Lun–Sáb 08–18, Dom cerrado).
- API portal: `GET/PUT /api/app/taller/horarios` (permiso `disponibilidad:gestionar`).
- Integración: ranking IA6 (`abierto_ahora`), CU37 selección, CU26 aceptar bandeja.
- Seeds: `talleres_red_seed.py`, `dev_talleres_red.py`, flag `SEED_TALLERES_RED_ON_START`; multi-org +4 sucursales/org; demo-sc +4 talleres extra (identidades TALLER3–6).

## Frontend web
- `/taller/panel/horarios` — grid semanal editable.

## Mobile cliente
- Badge **Cerrado** en selección de taller; confirmación deshabilitada fuera de horario.

## Cómo probar
```bash
docker compose exec backend python -m app.seeds  # run_all
# Portal taller → Horarios
# Mobile cliente → elegir taller (ver cerrados fuera de franja)
```

## Credenciales nuevas demo-sc (password `scdemo1`)
- `sandra.miranda@sc-demo.test`, `felipe.guzman@sc-demo.test`, `elena.cortez@sc-demo.test`, `pablo.ramos@sc-demo.test`
