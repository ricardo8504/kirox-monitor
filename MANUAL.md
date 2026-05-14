# Manual de Usuario

## Roles y permisos

| Rol | Ver métricas | Agregar/editar servidores | Gestionar usuarios | Eliminar |
|-----|:---:|:---:|:---:|:---:|
| READONLY | ✓ | — | — | — |
| OPERATOR | ✓ | ✓ | — | — |
| ADMIN | ✓ | ✓ | ✓ | ✓ |

---

## Servidores

### Agregar un servidor

1. Ir a **Servidores** → botón **Agregar servidor**
2. Completar los campos:

| Campo | Descripción |
|-------|-------------|
| Nombre | Nombre descriptivo (ej. `Producción Cliente A`) |
| Host | IP o dominio del servidor |
| Puerto SSH | Puerto SSH (default: 22) |
| Usuario SSH | Usuario para conectarse vía SSH |
| Contraseña SSH o Clave privada | Una de las dos opciones |
| Puerto Odoo | Puerto donde corre Odoo (default: 8069) |
| Puerto PostgreSQL | Puerto de la DB (default: 5432) |
| Usuario DB | Usuario de PostgreSQL (default: `postgres`) |
| Contraseña DB | Contraseña de PostgreSQL (opcional, para métricas avanzadas) |
| Tipo / Entorno | `PRODUCTION`, `STAGING` o `DEVELOPMENT` |
| Intervalo | Segundos entre recolecciones (default: 60) |

3. Usar **Probar conexión** para verificar el acceso SSH antes de guardar.

> Las credenciales SSH y de base de datos se almacenan cifradas con Fernet.

### Requerimientos en el servidor remoto

El usuario SSH necesita permisos para ejecutar los siguientes comandos sin contraseña (sudo no requerido):

```bash
cat /proc/stat
cat /proc/meminfo
cat /proc/loadavg
df -P
cat /proc/net/dev
ps aux
cat /sys/class/thermal/thermal_zone*/temp  # temperatura CPU (opcional)
```

Para métricas PostgreSQL, el usuario de DB debe tener acceso a `pg_stat_activity` y `pg_stat_database`.

---

## Dashboard

Muestra un resumen de todos los servidores registrados con:
- Estado de conexión (último `last_seen`)
- CPU, RAM y disco actuales
- Alertas activas

---

## Detalle de servidor

Al hacer clic en un servidor se accede al panel detallado con:

### Métricas en tiempo real
Se actualizan vía WebSocket cada vez que el worker recolecta datos (según el intervalo configurado).

| Sección | Métricas |
|---------|---------|
| Sistema | CPU %, RAM %, swap %, carga 1/5/15 min, disco por partición, red entrada/salida, procesos, temperatura |
| Odoo | Workers activos, procesos colgados, memoria MB, CPU %, tiempo de respuesta ms, requests concurrentes |
| PostgreSQL | Conexiones activas, queries lentas, locks, deadlocks, tamaño DB MB |

### Gráficas históricas
Selector de rango (1h, 6h, 24h, 7d) para ver evolución de métricas Odoo y PostgreSQL.

---

## Alertas

### Crear una regla de alerta

1. Ir a **Alertas** → **Nueva regla**
2. Seleccionar:
   - **Servidor** al que aplica
   - **Métrica** a evaluar (CPU, RAM, disco, conexiones PG, workers Odoo, etc.)
   - **Condición**: `>`, `<`, `>=`, `<=`
   - **Umbral**: valor numérico
   - **Severidad**: `INFO`, `WARNING`, `CRITICAL`
   - **Cooldown**: minutos entre alertas repetidas del mismo tipo

Cuando una métrica supera el umbral, se crea un evento de alerta y se envían notificaciones por los canales configurados.

### Canales de notificación

Ir a **Configuración** → **Canales** para agregar:

| Canal | Configuración requerida |
|-------|------------------------|
| Email | SMTP configurado en `.env` |
| Telegram | `TELEGRAM_BOT_TOKEN` en `.env` + Chat ID |
| Webhook | URL del endpoint receptor |

### Resolver alertas

Los eventos activos aparecen en **Alertas → Eventos**. Cada evento puede marcarse como resuelto manualmente.

---

## Usuarios

Solo los ADMIN pueden gestionar usuarios. Ir a **Configuración** → **Usuarios**:

- **Crear usuario**: email, username, contraseña, rol
- **Editar**: cambiar rol o desactivar cuenta
- **Eliminar**: borra el usuario permanentemente

---

## Seguridad

- Sesión JWT con duración de 8 horas (access token) y 7 días (refresh token)
- Rate limiting: login 5/min, refresh 10/min, test-connection 3/min
- Credenciales SSH y DB cifradas en base de datos (AES-128 Fernet)
- Audit log: todas las acciones CRUD quedan registradas con usuario, IP y timestamp

---

## API

La API REST está disponible en `http://localhost/api/v1/`.

Documentación interactiva (Swagger UI) en `http://localhost/docs` cuando `APP_ENV=development`.

### Autenticación

```bash
# Obtener token
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin1234!"}'

# Usar token
curl http://localhost/api/v1/servers \
  -H "Authorization: Bearer <access_token>"
```

### Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/login` | Obtener tokens |
| POST | `/auth/refresh` | Renovar access token |
| GET | `/servers` | Listar servidores |
| POST | `/servers` | Crear servidor |
| GET | `/servers/{id}` | Detalle de servidor |
| PUT | `/servers/{id}` | Actualizar servidor |
| DELETE | `/servers/{id}` | Eliminar servidor |
| POST | `/servers/{id}/test-connection` | Probar conexión SSH |
| GET | `/servers/{id}/metrics/latest` | Métricas más recientes |
| GET | `/servers/{id}/metrics/history` | Historial de métricas del sistema |
| GET | `/servers/{id}/metrics/odoo/history` | Historial de métricas Odoo |
| GET | `/servers/{id}/metrics/pg/history` | Historial de métricas PostgreSQL |
| GET | `/alerts/rules` | Listar reglas de alerta |
| POST | `/alerts/rules` | Crear regla |
| GET | `/alerts/events` | Listar eventos de alerta |
| GET | `/health` | Estado del servicio |

### WebSocket

```
ws://localhost/ws/metrics/{server_id}?token=<access_token>
```

Recibe mensajes JSON con la estructura:
```json
{
  "type": "metrics",
  "server_id": "uuid",
  "data": {
    "system": { "cpu_usage": {...}, "ram_usage": {...} },
    "odoo": { "workers_active": 4, "memory_mb": 1024, ... },
    "pg": { "connections_active": 12, "db_size_mb": 850, ... }
  }
}
```
