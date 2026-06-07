# Despliegue en Azure VM + DNS + HTTPS (Certbot)

Guía para publicar **EmergenciasViales** en una VM Microsoft Azure con dominio Azure (`*.cloudapp.azure.com`) y certificado TLS gratuito de **Let's Encrypt** vía **Certbot**.

## 1. DNS en Azure (no es Certbot)

El hostname `oftalmologia-si2.westus3.cloudapp.azure.com` se configura en **Azure Portal**, no con Certbot:

1. VM → **Redes** → **IP pública** asociada.
2. En la IP pública: **Configuración** → **Nombre DNS** → etiqueta `oftalmologia-si2`.
3. Azure genera: `oftalmologia-si2.westus3.cloudapp.azure.com` apuntando a la IP elástica.

**Certbot** solo emite el certificado HTTPS cuando ese nombre resuelve a tu VM y el puerto **80** está abierto.

## 2. Firewall (NSG)

En el grupo de seguridad de red de la VM, permitir entrante:

| Puerto | Uso |
|--------|-----|
| 22 | SSH (administración) |
| 80 | HTTP (desafío ACME + redirección a HTTPS) |
| 443 | HTTPS (aplicación) |

No expongas PostgreSQL (5432) ni Mailpit (8025) a Internet en producción.

## 3. Variables `.env` (raíz del repo)

Copiá `.env.example` → `.env` y ajustá al menos:

```env
ENVIRONMENT=production
DEBUG=false

PUBLIC_DOMAIN=oftalmologia-si2.westus3.cloudapp.azure.com
CERTBOT_EMAIL=tu-email@ejemplo.com

APP_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
FRONTEND_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
API_PUBLIC_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
EMAIL_LINK_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
EVIDENCIAS_PUBLIC_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com
CORS_ORIGINS=https://oftalmologia-si2.westus3.cloudapp.azure.com

RUN_SEEDS_ON_START=false
SEED_ADMIN_ON_START=false
EMAIL_STRICT=true
```

**Mobile (build/release):**

```bash
flutter build apk --dart-define=API_BASE_URL=https://oftalmologia-si2.westus3.cloudapp.azure.com/api
```

El frontend Angular en producción ya usa `apiUrl: '/api'` (proxy nginx → backend).

## 4. Arquitectura en Azure

```
Internet :443/:80
    │
    ▼
reverse-proxy (nginx + Certbot certs)
    │  proxy_pass
    ▼
frontend (nginx SPA + /api → backend)
    │
    ├── backend (FastAPI)
    ├── db (PostgreSQL, solo red Docker)
    └── mailpit (solo red Docker; SMTP real en prod)
```

Archivos:

| Archivo | Rol |
|---------|-----|
| `deploy/docker-compose.azure.yml` | Overlay: reverse-proxy, certbot, cierra puertos públicos de db/backend |
| `deploy/nginx/azure-http-bootstrap.conf.template` | HTTP sin TLS (primera emisión cert) |
| `deploy/nginx/azure-https.conf.template` | HTTP→HTTPS + TLS |
| `deploy/scripts/certbot-init.sh` | Script único primera vez |

## 5. Despliegue paso a paso (VM Ubuntu)

```bash
# En la VM
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar

git clone <tu-repo> && cd Examen-1-SI2
cp .env.example .env
# Editar .env (nano .env) con PUBLIC_DOMAIN, CERTBOT_EMAIL, URLs https...

chmod +x deploy/scripts/*.sh
./deploy/scripts/certbot-init.sh
```

El script:

1. Levanta el stack con HTTP (bootstrap).
2. Ejecuta `certbot certonly --webroot`.
3. Recrea `reverse-proxy` con plantilla HTTPS.

## 6. Operación

```bash
# Stack completo Azure
docker compose -f docker-compose.yml -f deploy/docker-compose.azure.yml up -d

# Renovación manual
./deploy/scripts/certbot-renew.sh

# Logs
docker logs emergencias_reverse_proxy
docker logs emergencias_certbot
```

Renovación automática: contenedor `emergencias_certbot` (cada 12 h) + hook que recarga nginx.

## 7. Verificación

1. `curl -I http://oftalmologia-si2.westus3.cloudapp.azure.com` → `301` a HTTPS.
2. `curl -I https://oftalmologia-si2.westus3.cloudapp.azure.com` → `200`.
3. Navegador: landing, `/admin/login`, `/taller`.
4. API: `https://.../api/health` (si existe ruta health pública) o login.

## 8. Errores frecuentes

| Síntoma | Causa probable |
|---------|----------------|
| Certbot timeout | NSG sin puerto 80; DNS aún no propagado |
| `connection refused` en 443 | No corrió `certbot-init.sh` fase 3 |
| CORS en login | `CORS_ORIGINS` sin `https://` exacto |
| Mixed content | `APP_PUBLIC_URL` aún en `http://` |

## 9. PUDS / diagrama despliegue

Actualizar diagrama D-006: nodo Azure VM con **reverse-proxy TLS** delante de contenedores Docker Compose.
