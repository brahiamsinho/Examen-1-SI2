# Credenciales de desarrollo — EmergenciasViales

> **Solo entorno local / demo.** Contraseñas cortas a propósito (`scdemo1`).  
> **No uses estos valores en producción.**  
> Secretos de terceros (Gemini, Stripe secret) viven en `.env` (gitignored). Este archivo documenta cuentas demo e infra.

**Última revisión:** 2026-06-04 · Fuente: `identidades_demo_sc.py`, `identidades_multi_org.py`, `talleres_red_seed.py`

---

## Contraseña común (cuentas seed)

| Variable | Valor |
|----------|--------|
| Todas las cuentas demo | `scdemo1` |
| `SEED_*_PASSWORD` / `SEED_MULTI_ORGS_PASSWORD` | `scdemo1` |

---

## URLs de acceso (Docker local)

| Servicio | URL |
|----------|-----|
| Frontend (Angular/nginx) | http://localhost |
| API backend | http://localhost:8000 |
| Swagger / OpenAPI | http://localhost:8000/docs |
| Admin panel | http://localhost/admin/login |
| Portal taller | http://localhost/taller |
| Registro taller | http://localhost/taller/registro |
| Mailpit (correo dev) | http://localhost:8025 |
| Postgres (desde host) | `localhost:5432` |

---

## Infraestructura (`.env` raíz)

| Variable | Valor dev (default) |
|----------|---------------------|
| `POSTGRES_USER` | `emergencias_user` |
| `POSTGRES_PASSWORD` | `cambiar_en_produccion` |
| `POSTGRES_DB` | `emergencias_db` |
| `POSTGRES_HOST` (en Docker) | `db` |
| `POSTGRES_PORT` | `5432` |
| `DATABASE_URL` (host → contenedor) | `postgresql+asyncpg://emergencias_user:cambiar_en_produccion@localhost:5432/emergencias_db` |
| `SECRET_KEY` (JWT) | `cambiar_por_una_clave_segura_256_bits` |
| `SMTP_HOST` | `mailhog` (alias Mailpit en compose) |
| `SMTP_PORT` | `1025` |
| `MAIL_FROM` | `noreply@emergenciasviales.local` |

---

## Organización principal — `demo-sc`

Tenant por defecto (Santa Cruz). Slug obligatorio en login móvil, portal taller y API (`X-Tenant-Slug: demo-sc`).  
Password de **todas** las cuentas: **`scdemo1`**.

### Cuentas plataforma y clientes (nivel organización)

| Rol | Email | Login | Notas |
|-----|-------|-------|--------|
| **Admin plataforma** | `patricio.mendez@sc-demo.test` | `/admin/login` | Rol `ADMIN` |
| **Cliente móvil** | `carlos.vega@sc-demo.test` | App cliente, org `demo-sc` | Vehículo demo seed |

Los **clientes son de la organización**, no de un taller concreto: cualquier taller de `demo-sc` puede atenderlos.

### Red de talleres — responsables, técnicos y portal `/taller`

Login taller: org **`demo-sc`** + email + `scdemo1`.

| # | Taller | Responsable (portal `/taller`) | Técnico (app móvil técnico) |
|---|--------|--------------------------------|----------------------------|
| 1 | Mecánica Express Rivero | `luis.rivera@sc-demo.test` | `marco.salas@sc-demo.test` |
| 2 | Auxilio Vial 4to Anillo SC | `rodrigo.torrez@sc-demo.test` | `andres.vargas@sc-demo.test` |
| 3 | Auxilio Sur SC — Zona Piraí | `sandra.miranda@sc-demo.test` | `mateo.rios@sc-demo.test` |
| 4 | Mecánica Express Urubó | `felipe.guzman@sc-demo.test` | `julia.meza@sc-demo.test` |
| 5 | Grúas Palermo Norte SC | `elena.cortez@sc-demo.test` | `renato.paz@sc-demo.test` |
| 6 | Auxilio Centro SC — 2do anillo | `pablo.ramos@sc-demo.test` | `diego.flores@sc-demo.test` |

Teléfonos responsables: +591 77010012 … 77010018 · Técnicos: 77010013, 77010024 … 77010028.

---

## 6 organizaciones SaaS (multi-org)

Patrón de email: `{local}@{slug}.demo.test` · Password: **`scdemo1`**  
Login portal taller: **slug de org** + email + password.

Cada org tiene **5 talleres** (1 principal + 4 sucursales), **2 técnicos en el principal** + **1 técnico por sucursal**, y **2 clientes** compartidos a nivel org.

### Matriz taller → responsable → técnico (patrón `{slug}`)

| Sucursal | Responsable (portal `/taller`) | Técnico(s) (app móvil) |
|----------|--------------------------------|-------------------------|
| Principal | `responsable@{slug}.demo.test` | `tecnico1@…`, `tecnico2@…` |
| Norte | `taller-norte@{slug}.demo.test` | `tecnico-norte@{slug}.demo.test` |
| Sur | `taller-sur@{slug}.demo.test` | `tecnico-sur@{slug}.demo.test` |
| Este | `taller-este@{slug}.demo.test` | `tecnico-este@{slug}.demo.test` |
| Oeste | `taller-oeste@{slug}.demo.test` | `tecnico-oeste@{slug}.demo.test` |

