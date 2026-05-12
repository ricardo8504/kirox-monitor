# Plan de Implementación — Odoo Monitor

> **INSTRUCCIÓN PARA CLAUDE:** Al iniciar cada sesión, leer este archivo completo,
> localizar el marcador `→ EN PROGRESO` o el primer paso con estado `[ ]`,
> y continuar desde ahí sin preguntar. Ejecutar, testear, marcar completado `[x]`,
> actualizar `## Estado actual` y continuar con el siguiente paso.
> Nunca saltarse tests. Si un test falla, corregir antes de avanzar.

---

## Estado actual

- **Fase activa:** 0 — Setup inicial
- **Paso activo:** 0.1 — Inicializar estructura de directorios
- **Último completado:** (ninguno)
- **Problemas abiertos:** (ninguno)
- **Decisiones técnicas registradas:** Ver sección al final

---

## Stack tecnológico (decidido)

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + FastAPI |
| ORM | SQLAlchemy 2.0 async + Alembic |
| Validación | Pydantic v2 |
| Auth | JWT (PyJWT) + bcrypt |
| Cifrado secrets | Fernet (cryptography) |
| Queue/Workers | Celery 5 + Redis |
| SSH | paramiko + asyncssh |
| DB | PostgreSQL 15 |
| Cache | Redis 7 |
| Frontend | React 18 + TypeScript + Vite |
| State | Zustand |
| Data fetching | TanStack Query v5 |
| HTTP client | axios |
| Gráficas | Apache ECharts (echarts-for-react) |
| Dashboard drag | react-grid-layout |
| WebSockets | FastAPI WebSockets nativo |
| Estilos | Tailwind CSS v3 |
| Tests backend | pytest + pytest-asyncio + httpx |
| Tests frontend | Vitest + React Testing Library |
| Linter backend | ruff + mypy |
| Formatter | black + isort |
| Linter frontend | ESLint + Prettier |
| Containers | Docker + Docker Compose v2 |
| Proxy | Nginx (producción) |
| Logs | structlog |

---

## Arquitectura del proyecto

```
odoo-monitor/
├── backend/
│   ├── app/
│   │   ├── api/              # Routers FastAPI (v1/)
│   │   ├── core/             # Config, security, logging, exceptions
│   │   ├── domain/           # Entidades puras (sin dependencias)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Acceso a datos (Repository Pattern)
│   │   ├── schemas/          # Pydantic DTOs (request/response)
│   │   ├── services/         # Lógica de negocio
│   │   ├── workers/          # Tareas Celery
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/              # Clientes HTTP tipados
│   │   ├── components/       # Componentes reutilizables
│   │   ├── hooks/            # Custom hooks
│   │   ├── pages/            # Páginas/vistas
│   │   ├── stores/           # Zustand stores
│   │   ├── types/            # TypeScript types/interfaces
│   │   └── utils/
│   ├── tests/
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── package.json
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── init.sh
│   └── seed.py
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── PLAN.md                   # Este archivo
└── ROADMAP.md                # Documento público de avance
```

---

## FASE 0 — Setup del proyecto e infraestructura base

**Objetivo:** Tener la estructura del proyecto, Docker Compose funcional y linters configurados.

### 0.1 — Inicializar estructura de directorios → EN PROGRESO
- [ ] Crear árbol de directorios completo según arquitectura
- [ ] Inicializar git repo con `.gitignore` adecuado
- [ ] Crear `.env.example` con todas las variables necesarias
- [ ] Crear `ROADMAP.md` inicial
- **Verificación:** `ls -la` confirma estructura. `git status` limpio.

### 0.2 — Docker Compose base
- [ ] `docker-compose.yml` con servicios: postgres, redis, backend, frontend, nginx
- [ ] `docker-compose.dev.yml` con hot-reload para desarrollo
- [ ] Volúmenes para persistencia de datos
- [ ] Healthchecks en cada servicio
- [ ] `Dockerfile` backend: multi-stage, non-root user
- [ ] `Dockerfile` frontend: multi-stage, nginx para prod
- [ ] **TEST:** `docker compose -f docker-compose.dev.yml up --build` levanta todos los servicios sin errores
- [ ] **TEST:** `docker compose ps` muestra todos los servicios healthy

### 0.3 — Backend: pyproject.toml y dependencias
- [ ] Crear `backend/pyproject.toml` con todas las dependencias
- [ ] Configurar `ruff.toml` (linter)
- [ ] Configurar `mypy.ini` (tipos)
- [ ] Configurar `pytest.ini` (tests)
- [ ] Configurar `black` y `isort` en pyproject.toml
- [ ] **TEST:** `ruff check .` sin errores
- [ ] **TEST:** `mypy app/` sin errores de configuración
- [ ] **TEST:** `pytest --co -q` lista tests (aunque sean 0)

