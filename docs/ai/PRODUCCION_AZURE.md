# Producción Azure — checklist completo

Guía única para levantar **EmergenciasViales** en VM Azure con HTTPS.

**Dominio de ejemplo:** `oftalmologia-si2.westus3.cloudapp.azure.com`

---

## 1. Azure Portal (antes de tocar el código)

### 1.1 DNS (nombre público)

1. VM → **Redes** → **IP pública**.
2. **Configuración** → **Nombre DNS** → etiqueta: `oftalmologia-si2`.
3. Resultado: `oftalmologia-si2.westus3.cloudapp.azure.com` → IP elástica de la VM.

Verificar desde tu PC:

```bash
nslookup oftalmologia-si2.westus3.cloudapp.azure.com
```

### 1.2 Firewall (NSG)

| Puerto | Protocolo | Para qué |
|--------|-----------|----------|
| 22 | TCP | SSH |
| 80 | TCP | Certbot + redirect HTTPS |
| 443 | TCP | App web + API (proxy nginx) |

**No abrir:** 5432 (PostgreSQL), 8000 (backend directo), 8025 (Mailpit).

### 1.3 VM — software base

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# cerrar sesión SSH y volver a entrar
```

---

## 2. Archivos que deben existir en la VM (no van a Git)

| Archivo | Dónde | Cómo obtenerlo |
|---------|-------|----------------|
| `.env` | raíz del repo | copiar plantilla de abajo |
| `backend/firebase-credentials.json` | backend/ | Firebase Console → Project settings → Service accounts → Generate new private key |
| (opcional) certificados SSL | `deploy/certbot/conf/` | los genera `certbot-init.sh` |

**Nunca** subas `.env` ni `firebase-credentials.json` a GitHub.

---

## 3. Credenciales — qué necesitás y de dónde salen

| Credencial | Variable / archivo | Dónde conseguirla |
|------------|-------------------|-------------------|
| Clave JWT backend | `SECRET_KEY` | Generar aleatoria (64+ chars). Ej: `openssl rand -hex 32` |
| Password PostgreSQL | `POSTGRES_PASSWORD` | Inventar una fuerte (solo Docker interno) |
| Email Let's Encrypt | `CERTBOT_EMAIL` | Tu email real (avisos de expiración cert) |
| Stripe test/live | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) → Developers → API keys |
| Webhook SaaS Stripe | `STRIPE_SAAS_WEBHOOK_SECRET` | Stripe → Webhooks → endpoint → Signing secret (`whsec_...`) |
| Firebase Admin (push mobile) | `backend/firebase-credentials.json` | Firebase Console → Service account JSON |
| Firebase Web (push navegador) | `FIREBASE_WEB_*` en `.env` | Firebase → Project settings → General → Web app + Cloud Messaging → Web Push certificates (VAPID) |
| Gemini (voz reportes taller) | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| SMTP real (opcional) | `SMTP_*` | SendGrid, Gmail workspace, etc. |

### Firebase web — valores mínimos

En `.env` (luego en VM: `cd frontend && npm run env:sync` antes del build si cambiás claves):

```env
FIREBASE_WEB_ENABLED=true
FIREBASE_WEB_API_KEY=
FIREBASE_WEB_AUTH_DOMAIN=transporte-si2.firebaseapp.com
FIREBASE_WEB_PROJECT_ID=transporte-si2
FIREBASE_WEB_STORAGE_BUCKET=transporte-si2.firebasestorage.app
FIREBASE_WEB_MESSAGING_SENDER_ID=
FIREBASE_WEB_APP_ID=1:XXXX:web:YYYY
FIREBASE_WEB_VAPID_KEY=BP...
```

`FIREBASE_WEB_APP_ID` y `FIREBASE_WEB_VAPID_KEY` deben ser **reales** (no placeholders `web:XXXXXXXX` / `BPxxxx`).

---

## 4. `.env` de producción — plantilla lista para pegar

Copiá a `.env` en la **raíz del repo en la VM**. Reemplazá todo lo que dice `CAMBIAR`.

```env
# ── Entorno ──────────────────────────────────────────────
ENVIRONMENT=production
DEBUG=false
TZ=America/La_Paz
PGTZ=America/La_Paz
API_PREFIX=/api