Clientes org: `cliente1@{slug}.demo.test`, `cliente2@{slug}.demo.test`

| Slug org | Plan | Taller principal |
|----------|------|------------------|
| `org-free-equipetrol` | Free | Taller Equipetrol Express |
| `org-free-urbari` | Free | Urbari Mecánica Rápida |
| `org-pro-anillo` | Pro | Auxilio Vial 4to Anillo Pro |
| `org-pro-plan3000` | Pro | Taller Plan 3000 Pro |
| `org-max-centro` | Max | Centro Max Asistencia Vial |
| `org-max-el-torno` | Max | El Torno Max Vial |

### Detalle por organización

#### `org-free-equipetrol` (Free)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-free-equipetrol.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-free-equipetrol.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-free-equipetrol.demo.test` |
| Responsable Norte | `taller-norte@org-free-equipetrol.demo.test` |
| Técnico Norte | `tecnico-norte@org-free-equipetrol.demo.test` |
| Responsable Sur | `taller-sur@org-free-equipetrol.demo.test` |
| Técnico Sur | `tecnico-sur@org-free-equipetrol.demo.test` |
| Responsable Este | `taller-este@org-free-equipetrol.demo.test` |
| Técnico Este | `tecnico-este@org-free-equipetrol.demo.test` |
| Responsable Oeste | `taller-oeste@org-free-equipetrol.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-free-equipetrol.demo.test` |
| Cliente 1 | `cliente1@org-free-equipetrol.demo.test` |
| Cliente 2 | `cliente2@org-free-equipetrol.demo.test` |

Placas vehículos: `SCF101A`, `SCF102B`

#### `org-free-urbari` (Free)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-free-urbari.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-free-urbari.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-free-urbari.demo.test` |
| Responsable Norte | `taller-norte@org-free-urbari.demo.test` |
| Técnico Norte | `tecnico-norte@org-free-urbari.demo.test` |
| Responsable Sur | `taller-sur@org-free-urbari.demo.test` |
| Técnico Sur | `tecnico-sur@org-free-urbari.demo.test` |
| Responsable Este | `taller-este@org-free-urbari.demo.test` |
| Técnico Este | `tecnico-este@org-free-urbari.demo.test` |
| Responsable Oeste | `taller-oeste@org-free-urbari.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-free-urbari.demo.test` |
| Cliente 1 | `cliente1@org-free-urbari.demo.test` |
| Cliente 2 | `cliente2@org-free-urbari.demo.test` |

Placas: `SCU201A`, `SCU202B`

#### `org-pro-anillo` (Pro)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-pro-anillo.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-pro-anillo.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-pro-anillo.demo.test` |
| Responsable Norte | `taller-norte@org-pro-anillo.demo.test` |
| Técnico Norte | `tecnico-norte@org-pro-anillo.demo.test` |
| Responsable Sur | `taller-sur@org-pro-anillo.demo.test` |
| Técnico Sur | `tecnico-sur@org-pro-anillo.demo.test` |
| Responsable Este | `taller-este@org-pro-anillo.demo.test` |
| Técnico Este | `tecnico-este@org-pro-anillo.demo.test` |
| Responsable Oeste | `taller-oeste@org-pro-anillo.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-pro-anillo.demo.test` |
| Cliente 1 | `cliente1@org-pro-anillo.demo.test` |
| Cliente 2 | `cliente2@org-pro-anillo.demo.test` |

Placas: `SCP301A`, `SCP302B`

#### `org-pro-plan3000` (Pro)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-pro-plan3000.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-pro-plan3000.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-pro-plan3000.demo.test` |
| Responsable Norte | `taller-norte@org-pro-plan3000.demo.test` |
| Técnico Norte | `tecnico-norte@org-pro-plan3000.demo.test` |
| Responsable Sur | `taller-sur@org-pro-plan3000.demo.test` |
| Técnico Sur | `tecnico-sur@org-pro-plan3000.demo.test` |
| Responsable Este | `taller-este@org-pro-plan3000.demo.test` |
| Técnico Este | `tecnico-este@org-pro-plan3000.demo.test` |
| Responsable Oeste | `taller-oeste@org-pro-plan3000.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-pro-plan3000.demo.test` |
| Cliente 1 | `cliente1@org-pro-plan3000.demo.test` |
| Cliente 2 | `cliente2@org-pro-plan3000.demo.test` |

Placas: `SCP401A`, `SCP402B`