### 0.4 — Frontend: Vite + React + TypeScript
- [ ] `npm create vite@latest frontend -- --template react-ts`
- [ ] Instalar dependencias: axios, zustand, @tanstack/react-query, react-router-dom, tailwindcss, echarts, echarts-for-react, react-grid-layout, lucide-react
- [ ] Instalar devDeps: vitest, @testing-library/react, @testing-library/jest-dom, eslint, prettier
- [ ] Configurar `tailwind.config.ts`
- [ ] Configurar `vite.config.ts` con alias `@/` y proxy al backend
- [ ] Configurar ESLint + Prettier
- [ ] **TEST:** `npm run build` sin errores
- [ ] **TEST:** `npm run test` pasa (aunque sean 0 tests)
- [ ] **TEST:** `npm run lint` sin errores

---

## FASE 1 — Backend: Esqueleto de FastAPI

**Objetivo:** API funcional con health check, configuración, logging y manejo de errores.

### 1.1 — Core: configuración con pydantic-settings
- [ ] `app/core/config.py`: clase `Settings` con todas las env vars tipadas
- [ ] Variables: DATABASE_URL, REDIS_URL, SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ENCRYPTION_KEY, ALLOWED_ORIGINS, DEBUG, LOG_LEVEL
- [ ] Validaciones en Settings (SECRET_KEY mínimo 32 chars, etc.)
- [ ] **TEST unitario:** `tests/unit/test_config.py` — verifica que Settings carga correctamente con `.env.test`

### 1.2 — Core: logging estructurado
- [ ] `app/core/logging.py`: configurar structlog con JSON en prod, formato legible en dev
- [ ] Campos mínimos: timestamp, level, logger, message, request_id
- [ ] Middleware de request_id (UUID por petición)
- [ ] **TEST unitario:** `tests/unit/test_logging.py` — verifica que logs emiten correctamente

### 1.3 — Core: manejo centralizado de excepciones
- [ ] `app/core/exceptions.py`: excepciones base del dominio (NotFoundError, UnauthorizedError, ConflictError, ValidationError, ExternalServiceError)
- [ ] `app/core/exception_handlers.py`: handlers para FastAPI que mapean excepciones a respuestas HTTP consistentes
- [ ] Formato de error estándar: `{"error": {"code": str, "message": str, "details": any}}`
- [ ] **TEST unitario:** `tests/unit/test_exceptions.py`

### 1.4 — Core: seguridad base
- [ ] `app/core/security.py`: funciones para hash/verify password, crear/verificar JWT
- [ ] Usar `bcrypt` para passwords
- [ ] JWT con exp, iat, sub, role
- [ ] `app/core/encryption.py`: Fernet wrapper para cifrar/descifrar secrets (SSH credentials)
- [ ] **TEST unitario:** `tests/unit/test_security.py` — hash/verify, JWT encode/decode, Fernet encrypt/decrypt

### 1.5 — Database: conexión async SQLAlchemy
- [ ] `app/core/database.py`: async engine, session factory, dependency `get_db`
- [ ] `app/models/base.py`: clase base con `id` (UUID), `created_at`, `updated_at`
- [ ] Alembic inicializado con `env.py` async
- [ ] Primera migración vacía: `alembic upgrade head` funciona
- [ ] **TEST integración:** `tests/integration/test_database.py` — conexión a DB de test, crear tabla, insertar, leer

### 1.6 — Main app y health check
- [ ] `app/main.py`: FastAPI con lifespan, CORS, exception handlers, routers
- [ ] `app/api/v1/health.py`: endpoint `GET /api/v1/health` retorna `{"status": "ok", "version": "...", "db": "ok", "redis": "ok"}`
- [ ] Middleware: request logging, timing
- [ ] **TEST integración:** `tests/integration/test_health.py` — health endpoint retorna 200
- [ ] **TEST:** `docker compose up backend` y `curl localhost:8000/api/v1/health` retorna 200

---

## FASE 2 — Autenticación y usuarios

**Objetivo:** Sistema completo de auth con JWT, roles y auditoría.

### 2.1 — Modelo User
- [ ] `app/models/user.py`: User(id, email, username, hashed_password, role, is_active, last_login, created_at, updated_at)
- [ ] Enum `UserRole`: ADMIN, OPERATOR, READONLY
- [ ] Migración Alembic: tabla `users`
- [ ] `app/repositories/user_repository.py`: get_by_id, get_by_email, get_by_username, create, update, delete, list
- [ ] **TEST unitario:** `tests/unit/test_user_model.py`
- [ ] **TEST integración:** `tests/integration/test_user_repository.py`

### 2.2 — Modelo AuditLog
- [ ] `app/models/audit_log.py`: AuditLog(id, user_id, action, resource, resource_id, ip_address, user_agent, created_at)
- [ ] Migración Alembic: tabla `audit_logs`
- [ ] `app/repositories/audit_log_repository.py`: create, list_by_user, list_recent
- [ ] **TEST integración:** `tests/integration/test_audit_log_repository.py`

