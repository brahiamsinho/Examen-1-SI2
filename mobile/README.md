# mobile_emergencias

App Flutter para EmergenciasViales (cliente y flujos móviles).

## Configuración `mobile/.env` (obligatorio)

La app **carga variables en runtime** desde el archivo **`mobile/.env`**, incluido como asset. No uses URLs fijas en el código para el API.

1. Copiá la plantilla: `cp .env.example .env` (o duplicá `.env.example` manualmente en Windows).
2. Editá `.env` en esta carpeta (`mobile/`), al menos:
   - **`API_BASE_URL`**: base del API **sin barra final**, alcanzable **desde el dispositivo** (emulador: `http://10.0.2.2:8000/api`; teléfono físico: `http://<IPv4-de-tu-PC>:8000/api`).
   - **`APP_NAME`**: nombre corto que verás en splash, selector de modo y título material.

Opcional:

- `API_CONNECT_TIMEOUT_SECONDS` (por defecto 10, entre 5 y 120).
- `API_RECEIVE_TIMEOUT_SECONDS` (por defecto 30, entre 5 y 300).

El acceso tipado está en `lib/core/config/app_env.dart`; las rutas HTTP en `lib/core/constants/api_constants.dart`.

## Módulo técnico / mecánico (ciclo 1)

Rutas bajo `lib/tecnico/` (misma filosofía que `lib/cliente/`: application / data / domain / presentation). Sesión con tokens **separados** del cliente (`tecnico_access_token` en secure storage).

- Entrada: selector de modo → **Técnico** → splash técnico → login.
- Roles: `TECNICO` o `TALLER_RESPONSABLE`. Seeds cortos (tras `python -m app.seeds`): `tec@test.com` / `tec123` (técnico), `taller@test.com` / `taller123` (responsable).

**Nota:** `.env` no debe subirse al repositorio (suele estar ignorado). Para CI, generá `.env` a partir de `.env.example` o secretos del pipeline.

**Seguridad:** los valores de `.env` quedan dentro del paquete instalado; no pongas secretos de producción ahí si el APK puede distribuirse fuera de tu equipo.

## Comandos

```bash
flutter pub get
flutter run
dart analyze
```
