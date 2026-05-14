# Guía de Instalación

## Requisitos

- Docker Engine 24+
- Docker Compose v2
- Acceso SSH al servidor Odoo a monitorear

---

## 1. Clonar el repositorio

```bash
git clone <repo-url>
cd monitor
```

---

## 2. Crear el archivo `.env`

Copiar la plantilla y ajustar los valores:

```bash
cp .env.example .env
```

Si no existe `.env.example`, crear `.env` con este contenido mínimo:

```env
# Base de datos
POSTGRES_DB=odoo_monitor
POSTGRES_USER=monitor
POSTGRES_PASSWORD=cambia_esto

# Backend
DATABASE_URL=postgresql+asyncpg://monitor:cambia_esto@postgres:5432/odoo_monitor
DATABASE_URL_SYNC=postgresql+psycopg2://monitor:cambia_esto@postgres:5432/odoo_monitor

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Seguridad — generar con: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=clave_secreta_minimo_32_caracteres_aqui

# Generar con: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=clave_fernet_base64_generada_aqui

# Usuario admin inicial
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin1234!
ADMIN_USERNAME=admin

# CORS — dominio donde corre el frontend
ALLOWED_ORIGINS=http://localhost,http://tu-dominio.com
```

### Generar las claves de seguridad

```bash
# SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 3. Levantar la stack

```bash
docker compose up -d
```

La primera vez tarda ~2 minutos mientras se construyen las imágenes y se aplican las migraciones.

### Verificar que todo esté corriendo

```bash
docker compose ps
```

Todos los contenedores deben estar en estado `healthy` o `Up`:

```
monitor-backend-1         Up (healthy)
monitor-celery-beat-1     Up
monitor-celery-worker-1   Up (healthy)
monitor-frontend-1        Up (healthy)
monitor-nginx-1           Up (healthy)
monitor-postgres-1        Up (healthy)
monitor-redis-1           Up (healthy)
```

---

## 4. Acceder a la aplicación

Abrir `http://localhost` en el navegador.

Credenciales iniciales (las definidas en `.env`):
- **Email**: `admin@example.com`
- **Password**: `Admin1234!`

---

## Variables de entorno opcionales

| Variable | Default | Descripción |
|----------|---------|-------------|
| `APP_ENV` | `production` | Entorno: `production`, `development`, `test` |
| `LOG_LEVEL` | `INFO` | Nivel de logs |
| `DEFAULT_MONITORING_INTERVAL` | `60` | Segundos entre recolecciones |
| `METRIC_RETENTION_DAYS` | `90` | Días de retención de métricas históricas |
| `SSH_TIMEOUT` | `10` | Timeout SSH en segundos |
| `SMTP_HOST` | `` | Servidor SMTP para notificaciones por email |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USER` | `` | Usuario SMTP |
| `SMTP_PASSWORD` | `` | Contraseña SMTP |
| `SMTP_FROM` | `noreply@example.com` | Remitente de emails |
| `TELEGRAM_BOT_TOKEN` | `` | Token del bot de Telegram para alertas |

---

## Actualizar

```bash
git pull
docker compose build
docker compose up -d
```

Las migraciones de base de datos se aplican automáticamente al iniciar el backend.

---

## Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f celery-worker

# Reiniciar un servicio
docker compose restart backend

# Apagar todo (conserva datos)
docker compose down

# Apagar y borrar volúmenes (borra base de datos)
docker compose down -v
```