### 2.3 — Schemas (DTOs) de Auth
- [ ] `app/schemas/auth.py`: LoginRequest, TokenResponse, RefreshTokenRequest
- [ ] `app/schemas/user.py`: UserCreate, UserUpdate, UserResponse, UserListResponse
- [ ] Validaciones en schemas (email válido, password >= 8 chars, etc.)
- [ ] **TEST unitario:** `tests/unit/test_auth_schemas.py`

### 2.4 — Servicio de autenticación
- [ ] `app/services/auth_service.py`: login(email, password) → tokens, refresh_token, logout, get_current_user
- [ ] Seed inicial: crear usuario admin en primera ejecución si no existe
- [ ] `app/services/user_service.py`: create_user, update_user, delete_user, list_users, change_password
- [ ] **TEST unitario:** `tests/unit/test_auth_service.py` — mock repository
- [ ] **TEST integración:** `tests/integration/test_auth_service.py` — DB real de test

### 2.5 — Endpoints de Auth
- [ ] `app/api/v1/auth.py`: POST /login, POST /refresh, POST /logout, GET /me
- [ ] `app/api/v1/users.py`: CRUD de usuarios (solo ADMIN)
- [ ] Dependency `get_current_user`, `require_role(roles: list[UserRole])`
- [ ] Registrar en audit_log cada login, logout, acceso fallido
- [ ] **TEST integración (API):** `tests/integration/api/test_auth_api.py`
  - Login correcto → 200 + tokens
  - Login incorrecto → 401
  - Token expirado → 401
  - Refresh token → nuevos tokens
  - GET /me sin token → 401
  - CRUD usuarios sin rol ADMIN → 403
- [ ] **TEST E2E manual:** `curl` de cada endpoint

### 2.6 — Rate limiting en auth
- [ ] Integrar `slowapi` con Redis como backend
- [ ] Limit: 5 intentos de login por IP por minuto
- [ ] **TEST integración:** `tests/integration/api/test_rate_limiting.py` — 6 peticiones → 429

---

## FASE 3 — Gestión de servidores

**Objetivo:** CRUD de servidores con validación SSH y almacenamiento seguro de credenciales.

### 3.1 — Modelo Server
- [ ] `app/models/server.py`: Server(id, name, host, port, ssh_user, ssh_password_encrypted, ssh_key_encrypted, server_type, environment, monitoring_interval, is_active, last_seen, created_by, created_at, updated_at)
- [ ] Enum `ServerType`: PRODUCTION, STAGING, DEVELOPMENT
- [ ] Enum `Environment`: igual
- [ ] Migración Alembic: tabla `servers`
- [ ] `app/repositories/server_repository.py`: CRUD completo + list con filtros
- [ ] **TEST integración:** `tests/integration/test_server_repository.py`

### 3.2 — Schemas de Server
- [ ] `app/schemas/server.py`: ServerCreate, ServerUpdate, ServerResponse, ServerListResponse
- [ ] `ServerCreate` incluye: ssh_password o ssh_key (al menos uno), validación de IP/dominio, puerto 1-65535
- [ ] `ServerResponse` NUNCA expone credentials (solo máscara)
- [ ] **TEST unitario:** `tests/unit/test_server_schemas.py`

### 3.3 — SSH Manager
- [ ] `app/services/ssh_manager.py`: clase SSHManager con:
  - `test_connection(host, port, user, password=None, key=None) → bool`
  - `execute_command(server, command) → (stdout, stderr, exit_code)`
  - Pool de conexiones por servidor
  - Timeout configurable (default 10s)
  - Manejo de errores: host down, auth failed, timeout
- [ ] **TEST unitario:** `tests/unit/test_ssh_manager.py` — mocks de paramiko
- [ ] **TEST integración (opcional):** contra servidor local si disponible

### 3.4 — Servicio de servidores
- [ ] `app/services/server_service.py`: create, update, delete, get, list, validate_connectivity
- [ ] Al crear/actualizar: cifrar credentials con Fernet antes de guardar
- [ ] Validar conectividad SSH antes de guardar (timeout 15s)
- [ ] **TEST unitario:** `tests/unit/test_server_service.py`
- [ ] **TEST integración:** `tests/integration/test_server_service.py`

### 3.5 — Endpoints de Server
- [ ] `app/api/v1/servers.py`:
  - `GET /servers` (ADMIN, OPERATOR, READONLY)
  - `POST /servers` (ADMIN, OPERATOR)
  - `GET /servers/{id}` (todos)
  - `PUT /servers/{id}` (ADMIN, OPERATOR)
  - `DELETE /servers/{id}` (ADMIN)
  - `POST /servers/{id}/test-connection` (ADMIN, OPERATOR)
- [ ] **TEST integración (API):** `tests/integration/api/test_servers_api.py`
  - CRUD completo con roles correctos
  - 403 con rol incorrecto
  - 404 para servidor inexistente
  - Credentials nunca en response
  - test-connection retorna status

---

## FASE 4 — Motor de monitoreo

**Objetivo:** Sistema async que recolecta métricas vía SSH y las almacena.