# ── Seguridad ────────────────────────────────────────────
SECRET_KEY=CAMBIAR_clave_jwt_larga_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── PostgreSQL (solo red Docker; overlay Azure no expone 5432) ──
POSTGRES_USER=emergencias_user
POSTGRES_PASSWORD=CAMBIAR_password_db_fuerte
POSTGRES_DB=emergencias_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# ── Azure DNS + HTTPS (Certbot) ────────────────────────────
PUBLIC_DOMAIN=oftalmologia-si2.westus3.cloudapp.azure.com
CERTBOT_EMAIL=CAMBIAR_tu_email@ejemplo.com
AZURE_HTTP_PORT=80
AZURE_HTTPS_PORT=443
FRONTEND_UPSTREAM=frontend:80
# Primera vez certbot-init usa bootstrap; después dejar en https:
NGINX_AZURE_CONF_TEMPLATE=./deploy/nginx/azure-https.conf.template

# ── URLs públicas (mismo dominio; nginx proxy /api → backend) ──
APP_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
FRONTEND_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
API_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
EMAIL_LINK_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
EVIDENCIAS_PUBLIC_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
CORS_ORIGINS=https://oftalmologia-si2.westus3.cloudapp.azure.com

# ── Docker interno ───────────────────────────────────────
BACKEND_UPSTREAM=backend:8000
UVICORN_PORT=8000
RUN_MIGRATIONS_ON_START=true
RUN_SEEDS_ON_START=false
RUN_SEEDS_IN_LIFESPAN=false

# ── Seeds demo — TODO false en producción real ─────────────
SEED_ADMIN_ON_START=false
SEED_CLIENTE_ON_START=false
SEED_TALLER_ON_START=false
SEED_TECNICO_ON_START=false
SEED_DEMO_SANTA_CRUZ_ON_START=false
SEED_DEMO_MEDIA_PRIORIDAD_ON_START=false
SEED_STRESS_VISUAL_ON_START=false
SEED_MULTI_ORGS_ON_START=false
SEED_MULTI_ORG_EMERGENCIAS_ON_START=false

# ── Correo ───────────────────────────────────────────────
# Demo/examen sin SMTP real:
EMAIL_ENABLED=false
EMAIL_STRICT=false
MAIL_FROM=noreply@oftalmologia-si2.westus3.cloudapp.azure.com
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USE_TLS=false
SMTP_USER=
SMTP_PASSWORD=

# Producción con SMTP real (descomentar y completar):
# EMAIL_ENABLED=true
# EMAIL_STRICT=true
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USE_TLS=true
# SMTP_USER=apikey
# SMTP_PASSWORD=CAMBIAR

# ── Pagos ────────────────────────────────────────────────
# Demo examen:
PAGO_PROVEEDOR_DEFAULT=SIMULADO
PAGO_SIMULADO_AUTOCOMPLETE=true

# Stripe real:
# PAGO_PROVEEDOR_DEFAULT=STRIPE
# PAGO_SIMULADO_AUTOCOMPLETE=false
# STRIPE_SECRET_KEY=sk_test_... o sk_live_...
# STRIPE_PUBLISHABLE_KEY=pk_test_... o pk_live_...
# STRIPE_SAAS_WEBHOOK_SECRET=whsec_...
# STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=false
# SAAS_PLATFORM_BASE_DOMAIN=oftalmologia-si2.westus3.cloudapp.azure.com

STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SAAS_WEBHOOK_SECRET=
STRIPE_SAAS_PRICE_STARTER=
STRIPE_SAAS_PRICE_PRO=
STRIPE_SAAS_PRICE_MAX=
STRIPE_SAAS_AUTO_BOOTSTRAP_PRICES=true

# ── Push Firebase ────────────────────────────────────────
FCM_ENABLED=true
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

FIREBASE_WEB_ENABLED=true
FIREBASE_WEB_API_KEY=CAMBIAR
FIREBASE_WEB_AUTH_DOMAIN=transporte-si2.firebaseapp.com
FIREBASE_WEB_PROJECT_ID=transporte-si2
FIREBASE_WEB_STORAGE_BUCKET=transporte-si2.firebasestorage.app
FIREBASE_WEB_MESSAGING_SENDER_ID=CAMBIAR
FIREBASE_WEB_APP_ID=CAMBIAR
FIREBASE_WEB_MEASUREMENT_ID=
FIREBASE_WEB_VAPID_KEY=CAMBIAR

# ── IA (opcional; requiere docker compose --profile ai) ───
AI_ENABLED=false
AI_INFERENCE_BASE_URL=http://ai-inference:8080
AI_INFERENCE_STUB=true
GEMINI_API_KEY=

# ── Rutas ETA OSRM (opcional; perfil routing) ────────────
OSRM_ENABLED=false
OSRM_BASE_URL=http://osrm:5000

# ── Backups ──────────────────────────────────────────────
BACKUP_ENABLED=true
BACKUP_STORAGE_DIR=backups
BACKUP_RETENTION_DAYS_DEFAULT=7
BACKUP_SCHEDULER_INTERVAL_SECONDS=3600

