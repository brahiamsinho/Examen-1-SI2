# Plataforma Inteligente de Atención de Emergencias Vehiculares 🚗🚨

Sistema digital completo, modular y escalable para coordinar y auditar la atención de emergencias vehiculares. Conecta clientes y sus vehículos con talleres, técnicos asignados y un panel administrativo de auditoría, manteniendo trazabilidad completa.

---

## 📋 Requisitos Previos

Asegúrate de contar con lo siguiente instalado en tu entorno local antes de iniciar:
- **Docker** y **Docker Compose**
- **Node.js** (v18+) y **npm**
- **Angular CLI** (v17+) `npm install -g @angular/cli@17`
- **Flutter SDK** (v3.3+)
- (Opcional) Cliente de visualización de base de datos tipo DBeaver o PgAdmin.

---

## 🐳 Gestión de Contenedores y Entorno con Docker

La arquitectura local está enteramente dockerizada. Es vital contar con el `.env` creado usando tu archivo `.env.example` como base.

### Arranque del entorno
| Acción | Comando |
|--------|---------|
| **Levantar e inicializar todo** (Recomendado primera vez) | `docker compose up -d --build` |
| Levantar servicios creados | `docker compose up -d` |
| Detener los contenedores | `docker compose down` |
| **Peligro:** Detener y borrar volúmenes (⚠️ Borra toda la base de datos) | `docker compose down -v` |

### Logs y Troubleshooting
| Acción | Comando |
|--------|---------|
| Ver logs en vivo de todos los servicios | `docker compose logs -f` |
| Ver logs exclusivos del backend | `docker compose logs -f backend` |
| Ver logs del frontend | `docker compose logs -f frontend` |
| Ver logs de la base de datos | `docker compose logs -f db` |
| Reiniciar únicamente el backend | `docker compose restart backend` |

---

## 🐍 Backend (FastAPI + SQLAlchemy + Alembic)

A diferencia de Django, FastAPI no cuenta con un motor ORM o de migraciones nativo. Utilizamos **SQLAlchemy** para mapear los objetos y **Alembic** para el control de versiones (migraciones).


| Acción | Django ORM | Equivalente en FastAPI (Alembic) |
|--------|------------|----------------------------------|
| **Preparar migración** detectando los cambios | `python manage.py makemigrations` | `docker compose exec backend alembic revision --autogenerate -m "Agregado campo X"` |
| **Ejecutar / Aplicar** migración a la base de datos | `python manage.py migrate` | `docker compose exec backend alembic upgrade head` |
| **Deshacer (Rollback)** la última migración | `python manage.py migrate <app> <anterior>` | `docker compose exec backend alembic downgrade -1` |

### Alembic en este repositorio

- **Qué es:** versiona el esquema de PostgreSQL (cambios incrementales en archivos Python bajo `backend/alembic/versions/`), parecido a las carpetas `migrations/` de Django.
- **No sustituye el backend:** FastAPI, routers y modelos siguen igual; solo se añade la herramienta de migración.
- **Convivencia con `init.sql`:** la primera migración (`0001_baseline`) está vacía: el esquema inicial lo sigue creando Docker con `backend/migrations/init.sql` la primera vez que levantas Postgres.
- **Una vez por base de datos** creada con ese flujo, marca la línea base para Alembic (sin ejecutar SQL otra vez):

```bash
docker compose exec backend alembic stamp 0001_baseline
```

A partir de ahí, cuando **realmente cambies** modelos SQLAlchemy: `revision --autogenerate -m "mensaje útil"` → **revisar a mano** el `.py` generado (autogenerate se equivoca con IDENTITY, índices y nombres de FK) → `upgrade head`.

**Importante:** no ejecutes `--autogenerate` “de prueba” sin cambios en código: suele generar un diff enorme contra la BD creada por `init.sql` y `upgrade head` puede fallar (p. ej. `ALTER COLUMN id` en columnas IDENTITY). Si ya generaste un archivo malo en `alembic/versions/`, bórralo; si `upgrade` falló, la versión en BD suele seguir en `0001_baseline` (transacción revertida).

- **Poblar datos demo (seeds):** `docker compose exec backend python -m app.seeds` — admin, cliente, taller, técnico según variables `SEED_*` en el `.env` raíz (valores cortos en `.env.example`).

**Nota:** Alembic usa el driver síncrono **psycopg** (`postgresql+psycopg://…`); la API sigue usando **asyncpg** (`postgresql+asyncpg://…`). La conversión la hace `backend/alembic/env.py`.

---

## 🗄️ Base de Datos e Inicialización
Al crear el contenedor PostgreSQL con volumen vacío, se monta `backend/migrations/init.sql` (tablas + roles/permisos base). Alembic gestiona **cambios posteriores** al esquema (ver sección anterior).

| Acción | Comando |
|--------|---------|
| **Inicializar BD automáticamente** | Ejecutando *docker compose up*, postgres detecta `init.sql` e inicializa si está vacío el volumen. |
| **Destruir BD y recrear desde cero** | `docker compose down -v && docker compose up -d db` |
| **Forzar ejecución del archivo SQL** | `docker compose exec db psql -U emergencias_user -d emergencias_db -f /docker-entrypoint-initdb.d/01_init.sql` |
| Entrar a la consola de la BD | `docker compose exec db psql -U emergencias_user -d emergencias_db` |

---

## 🌐 Frontend (Angular Web)

El frontend web expone los paneles de administración y consumo de datos consumiendo los recursos bajo Nginx al compilarse en servidor para producción y en node para desarrollo de forma local.

*(Asegúrate de estar en el directorio root `/frontend`)*

| Acción | Comando Ejecutivo |
|--------|-------------------|
| Descargar e instalar dependencias del proyecto | `npm install` |
| Servir ambiente y desarrollar local (Hot Reload) | `ng serve` |
| Ejecutar lints de análisis estático | `ng lint` |
| Construir / Compilar aplicación final (Producción) | `ng build --configuration production` |

---

## 📱 Móvil (Flutter)

App para **cliente** (registro, vehículos, perfil) y **técnico / responsable de taller** (login, home, perfil, placeholders de servicios). Configuración por `mobile/.env` (`API_BASE_URL`, `APP_NAME`). Detalle: **[mobile/README.md](mobile/README.md)**.

*(Directorio del proyecto: `mobile/`)*

| Acción | Comando |
|--------|---------|
| Dependencias | `flutter pub get` |
| Ejecutar en emulador o dispositivo | `flutter run` |
| Análisis estático | `dart analyze` |
| Limpiar build local | `flutter clean` |
| APK Android | `flutter build apk` |

Usuarios demo del backend (tras `docker compose exec backend python -m app.seeds`): por ejemplo `cli@test.com` / `cli123`, `taller@test.com` / `taller123`, `tec@test.com` / `tec123` (ver `.env.example` raíz y `SEED_*`).

---

## 🔐 Notas Adicionales y Buenas Prácticas

1. **La carpeta `docs/ai/` es vital.** Aquí alojamos el Contexto del software (`ARCHITECTURE.md`, `CURRENT_STATE.md`, etc.). Revísala siempre.
2. Si por algún motivo tienes errores de *caché de Docker*, fuerza el build con la bandera limpia: `docker compose build --no-cache`.
3. Nunca adjuntar datos de variables de entorno (como `SECRET_KEY` o contraseñas) dentro de archivos de repositorio. Manipula esto con los `.env`.