### 4.1 — Modelos de métricas
- [ ] `app/models/metric.py`: Metric(id, server_id, metric_type, value, unit, timestamp, raw_data JSON)
- [ ] Enum `MetricType`: CPU_USAGE, RAM_USAGE, SWAP_USAGE, DISK_USAGE, DISK_IO, LOAD_AVERAGE, NETWORK_IO, PROCESS_COUNT, etc. (lista completa del contexto.txt)
- [ ] `app/models/odoo_metric.py`: OdooMetric(server_id, workers_active, processes_hung, memory_mb, cpu_percent, response_time_ms, requests_concurrent, timestamp)
- [ ] `app/models/pg_metric.py`: PgMetric(server_id, connections_active, slow_queries, locks, deadlocks, timestamp)
- [ ] Migraciones Alembic para las 3 tablas
- [ ] Índices: (server_id, timestamp) para queries de series de tiempo
- [ ] `app/repositories/metric_repository.py`: insert_batch, get_latest, get_range(server_id, metric_type, from, to)
- [ ] **TEST integración:** `tests/integration/test_metric_repository.py`

### 4.2 — Collectors: métricas del sistema
- [ ] `app/services/collectors/system_collector.py`
- [ ] Comandos SSH a ejecutar:
  ```
  CPU:     top -bn1 | grep "Cpu(s)"  ó  mpstat 1 1
  RAM:     free -m
  SWAP:    free -m
  Disk:    df -h
  DiskIO:  iostat -x 1 1
  Load:    uptime ó cat /proc/loadavg
  Network: cat /proc/net/dev
  Temp:    cat /sys/class/thermal/thermal_zone*/temp (si existe)
  Procs:   ps aux --no-headers | wc -l
  ```
- [ ] Parser para cada comando → `SystemMetrics` dataclass
- [ ] Manejo de errores: comando no disponible → None, no falla el ciclo
- [ ] **TEST unitario:** `tests/unit/collectors/test_system_collector.py`
  - Test de parsers con output de comandos reales (fixtures)
  - Verificar que outputs malformados no crashean

### 4.3 — Collectors: métricas de Odoo
- [ ] `app/services/collectors/odoo_collector.py`
- [ ] Comandos:
  ```
  Procesos: ps aux | grep openerp-server ó odoo
  Workers:  ps aux | grep worker
  Colgados: ps aux | grep -v grep | grep odoo | awk tiempo_cpu
  Memoria:  ps aux | grep odoo | awk '{sum+=$6} END {print sum}'
  HTTP resp: curl -s -o /dev/null -w "%{time_total}" localhost:8069
  Logs:     tail -n 100 /var/log/odoo/*.log | grep -i 'error\|critical'
  ```
- [ ] Parser → `OdooMetrics` dataclass
- [ ] **TEST unitario:** `tests/unit/collectors/test_odoo_collector.py`

### 4.4 — Collectors: métricas PostgreSQL
- [ ] `app/services/collectors/pg_collector.py`
- [ ] Conexión directa vía SSH tunnel o psycopg2 remoto (configurar por servidor)
- [ ] Queries SQL:
  ```sql
  -- Conexiones activas
  SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
  -- Slow queries (>5s)
  SELECT pid, now()-pg_stat_activity.query_start AS duration, query
  FROM pg_stat_activity WHERE state = 'active' AND now()-pg_stat_activity.query_start > interval '5 seconds';
  -- Locks
  SELECT count(*) FROM pg_locks WHERE NOT granted;
  -- Deadlocks
  SELECT deadlocks FROM pg_stat_database WHERE datname = current_database();
  -- DB size
  SELECT pg_size_pretty(pg_database_size(current_database()));
  ```
- [ ] Ejecutar vía SSH: `psql -U postgres -c "..."` o tunnel
- [ ] **TEST unitario:** `tests/unit/collectors/test_pg_collector.py`

### 4.5 — Monitoring Orchestrator
- [ ] `app/services/monitoring_orchestrator.py`: orquesta los 3 collectors para un servidor
- [ ] Maneja timeouts: si SSH falla → marcar servidor como offline, guardar evento
- [ ] Guarda métricas en batch para eficiencia
- [ ] **TEST unitario:** `tests/unit/test_monitoring_orchestrator.py`

### 4.6 — Tareas Celery
- [ ] `app/workers/celery_app.py`: configuración Celery con Redis
- [ ] `app/workers/tasks.py`:
  - `collect_metrics(server_id)`: recolectar y guardar métricas de un servidor
  - `collect_all_servers()`: iterar sobre servidores activos y encolar collect_metrics
  - `cleanup_old_metrics()`: purgar métricas > 90 días
- [ ] Beat schedule: `collect_all_servers` cada 60s (configurable), `cleanup_old_metrics` diario
- [ ] Celery flower para monitoreo del worker (en docker-compose.dev.yml)
- [ ] **TEST unitario:** `tests/unit/workers/test_tasks.py` — mocks de collectors y repository
- [ ] **TEST integración:** `tests/integration/workers/test_celery_tasks.py` — con Redis real

