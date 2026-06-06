# Credenciales de desarrollo — EmergenciasViales

> **Solo entorno local / demo.** Contraseñas cortas a propósito (`scdemo1`).  
> **No uses estos valores en producción.**  
> Secretos de terceros (Gemini, Stripe secret) viven en `.env` (gitignored). Este archivo documenta cuentas demo e infra.

**Última revisión:** 2026-06-05 · Fuente: `identidades_demo_sc.py`, `identidades_multi_org.py`, `.env.example`

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

| Rol | Email | Password | Notas |
|-----|-------|----------|--------|
| **Admin plataforma** | `patricio.mendez@sc-demo.test` | `scdemo1` | Login en `/admin/login`. Rol `ADMIN`. |
| **Cliente (app móvil)** | `carlos.vega@sc-demo.test` | `scdemo1` | Org `demo-sc`. Vehículo demo seed. |
| **Responsable taller 1** | `luis.rivera@sc-demo.test` | `scdemo1` | Taller **Mecánica Express Rivero**. Portal `/taller`. |
| **Técnico** | `marco.salas@sc-demo.test` | `scdemo1` | Asignado al taller principal. App móvil técnico. |
| **Responsable taller 2** | `rodrigo.torrez@sc-demo.test` | `scdemo1` | Taller **Auxilio Vial 4to Anillo SC**. Requiere seed media (`python -m app.seeds`). |

**Teléfonos demo-sc:** +591 77010010 (admin) … 77010014 (taller 2).

---

## 6 organizaciones SaaS (multi-org)

Patrón de email: `{local}@{slug}.demo.test` · Password: **`scdemo1`**  
Login portal taller: slug de org + email + password.

| Slug org | Plan | Taller | Responsable |
|----------|------|--------|-------------|
| `org-free-equipetrol` | Free | Taller Equipetrol Express | `responsable@org-free-equipetrol.demo.test` |
| `org-free-urbari` | Free | Urbari Mecánica Rápida | `responsable@org-free-urbari.demo.test` |
| `org-pro-anillo` | Pro | Auxilio Vial 4to Anillo Pro | `responsable@org-pro-anillo.demo.test` |
| `org-pro-plan3000` | Pro | Taller Plan 3000 Pro | `responsable@org-pro-plan3000.demo.test` |
| `org-max-centro` | Max | Centro Max Asistencia Vial | `responsable@org-max-centro.demo.test` |
| `org-max-el-torno` | Max | El Torno Max Vial | `responsable@org-max-el-torno.demo.test` |

### Detalle por organización

#### `org-free-equipetrol` (Free)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-free-equipetrol.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-free-equipetrol.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-free-equipetrol.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-free-equipetrol.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-free-equipetrol.demo.test` | `scdemo1` |

Placas vehículos: `SCF101A`, `SCF102B`

#### `org-free-urbari` (Free)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-free-urbari.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-free-urbari.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-free-urbari.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-free-urbari.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-free-urbari.demo.test` | `scdemo1` |

Placas: `SCU201A`, `SCU202B`

#### `org-pro-anillo` (Pro)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-pro-anillo.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-pro-anillo.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-pro-anillo.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-pro-anillo.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-pro-anillo.demo.test` | `scdemo1` |

Placas: `SCP301A`, `SCP302B`

#### `org-pro-plan3000` (Pro)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-pro-plan3000.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-pro-plan3000.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-pro-plan3000.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-pro-plan3000.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-pro-plan3000.demo.test` | `scdemo1` |

Placas: `SCP401A`, `SCP402B`

#### `org-max-centro` (Max)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-max-centro.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-max-centro.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-max-centro.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-max-centro.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-max-centro.demo.test` | `scdemo1` |

Placas: `SCM501A`, `SCM502B`

#### `org-max-el-torno` (Max)

| Rol | Email | Password |
|-----|-------|----------|
| Responsable | `responsable@org-max-el-torno.demo.test` | `scdemo1` |
| Técnico 1 | `tecnico1@org-max-el-torno.demo.test` | `scdemo1` |
| Técnico 2 | `tecnico2@org-max-el-torno.demo.test` | `scdemo1` |
| Cliente 1 | `cliente1@org-max-el-torno.demo.test` | `scdemo1` |
| Cliente 2 | `cliente2@org-max-el-torno.demo.test` | `scdemo1` |

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