#### `org-max-centro` (Max)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-max-centro.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-max-centro.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-max-centro.demo.test` |
| Responsable Norte | `taller-norte@org-max-centro.demo.test` |
| Técnico Norte | `tecnico-norte@org-max-centro.demo.test` |
| Responsable Sur | `taller-sur@org-max-centro.demo.test` |
| Técnico Sur | `tecnico-sur@org-max-centro.demo.test` |
| Responsable Este | `taller-este@org-max-centro.demo.test` |
| Técnico Este | `tecnico-este@org-max-centro.demo.test` |
| Responsable Oeste | `taller-oeste@org-max-centro.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-max-centro.demo.test` |
| Cliente 1 | `cliente1@org-max-centro.demo.test` |
| Cliente 2 | `cliente2@org-max-centro.demo.test` |

Placas: `SCM501A`, `SCM502B`

#### `org-max-el-torno` (Max)

| Rol | Email |
|-----|--------|
| Responsable principal | `responsable@org-max-el-torno.demo.test` |
| Técnico 1 (principal) | `tecnico1@org-max-el-torno.demo.test` |
| Técnico 2 (principal) | `tecnico2@org-max-el-torno.demo.test` |
| Responsable Norte | `taller-norte@org-max-el-torno.demo.test` |
| Técnico Norte | `tecnico-norte@org-max-el-torno.demo.test` |
| Responsable Sur | `taller-sur@org-max-el-torno.demo.test` |
| Técnico Sur | `tecnico-sur@org-max-el-torno.demo.test` |
| Responsable Este | `taller-este@org-max-el-torno.demo.test` |
| Técnico Este | `tecnico-este@org-max-el-torno.demo.test` |
| Responsable Oeste | `taller-oeste@org-max-el-torno.demo.test` |
| Técnico Oeste | `tecnico-oeste@org-max-el-torno.demo.test` |
| Cliente 1 | `cliente1@org-max-el-torno.demo.test` |
| Cliente 2 | `cliente2@org-max-el-torno.demo.test` |

Placas: `SCM601A`, `SCM602B`

---

## Clientes stress visual (opcional)

Cargados con `docker compose exec backend python -m app.seeds` si corre `dev_stress_visual`.

| Campo | Valor |
|-------|--------|
| Password | `scdemo1` |
| Dominio | `*.lista.sc-demo.test` |
| Patrón email | `{nombre}.{apellido}.{NN}@lista.sc-demo.test` (NN = 01…08) |
| Teléfono | `+59177021{NNN}` |

Ejemplos:

| Email | Password |
|-------|----------|
| `valentina.suarez.01@lista.sc-demo.test` | `scdemo1` |
| `diego.camacho.02@lista.sc-demo.test` | `scdemo1` |
| `fernanda.quiroga.03@lista.sc-demo.test` | `scdemo1` |
| `joseLuis.aguilera.04@lista.sc-demo.test` | `scdemo1` |
| `andrea.pena.05@lista.sc-demo.test` | `scdemo1` |
| `ricardo.villanueva.06@lista.sc-demo.test` | `scdemo1` |
| `mariaElena.rojas.07@lista.sc-demo.test` | `scdemo1` |
| `gabriel.ortiz.08@lista.sc-demo.test` | `scdemo1` |

Org: `demo-sc` (tenant por defecto).

---

## API keys y secretos (`.env` — no versionar)

Estos valores **no** están duplicados aquí por seguridad. Abrí `.env` en la raíz del repo:

| Variable | Uso |
|----------|-----|
| `GEMINI_API_KEY` | Reportes por voz (portal taller) |
| `GEMINI_MODEL` | `gemini-2.5-flash` |
| `STRIPE_SECRET_KEY` | Stripe test (`sk_test_…`) — backend billing |
| `STRIPE_PUBLISHABLE_KEY` | Stripe test (`pk_test_…`) — checkout |
| `STRIPE_SAAS_WEBHOOK_SECRET` | Webhook SaaS (vacío en local OK) |
| `STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES` | `true` — crea prices en test |
| `FIREBASE_CREDENTIALS_PATH` | `/app/firebase-credentials.json` (FCM desactivado por defecto) |

---

## Cómo cargar / refrescar datos demo

```powershell
# Seed completo (demo-sc emergencias + multi-org + stress, idempotente)
docker compose exec backend python -m app.seeds
```

En Docker dev, con `docker-compose.override.yml` también se cargan al arrancar:

| Flag | Datos |
|------|--------|
| `SEED_DEMO_SANTA_CRUZ_ON_START=true` | 10 solicitudes `[DEMO-SC]` — bandeja, historial, comisiones (taller `luis.rivera@…`) |
| `SEED_DEMO_MEDIA_PRIORIDAD_ON_START=true` | Notificaciones, chat, 2º taller, ai_payload |
| `SEED_MULTI_ORG_EMERGENCIAS_ON_START=true` | 5 solicitudes por org multi-org (6 talleres) |

Por org multi-org ver login: `responsable@{slug}.demo.test` / `scdemo1`.

---

## Referencias en código

- `backend/app/seeds/identidades_demo_sc.py` — demo-sc
- `backend/app/seeds/identidades_multi_org.py` — 6 organizaciones
- `.env.example` — plantilla de variables
- `docs/ai/FLOWS_PORTAL_TALLER.md` — flujos login/registro taller