### 4.7 — Endpoint de métricas
- [ ] `app/api/v1/metrics.py`:
  - `GET /servers/{id}/metrics/latest` → últimas métricas de cada tipo
  - `GET /servers/{id}/metrics/history?metric=CPU_USAGE&from=...&to=...` → serie temporal
  - `GET /servers/{id}/metrics/odoo/latest`
  - `GET /servers/{id}/metrics/pg/latest`
- [ ] **TEST integración (API):** `tests/integration/api/test_metrics_api.py`

---

## FASE 5 — Sistema de alertas

**Objetivo:** Alertas configurables con notificaciones multi-canal y anti-spam.

### 5.1 — Modelos de alertas
- [ ] `app/models/alert_rule.py`: AlertRule(id, server_id, metric_type, condition, threshold, severity, enabled, cooldown_minutes, created_by, created_at)
- [ ] Enum `AlertSeverity`: INFO, WARNING, CRITICAL
- [ ] Enum `AlertCondition`: GREATER_THAN, LESS_THAN, EQUALS
- [ ] `app/models/alert_event.py`: AlertEvent(id, rule_id, server_id, message, severity, metric_value, notified_at, resolved_at)
- [ ] `app/models/notification_channel.py`: NotificationChannel(id, type, config_encrypted, user_id, enabled)
- [ ] Enum `ChannelType`: EMAIL, TELEGRAM, WEBHOOK
- [ ] Migraciones Alembic para las 3 tablas
- [ ] Repositories para las 3 entidades
- [ ] **TEST integración:** repositories

### 5.2 — Motor de evaluación de alertas
- [ ] `app/services/alert_engine.py`:
  - `evaluate_rules(server_id, metrics)`: evaluar reglas contra métricas actuales
  - `should_notify(rule_id, alert_event)`: respetar cooldown con Redis
  - `create_alert_event(rule, metric_value)`: crear evento y encolar notificación
- [ ] **TEST unitario:** `tests/unit/test_alert_engine.py`
  - threshold GREATER_THAN con valor sobre y bajo umbral
  - cooldown respetado (no duplicar alertas)
  - alertas resueltas automáticamente

### 5.3 — Notificaciones
- [ ] `app/services/notifications/email_notifier.py`: SMTP con aiosmtplib, template HTML
- [ ] `app/services/notifications/telegram_notifier.py`: Bot API con httpx
- [ ] `app/services/notifications/webhook_notifier.py`: POST a URL con payload JSON
- [ ] `app/services/notifications/notification_dispatcher.py`: despacha a todos los canales configurados del usuario
- [ ] **TEST unitario:** `tests/unit/notifications/test_*` — mocks de SMTP y HTTP

### 5.4 — Tarea Celery para alertas
- [ ] `app/workers/tasks.py`: agregar `process_alerts(server_id, metrics_snapshot)`
- [ ] Se llama desde `collect_metrics` después de guardar métricas
- [ ] **TEST unitario:** `tests/unit/workers/test_alert_task.py`

### 5.5 — Endpoints de alertas
- [ ] `app/api/v1/alerts.py`:
  - CRUD de `AlertRule`
  - `GET /alerts/events` — historial de alertas
  - `POST /alerts/events/{id}/resolve`
  - CRUD de `NotificationChannel` (config se cifra automáticamente)
  - `POST /notifications/test` — enviar notificación de prueba
- [ ] **TEST integración (API):** `tests/integration/api/test_alerts_api.py`

---

## FASE 6 — WebSockets y tiempo real

**Objetivo:** Streaming de métricas en tiempo real al frontend vía WebSockets.

### 6.1 — WebSocket Manager
- [ ] `app/core/websocket_manager.py`: ConnectionManager con:
  - `connect(websocket, server_id, user_id)`
  - `disconnect(websocket)`
  - `broadcast_to_server(server_id, data)`
  - `broadcast_to_user(user_id, data)`
  - Manejo de conexiones muertas (ping/pong)
- [ ] **TEST unitario:** `tests/unit/test_websocket_manager.py`

### 6.2 — Endpoints WebSocket
- [ ] `app/api/v1/ws.py`:
  - `WS /ws/metrics/{server_id}` — stream de métricas en tiempo real (auth por query param token)
  - `WS /ws/alerts` — notificaciones de alertas
- [ ] Auth: validar JWT del query param `?token=...`
- [ ] **TEST integración:** `tests/integration/test_websockets.py` — con httpx WebSocket client

### 6.3 — Publicar métricas vía WebSocket
- [ ] En `collect_metrics` task: después de guardar, publicar vía Redis pub/sub
- [ ] `app/workers/ws_publisher.py`: suscribirse a Redis pub/sub y hacer broadcast a WebSocket connections
- [ ] **TEST integración:** métricas fluyen de Celery → Redis → WebSocket

---

## FASE 7 — Frontend: Base

**Objetivo:** Aplicación React funcional con auth, routing y componentes base.

