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
| **Preparar migración** detectando los cambios | `python manage.py makemigrations` | `alembic revision --autogenerate -m "Agregado campo X"` |
| **Ejecutar / Aplicar** migración a la base de datos | `python manage.py migrate` | `alembic upgrade head` |
| **Deshacer (Rollback)** la última migración | `python manage.py migrate <app> <anterior>` | `alembic downgrade -1` |

---

## 🗄️ Base de Datos e Inicialización
Actualmente, en lugar de correr migraciones pesadas, las tablas y los registros semillas se configuran al crear el contenedor PostgreSQL montando un volúmen al script `backend/migrations/init.sql`.

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

Aplicación enfocada a actores logísticos como técnicos o como vista compacta de propietarios (clientes).

*(Asegúrate de estar en el directorio root `/mobile`)*

| Acción | Comando Ejecutivo |
|--------|-------------------|
| Inicializar proyecto estructural base en caso de ser necesario | `flutter create .` |
| Descargar/actualizar las librerías definidas en el yaml | `flutter pub get` |
| Revisar el estado y configuraciones del SDK | `flutter doctor` |
| Levantar app dentro de un emulador (Previamente abierto) o equipo | `flutter run` |
| Realizar limpieza del entorno Flutter | `flutter clean` |
| **Compilar** aplicación en APK de Android. | `flutter build apk` |

---

## 🔐 Notas Adicionales y Buenas Prácticas

1. **La carpeta `docs/ai/` es vital.** Aquí alojamos el Contexto del software (`ARCHITECTURE.md`, `CURRENT_STATE.md`, etc.). Revísala siempre.
2. Si por algún motivo tienes errores de *caché de Docker*, fuerza el build con la bandera limpia: `docker compose build --no-cache`.
3. Nunca adjuntar datos de variables de entorno (como `SECRET_KEY` o contraseñas) dentro de archivos de repositorio. Manipula esto con los `.env`.