EVIDENCIA_MAX_UPLOAD_BYTES=15728640
```

### Demo del examen (datos de prueba)

Si necesitás usuarios demo en la VM **una sola vez**:

```bash
docker compose exec backend python -m app.seeds
```

No uses `SEED_*_ON_START=true` en producción permanente.

Usuarios demo típicos (contraseña `scdemo1`):

| Rol | Email |
|-----|-------|
| Admin | patricio.mendez@sc-demo.test |
| Cliente | carlos.vega@sc-demo.test |
| Taller | luis.rivera@sc-demo.test |
| Técnico | marco.salas@sc-demo.test |

---

## 5. Comandos de despliegue (en la VM)

```bash
git clone <URL_REPO>
cd Examen-1-SI2

cp docs/ai/PRODUCCION_AZURE.md .   # opcional, referencia local
nano .env                          # pegar plantilla §4 y completar CAMBIAR

# Firebase JSON (copiar por scp desde tu PC):
# scp backend/firebase-credentials.json user@VM:~/Examen-1-SI2/backend/

chmod +x deploy/scripts/*.sh

# Primera vez: certificado + HTTPS
./deploy/scripts/certbot-init.sh

# Siguientes veces / reinicios
docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml up -d --build
```

### Perfiles opcionales

```bash
# IA (Whisper/YOLO)
docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml --profile ai up -d

# OSRM rutas
docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml --profile routing up -d
```

---

## 6. Mobile (build apuntando a producción)

```bash
flutter build apk --dart-define=API_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com/api
```

iOS:

```bash
flutter build ios --dart-define=API_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com/api
```

---

## 7. Verificación rápida

```bash
curl -I http://oftalmologia-si2.westus3.cloudapp.azure.com
# → 301 Location: https://...

curl -I https://oftalmologia-si2.westus3.cloudapp.azure.com
# → 200

curl -s https://oftalmologia-si2.westus3.cloudapp.azure.com/api/health
# → JSON ok (si endpoint existe)
```

Navegador:

- `https://oftalmologia-si2.westus3.cloudapp.azure.com/` — landing
- `https://.../admin/login` — panel admin
- `https://.../taller` — portal taller

---

## 8. Errores frecuentes

| Síntoma | Solución |
|---------|----------|
| Certbot timeout | NSG sin puerto 80; DNS no apunta a la VM |
| CORS / login falla | `CORS_ORIGINS` debe ser exactamente `https://oftalmologia-si2.westus3.cloudapp.azure.com` |
| Links rotos evidencias/mail | Todas las URLs públicas con `https://`, sin `:8000` |
| Push web no llega | `FIREBASE_WEB_VAPID_KEY` y `FIREBASE_WEB_APP_ID` reales + permiso notificaciones Chrome |
| Push mobile no llega | `FCM_ENABLED=true` + `firebase-credentials.json` montado |
| Puerto 80 ocupado | Usar overlay Azure (`deploy/docker-compose.azure.yml`) con `ports: !reset` |
| `.env: Cruz: command not found` al ejecutar `certbot-init.sh` | Valores con espacios/comas sin comillas (`Santa Cruz`, `Barrio Equipetrol, …`). Solución: `git pull` (usa `deploy/scripts/load-env.sh`) **o** poner comillas dobles en esas líneas del `.env` |

---

## 9. Renovación certificado SSL

Automática: contenedor `emergencias_certbot`.

Manual:

```bash
./deploy/scripts/certbot-renew.sh
```

---

## 10. Arquitectura (1 diagrama)

```
Internet
   │  :443 / :80
   ▼
reverse-proxy (nginx + TLS Certbot)
   │
   ▼
frontend (Angular + nginx /api → backend)
   ├── backend (FastAPI)
   ├── db (PostgreSQL)
   └── mailpit (solo red interna Docker)
```

---

## 11. Checklist final antes de la defensa

- [ ] DNS Azure configurado y resuelve
- [ ] NSG: 22, 80, 443
- [ ] `.env` con `ENVIRONMENT=production`, `DEBUG=false`
- [ ] `SECRET_KEY` y `POSTGRES_PASSWORD` cambiados
- [ ] URLs todas en `https://oftalmologia-si2.westus3.cloudapp.azure.com`
- [ ] `certbot-init.sh` ejecutado sin error
- [ ] Landing + admin + taller cargan por HTTPS
- [ ] Mobile compilada con `API_BASE_URL` HTTPS
- [ ] `.env` y `firebase-credentials.json` **no** están en Git

---

**Ver también:** `docs/ai/DEPLOYMENT_AZURE.md` (detalle técnico Certbot/nginx).