### 7.1 — Estructura y configuración
- [ ] `src/types/index.ts`: todos los tipos TypeScript (User, Server, Metric, Alert, etc.) alineados con schemas del backend
- [ ] `src/api/client.ts`: axios instance con interceptor para JWT (auto-refresh)
- [ ] `src/api/auth.ts`, `servers.ts`, `metrics.ts`, `alerts.ts`: funciones tipadas para cada endpoint
- [ ] `src/stores/authStore.ts`: Zustand store para auth state (user, token, login, logout)
- [ ] `src/stores/serverStore.ts`: servidores seleccionados, estado
- [ ] **TEST:** `tests/api/test_client.ts` — interceptor agrega Bearer token

### 7.2 — Layout y Router
- [ ] `src/App.tsx`: React Router con rutas protegidas
- [ ] Rutas: `/login`, `/dashboard`, `/servers`, `/servers/:id`, `/alerts`, `/settings`, `/users`
- [ ] `src/components/layout/MainLayout.tsx`: sidebar + header + content
- [ ] `src/components/layout/Sidebar.tsx`: navegación con iconos (lucide-react)
- [ ] `src/components/layout/Header.tsx`: user menu, notificaciones badge
- [ ] `src/components/common/ProtectedRoute.tsx`: redirige a login si no auth
- [ ] `src/components/common/RoleGuard.tsx`: oculta UI por rol
- [ ] **TEST:** `tests/components/layout/` — renders, navegación, protección de rutas

### 7.3 — Página de Login
- [ ] `src/pages/Login.tsx`: form con email/password, validación, error handling
- [ ] Hook `useAuth`: wraps authStore con lógica de login/logout
- [ ] Redirect a `/dashboard` si ya autenticado
- [ ] **TEST:** `tests/pages/test_login.tsx` — submit form, error display, redirect

### 7.4 — Componentes comunes
- [ ] `src/components/common/`: Button, Input, Select, Modal, Table, Badge, Spinner, Alert, Card, Tooltip, EmptyState
- [ ] Todos tipados, accesibles (aria-*), testables
- [ ] **TEST:** `tests/components/common/` — render + interactions básicas

---

## FASE 8 — Frontend: Servidores y métricas básicas

**Objetivo:** CRUD de servidores y visualización de métricas del sistema.

### 8.1 — Lista de servidores
- [ ] `src/pages/Servers/ServerList.tsx`: tabla con status badge, acciones por rol
- [ ] `src/hooks/useServers.ts`: TanStack Query para listar/invalidar servidores
- [ ] Status badge: online (verde), offline (rojo), warning (amarillo)
- [ ] **TEST:** `tests/pages/servers/test_server_list.tsx`

### 8.2 — Formulario de servidor
- [ ] `src/pages/Servers/ServerForm.tsx`: crear/editar servidor
- [ ] Campos: name, host, port, ssh_user, auth method (password/key), type, environment, interval
- [ ] Botón "Probar conexión" → llama test-connection API
- [ ] Validación en cliente y display de errores del servidor
- [ ] **TEST:** `tests/pages/servers/test_server_form.tsx`

### 8.3 — Detalle de servidor
- [ ] `src/pages/Servers/ServerDetail.tsx`: vista principal del servidor
- [ ] Tabs: Overview, Odoo, PostgreSQL, Alerts, Logs
- [ ] Overview: métricas actuales en KPI cards (CPU, RAM, Disco, Load)
- [ ] **TEST:** `tests/pages/servers/test_server_detail.tsx`

### 8.4 — Gauge / Métricas en tiempo real
- [ ] `src/hooks/useWebSocket.ts`: hook que gestiona conexión WS, reconexión automática
- [ ] `src/hooks/useServerMetrics.ts`: combina REST (inicial) + WebSocket (updates)
- [ ] `src/components/metrics/MetricGauge.tsx`: gauge circular con ECharts (CPU%, RAM%, Disco%)
- [ ] `src/components/metrics/MetricChart.tsx`: línea temporal con ECharts
- [ ] Actualización en tiempo real sin re-render innecesario
- [ ] **TEST:** `tests/components/metrics/` — renders con datos mock

---

## FASE 9 — Frontend: Dashboard dinámico

**Objetivo:** Dashboard personalizable con widgets arrastrables y gráficas históricas.

### 9.1 — Dashboard engine
- [ ] `src/pages/Dashboard/DashboardPage.tsx`: página principal
- [ ] `react-grid-layout` para drag-and-drop de widgets
- [ ] Layout guardado en localStorage y/o backend por usuario
- [ ] `src/types/dashboard.ts`: DashboardLayout, Widget, WidgetType
- [ ] **TEST:** `tests/pages/dashboard/test_dashboard_page.tsx`

### 9.2 — Widgets
- [ ] `src/components/widgets/CpuWidget.tsx`: gráfica de línea CPU% últimas 24h
- [ ] `src/components/widgets/RamWidget.tsx`: área RAM% + SWAP
- [ ] `src/components/widgets/DiskWidget.tsx`: barras por partición
- [ ] `src/components/widgets/LoadWidget.tsx`: línea de load average
- [ ] `src/components/widgets/OdooWidget.tsx`: workers, procesos, response time
- [ ] `src/components/widgets/PgWidget.tsx`: conexiones, locks, slow queries
- [ ] `src/components/widgets/AlertsWidget.tsx`: últimas alertas activas
- [ ] `src/components/widgets/ServerStatusWidget.tsx`: grid de servidores con status
- [ ] Cada widget: configuración de rango de tiempo, título editable
- [ ] **TEST:** `tests/components/widgets/` — render con datos mock

### 9.3 — Filtros y exportación
- [ ] `src/components/dashboard/DateRangePicker.tsx`: selector de rango temporal
- [ ] `src/components/dashboard/ExportButton.tsx`: exportar CSV/JSON de métricas seleccionadas
- [ ] **TEST:** componentes individuales

---

## FASE 10 — Frontend: Alertas y configuración

**Objetivo:** UI completa para gestionar alertas, canales de notificación y configuración del sistema.

### 10.1 — Gestión de alertas
- [ ] `src/pages/Alerts/AlertRuleList.tsx`: lista de reglas por servidor
- [ ] `src/pages/Alerts/AlertRuleForm.tsx`: crear/editar regla (servidor, métrica, condición, umbral, severidad, cooldown)
- [ ] `src/pages/Alerts/AlertEventList.tsx`: historial con filtros y botón resolver
- [ ] `src/hooks/useAlerts.ts`
- [ ] **TEST:** `tests/pages/alerts/`

### 10.2 — Canales de notificación
- [ ] `src/pages/Settings/NotificationChannels.tsx`: listar/crear canales
- [ ] Formularios por tipo: Email (SMTP config), Telegram (bot token + chat_id), Webhook (URL + headers)
- [ ] Botón "Probar canal"
- [ ] **TEST:** `tests/pages/settings/test_notification_channels.tsx`

### 10.3 — Gestión de usuarios
- [ ] `src/pages/Users/UserList.tsx`: solo visible para ADMIN
- [ ] `src/pages/Users/UserForm.tsx`: crear/editar usuario, asignar rol
- [ ] `src/pages/Profile/ProfilePage.tsx`: cambiar password, configuración personal
- [ ] **TEST:** `tests/pages/users/`

---

## FASE 11 — Docker y despliegue

**Objetivo:** Un solo `docker compose up -d` levanta todo en producción.

### 11.1 — Dockerfiles optimizados
- [ ] `backend/Dockerfile`:
  - Multi-stage: build → runtime
  - Base: `python:3.11-slim`
  - Non-root user `appuser`
  - `pip install --no-cache-dir`
  - HEALTHCHECK incluido
- [ ] `frontend/Dockerfile`:
  - Multi-stage: `node:20-alpine` build → `nginx:alpine` runtime
  - Build optimizado con cache de layers
- [ ] **TEST:** `docker build -t backend-test backend/` sin errores
- [ ] **TEST:** `docker build -t frontend-test frontend/` sin errores

### 11.2 — docker-compose.yml (producción)
- [ ] Servicios: `postgres`, `redis`, `backend`, `celery-worker`, `celery-beat`, `frontend`, `nginx`
- [ ] Networks: `backend-net` (backend↔postgres↔redis), `frontend-net` (nginx↔frontend↔backend)
- [ ] Volúmenes nombrados: `postgres_data`, `redis_data`, `backend_logs`
- [ ] Variables de entorno: todas desde `.env`
- [ ] Restart policy: `unless-stopped`
- [ ] Healthchecks: todos los servicios
- [ ] Dependencias correctas con `depends_on: condition: service_healthy`
- [ ] **TEST:** `docker compose config` sin errores
- [ ] **TEST:** `docker compose up -d` levanta todos los servicios

### 11.3 — docker-compose.dev.yml
- [ ] Override para desarrollo: hot-reload backend (`uvicorn --reload`), Vite dev server
- [ ] Celery Flower en puerto 5555
- [ ] Mounts de código fuente
- [ ] Puertos expuestos para debug

### 11.4 — Nginx
- [ ] `nginx/nginx.conf`: proxy pass a backend (API + WebSocket), servir frontend estático
- [ ] WebSocket upgrade headers correctos
- [ ] Gzip compression
- [ ] Security headers (X-Frame-Options, CSP básico)

### 11.5 — Scripts de inicialización
- [ ] `scripts/init.sh`: espera a que postgres esté ready, corre `alembic upgrade head`, corre seed
- [ ] `scripts/seed.py`: crea usuario admin desde variables de entorno (ADMIN_EMAIL, ADMIN_PASSWORD)
- [ ] El backend ejecuta init.sh en su CMD antes de iniciar uvicorn
- [ ] **TEST:** contenedor fresh arranca sin intervención manual

### 11.6 — .env.example completo
- [ ] Documentar todas las variables con comentarios y valores de ejemplo
- [ ] `.env.test` para tests de integración
- [ ] **Verificación final:** clonar repo en directorio limpio, copiar .env.example a .env, `docker compose up -d`, esperar 30s, `curl localhost/api/v1/health` → 200

---

## FASE 12 — Documentación y CI básico

**Objetivo:** Documentación actualizada y pipeline CI funcional.

### 12.1 — Actualizar ROADMAP.md
- [ ] Sección "Estado actual" con qué funciona
- [ ] Sección "Arquitectura" con diagrama ASCII
- [ ] Sección "Guía rápida de desarrollo"
- [ ] Sección "Variables de entorno" explicadas
- [ ] Sección "API Docs" (FastAPI autogenera en /docs)

### 12.2 — GitHub Actions CI
- [ ] `.github/workflows/backend-ci.yml`:
  - trigger: push/PR a main
  - jobs: lint (ruff, mypy), test (pytest con postgres+redis services)
  - Cache de pip
- [ ] `.github/workflows/frontend-ci.yml`:
  - jobs: lint (eslint), type-check (tsc), test (vitest), build
  - Cache de npm
- [ ] **TEST:** workflow se ejecuta sin errores (si hay repo en GitHub)

### 12.3 — API Docs
- [ ] FastAPI genera `/docs` (Swagger) y `/redoc` automáticamente
- [ ] Asegurar que todos los endpoints tienen docstrings y response_model
- [ ] Tags correctos en routers para organización

---

## FASE 13 — Extras de alto valor

**Objetivo:** Funcionalidades adicionales que elevan el producto significativamente.

### 13.1 — Integración Prometheus/Grafana (opcional)
- [ ] Endpoint `GET /metrics` en formato Prometheus (prometheus-fastapi-instrumentator)
- [ ] Agregar Grafana + Prometheus al docker-compose.yml
- [ ] Dashboard básico de Grafana importable

### 13.2 — Detección de anomalías básica
- [ ] Algoritmo simple: si valor actual > media de últimas 2h + 2*stddev → anomaly flag
- [ ] Implementar en `app/services/anomaly_detector.py`
- [ ] Guardar en `MetricEvent` con type=ANOMALY
- [ ] Mostrar en frontend como badge especial

### 13.3 — Health checks automáticos HTTP
- [ ] `app/services/collectors/http_checker.py`: GET a URL de Odoo, medir tiempo de respuesta
- [ ] Config por servidor: URL a checkear, timeout, expected status code
- [ ] Si no responde → alerta automática tipo "Odoo HTTP unreachable"

### 13.4 — Exportación de reportes
- [ ] Endpoint `GET /servers/{id}/report?from=...&to=...&format=csv|json`
- [ ] Exportar serie temporal completa de métricas en el rango solicitado

### 13.5 — API pública documentada
- [ ] API key de solo lectura para integrar con otros sistemas
- [ ] Modelo ApiKey en DB, endpoints de gestión
- [ ] Auth middleware que acepta Bearer JWT O X-API-Key header

---

## Checklist de verificación por fase

Antes de marcar una fase como COMPLETA, verificar:

- [ ] Todos los tests de la fase pasan (`pytest -v` o `vitest`)
- [ ] No hay regresiones en tests anteriores
- [ ] `ruff check .` sin errores (backend)
- [ ] `mypy app/` sin errores de tipo (backend)
- [ ] `npm run type-check` sin errores (frontend)
- [ ] `npm run lint` sin errores (frontend)
- [ ] Docker Compose levanta sin errores
- [ ] Health endpoint responde 200
- [ ] ROADMAP.md actualizado con el avance

---

## Decisiones técnicas

| Decisión | Alternativa rechazada | Motivo |
|----------|----------------------|--------|
| FastAPI | Django REST, Flask | Async nativo, tipado, performance |
| SQLAlchemy 2.0 async | Tortoise ORM | Madurez, ecosystem, soporte Alembic |
| Celery + Redis | APScheduler, RQ | Escalabilidad, retry policies, monitoring |
| Fernet para SSH keys | AES manual | Librería probada, wrapper simple |
| Zustand | Redux, Jotai | Mínimo boilerplate, TypeScript perfecto |
| TanStack Query | SWR, react-query v3 | Cache, invalidation, deduplication |
| ECharts | Recharts, D3 | Performance con grandes datasets |
| react-grid-layout | dnd-kit custom | Maduro, cases de uso exactos |

---

## Cómo continuar en una nueva sesión

1. Claude lee este archivo completo
2. Lee `ROADMAP.md` para estado actual
3. Localiza `→ EN PROGRESO` o primer `[ ]`
4. Ejecuta el paso
5. Corre los tests especificados
6. Si pasan: marca `[x]` el paso, actualiza `## Estado actual` arriba
7. Si fallan: corrige hasta que pasen, luego avanza
8. Al terminar cada FASE: actualiza `ROADMAP.md`
9. Continúa con el siguiente paso sin esperar
