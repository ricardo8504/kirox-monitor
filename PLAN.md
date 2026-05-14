# Plan de Implementación — Odoo Monitor

> **INSTRUCCIÓN PARA CLAUDE:** Al iniciar cada sesión, leer este archivo completo,
> localizar el marcador `→ EN PROGRESO` o el primer paso con estado `[ ]`,
> y continuar desde ahí sin preguntar. Ejecutar, testear, marcar completado `[x]`,
> actualizar `## Estado actual` y continuar con el siguiente paso.
> Nunca saltarse tests. Si un test falla, corregir antes de avanzar.

---

## Estado actual

- **Fase activa:** 14 — Correcciones y mejoras de producción → EN PROGRESO
- **Paso activo:** 14.3 — WebSocket real-time pipeline
- **Último completado:** 14.2 — AlertEngine conectado al pipeline ✓
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

### 0.1 — Inicializar estructura de directorios ✓
- [x] Crear árbol de directorios completo según arquitectura
- [x] Inicializar git repo con `.gitignore` adecuado
- [x] Crear `.env.example` con todas las variables necesarias
- [x] Crear `ROADMAP.md` inicial
- **Verificación:** `ls -la` confirma estructura. `git status` limpio.

### 0.2 — Docker Compose base ✓
- [x] `docker-compose.yml` con servicios: postgres, redis, backend, frontend, nginx
- [x] `docker-compose.dev.yml` con hot-reload para desarrollo
- [x] Volúmenes para persistencia de datos
- [x] Healthchecks en cada servicio
- [x] `Dockerfile` backend: multi-stage, non-root user
- [x] `Dockerfile` frontend: multi-stage, nginx para prod
- [ ] **TEST:** `docker compose -f docker-compose.dev.yml up --build` (pendiente: requiere Docker en CI)
- [ ] **TEST:** `docker compose ps` (pendiente: requiere Docker en CI)

### 0.3 — Backend: pyproject.toml y dependencias ✓
- [x] Crear `backend/pyproject.toml` con todas las dependencias
- [x] Configurar ruff (en pyproject.toml)
- [x] Configurar mypy con plugin pydantic (en pyproject.toml)
- [x] Configurar pytest (en pyproject.toml)
- [x] Configurar black e isort (en pyproject.toml)
- [x] **TEST:** `ruff check app/` → All checks passed
- [x] **TEST:** `mypy app/` → Success: no issues found
- [x] **TEST:** `pytest tests/unit/test_config.py` → 5/5 passed

### 0.4 — Frontend: Vite + React + TypeScript ✓
- [x] `package.json` con todas las dependencias
- [x] Instalar dependencias: axios, zustand, @tanstack/react-query, react-router-dom, tailwindcss, echarts, echarts-for-react, react-grid-layout, lucide-react
- [x] Instalar devDeps: vitest, @testing-library/react, @testing-library/jest-dom, eslint, prettier, @types/node
- [x] Configurar `tailwind.config.ts`
- [x] Configurar `vite.config.ts` con alias `@/` y proxy al backend
- [x] Configurar ESLint + Prettier, `vitest.config.ts` separado
- [x] **TEST:** `npm run build` sin errores ✓
- [x] **TEST:** `npm run test` pasa (0 tests, passWithNoTests: true) ✓
- [x] **TEST:** `npm run lint` sin errores ✓

---

## FASE 1 — Backend: Esqueleto de FastAPI

**Objetivo:** API funcional con health check, configuración, logging y manejo de errores.

### 1.1 — Core: configuración con pydantic-settings ✓
- [x] `app/core/config.py`: clase `Settings` con todas las env vars tipadas
- [x] Variables: DATABASE_URL, REDIS_URL, SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ENCRYPTION_KEY, ALLOWED_ORIGINS, DEBUG, LOG_LEVEL
- [x] Validaciones en Settings (SECRET_KEY mínimo 32 chars, etc.)
- [x] **TEST unitario:** `tests/unit/test_config.py` — 5/5 passed

### 1.2 — Core: logging estructurado ✓
- [x] `app/core/logging.py`: configurar structlog con JSON en prod, formato legible en dev
- [x] Campos mínimos: timestamp, level, message, request_id
- [x] Middleware de request_id (UUID por petición) en `app/core/middleware.py`
- [x] **TEST unitario:** `tests/unit/test_logging.py` — 6/6 passed

### 1.3 — Core: manejo centralizado de excepciones ✓
- [x] `app/core/exceptions.py`: NotFoundError, UnauthorizedError, ForbiddenError, ConflictError, ValidationError, ExternalServiceError
- [x] `app/core/exception_handlers.py`: handlers FastAPI → HTTP consistentes
- [x] Formato: `{"error": {"code": str, "message": str, "details": any}}`
- [x] **TEST unitario:** `tests/unit/test_exceptions.py` — 7/7 passed

### 1.4 — Core: seguridad base ✓
- [x] `app/core/security.py`: hash/verify password (bcrypt), JWT access/refresh tokens
- [x] JWT con exp, iat, sub, role, type
- [x] `app/core/encryption.py`: Fernet encrypt/decrypt para SSH credentials
- [x] **TEST unitario:** `tests/unit/test_security.py` — 11/11 passed

### 1.5 — Database: conexión async SQLAlchemy ✓
- [x] `app/core/database.py`: async engine, AsyncSessionLocal, dependency `get_db`
- [x] `app/models/base.py`: BaseModel con UUID pk, created_at, updated_at
- [x] Alembic inicializado: `alembic/env.py` async, `alembic.ini`, `script.py.mako`
- [ ] **TEST integración:** `tests/integration/test_database.py` — requiere Postgres live (pendiente Docker)

### 1.6 — Main app y health check ✓
- [x] `app/main.py`: FastAPI con lifespan, CORS, exception handlers, routers
- [x] `app/api/v1/health.py`: `GET /api/v1/health` → `{"status": "ok", "version", "db", "env"}`
- [x] Middleware: RequestLoggingMiddleware (request_id, timing, X-Request-ID header)
- [x] **TEST integración:** `tests/integration/test_health.py` — 2/2 passed
- [ ] **TEST:** `docker compose up backend` (pendiente Docker)

---

## FASE 2 — Autenticación y usuarios

**Objetivo:** Sistema completo de auth con JWT, roles y auditoría.

### 2.1 — Modelo User ✓
- [x] `app/models/user.py`: User con UUID pk, email, username, hashed_password, role (StrEnum), is_active, last_login
- [x] Enum `UserRole`: ADMIN, OPERATOR, READONLY
- [x] `app/repositories/user_repository.py`: get_by_id, get_by_email, get_by_username, create, update, delete, list
- [ ] Migración Alembic: tabla `users` (pendiente Docker)

### 2.2 — Modelo AuditLog ✓
- [x] `app/models/audit_log.py`: AuditLog(user_id, action, resource, resource_id, ip_address, user_agent)
- [x] `app/repositories/audit_log_repository.py`: create, list_by_user, list_recent
- [ ] Migración Alembic: tabla `audit_logs` (pendiente Docker)

### 2.3 — Schemas (DTOs) de Auth ✓
- [x] `app/schemas/auth.py`: LoginRequest, TokenResponse, RefreshTokenRequest
- [x] `app/schemas/user.py`: UserCreate, UserUpdate, UserResponse, UserListResponse, ChangePasswordRequest
- [x] **TEST unitario:** `tests/unit/test_auth_schemas.py` — 9/9 passed

### 2.4 — Servicio de autenticación ✓
- [x] `app/services/auth_service.py`: AuthService (login, refresh, get_current_user) + UserService (create, get, change_password, ensure_admin_exists)
- [x] `app/core/deps.py`: get_current_user, require_roles FastAPI dependencies
- [x] **TEST unitario:** `tests/unit/test_auth_service.py` — 9/9 passed

### 2.5 — Endpoints de Auth ✓
- [x] `app/api/v1/auth.py`: POST /login, POST /refresh, GET /me
- [x] `app/api/v1/users.py`: GET /users, POST /users, GET /users/{id} (solo ADMIN)
- [x] **TEST integración (API):** `tests/integration/api/test_auth_api.py` — 6/6 passed

### 2.6 — Rate limiting en auth
- [ ] Integrar `slowapi` con Redis como backend
- [ ] Limit: 5 intentos de login por IP por minuto
- [ ] **TEST integración:** `tests/integration/api/test_rate_limiting.py` — 6 peticiones → 429

---

## FASE 3 — Gestión de servidores

**Objetivo:** CRUD de servidores con validación SSH y almacenamiento seguro de credenciales.

### 3.1 — Modelo Server ✓
- [x] `app/models/server.py`: Server con SSH creds cifradas, ServerType/Environment StrEnums
- [x] `app/repositories/server_repository.py`: CRUD completo + list con filtros

### 3.2 — Schemas de Server ✓
- [x] `app/schemas/server.py`: ServerCreate, ServerUpdate, ServerResponse
- [x] ServerResponse nunca expone credentials

### 3.3 — SSH Manager ✓
- [x] `app/services/ssh_manager.py`: SSHManager con test_connection + execute_command
- [x] CommandResult(stdout, stderr, exit_code)

### 3.4 — Servicio de servidores ✓
- [x] `app/services/server_service.py`: create, update, delete, get, list, validate_connectivity
- [x] Credentials cifradas con Fernet antes de guardar
- [x] **TEST unitario:** `tests/unit/test_server_service.py` ✓

### 3.5 — Endpoints de Server ✓
- [x] `app/api/v1/servers.py`: GET/POST/PATCH/DELETE /servers, GET/POST /servers/{id}/test-connection
- [x] **TEST integración (API):** `tests/integration/api/test_servers_api.py` ✓

---

## FASE 4 — Motor de monitoreo

**Objetivo:** Sistema async que recolecta métricas vía SSH y las almacena.

### 4.1 — Modelos de métricas ✓
- [x] `app/models/metric.py`: Metric, OdooMetric, PgMetric con MetricType StrEnum (13 tipos)
- [x] Índices compuestos (server_id, timestamp)
- [x] `app/repositories/metric_repository.py`: insert_batch, get_latest, get_history

### 4.2 — Collectors: sistema ✓
- [x] `app/services/collectors/system_collector.py`: parsers cpu/ram/disk/load/net/procs/temp
- [x] **TEST unitario:** `tests/unit/collectors/test_system_collector.py` ✓

### 4.3 — Collectors: Odoo ✓
- [x] `app/services/collectors/odoo_collector.py`: workers, response time, db connections
- [x] **TEST unitario:** `tests/unit/collectors/test_odoo_collector.py` ✓

### 4.4 — Collectors: PostgreSQL ✓
- [x] `app/services/collectors/pg_collector.py`: conexiones, locks, slow queries, db size
- [x] **TEST unitario:** `tests/unit/collectors/test_pg_collector.py` ✓

### 4.5 — Monitoring Orchestrator ✓
- [x] `app/services/monitoring_orchestrator.py`: orquesta los 3 collectors, SSH error handling
- [x] **TEST unitario:** `tests/unit/test_monitoring_orchestrator.py` ✓

### 4.6 — Tareas Celery ✓
- [x] `app/workers/celery_app.py`: Redis broker, beat_schedule (60s collect, daily cleanup)
- [x] `app/workers/tasks.py`: collect_metrics, collect_all_servers, cleanup_old_metrics
- [x] **TEST unitario:** `tests/unit/workers/test_tasks.py` ✓ (asyncio mocked)

### 4.7 — Endpoint de métricas ✓
- [x] `app/api/v1/metrics.py`: GET latest, GET history con paginación

---

## FASE 5 — Sistema de alertas

**Objetivo:** Alertas configurables con notificaciones multi-canal y anti-spam.

### 5.1 — Modelos de alertas ✓
- [x] `app/models/alert.py`: AlertRule, AlertEvent, NotificationChannel + StrEnums
- [x] Repositories: alert_rule, alert_event, notification_channel

### 5.2 — Motor de evaluación de alertas ✓
- [x] `app/services/alert_engine.py`: evaluate_rules, cooldown vía Redis SET/TTL
- [x] **TEST unitario:** `tests/unit/test_alert_engine.py` ✓

### 5.3 — Notificaciones ✓
- [x] `app/services/notifications/email_notifier.py`: aiosmtplib
- [x] `app/services/notifications/telegram_notifier.py`: httpx Bot API
- [x] `app/services/notifications/webhook_notifier.py`: httpx POST
- [x] `app/services/notifications/notification_dispatcher.py`
- [x] **TEST unitario:** `tests/unit/notifications/test_*` ✓

### 5.4 — Alertas en collect_metrics ✓
- [x] `collect_metrics` llama `process_alerts` + `publish_metrics` tras guardar

### 5.5 — Endpoints de alertas ✓
- [x] `app/api/v1/alerts.py`: CRUD rules/events/channels, acknowledge, resolve, test channel
- [x] **TEST integración (API):** `tests/integration/api/test_alerts_api.py` ✓

---

## FASE 6 — WebSockets y tiempo real

**Objetivo:** Streaming de métricas en tiempo real al frontend vía WebSockets.

### 6.1 — WebSocket Manager ✓
- [x] `app/core/websocket_manager.py`: ConnectionManager server_id + user_id routing
- [x] **TEST unitario:** `tests/unit/test_websocket_manager.py` — 6/6 ✓

### 6.2 — Endpoints WebSocket ✓
- [x] `app/api/v1/ws.py`: WS /ws/metrics/{server_id} + WS /ws/alerts
- [x] JWT auth por query param `?token=...`, cierre 4001 si inválido

### 6.3 — Publicar métricas vía WebSocket ✓
- [x] `app/workers/ws_publisher.py`: publica a Redis pub/sub `ws:metrics:{server_id}`
- [x] collect_metrics llama publish_metrics tras guardar

---

## FASE 7 — Frontend: Base

**Objetivo:** Aplicación React funcional con auth, routing y componentes base.

### 7.1 — Estructura y configuración ✓
- [x] `src/types/index.ts`: todos los tipos TypeScript (User, Server, Metric, Alert, etc.)
- [x] `src/api/client.ts`: axios instance con interceptor para JWT (auto-refresh + cola de reintentos)
- [x] `src/api/auth.ts`, `servers.ts`, `metrics.ts`, `alerts.ts`: funciones tipadas
- [x] `src/stores/authStore.ts`: Zustand persist store para auth state
- [x] `src/stores/serverStore.ts`: servidores + live metrics

### 7.2 — Layout y Router ✓
- [x] `src/App.tsx`: React Router con rutas protegidas
- [x] Rutas: `/login`, `/dashboard`, `/servers`, `/servers/:id`, `/alerts`, `/settings`
- [x] `src/components/layout/MainLayout.tsx`: sidebar + header + content
- [x] `src/components/layout/Sidebar.tsx`: navegación con iconos (lucide-react)
- [x] `src/components/layout/Header.tsx`: user menu, logout
- [x] `src/components/auth/ProtectedRoute.tsx`: redirige a login si no auth, soporta roles
- [x] `src/hooks/useWebSocket.ts`: hook para WS de métricas y alertas con reconexión

### 7.3 — Página de Login ✓
- [x] `src/pages/LoginPage.tsx`: form con username/password, validación, error handling
- [x] Hook `src/hooks/useAuth.ts`: login, logout, useMe
- [x] Redirect a ruta previa tras login

### 7.4 — Componentes comunes ✓
- [x] `src/components/ui/`: Button, Input, Badge, Spinner, Card, Modal, Table, EmptyState
- [x] Todos tipados, accesibles (aria-*)
- [x] **TEST:** `src/components/ui/__tests__/` — 17 tests pasan ✓

---

## FASE 8 — Frontend: Servidores y métricas básicas

**Objetivo:** CRUD de servidores y visualización de métricas del sistema.

### 8.1 — Lista de servidores ✓
- [x] `src/pages/ServersPage.tsx`: tabla con status badge, acciones (test, delete)
- [x] `src/hooks/useServers.ts`: TanStack Query para listar/crear/editar/borrar servidores
- [x] Status badge: online (verde), offline (rojo), maintenance (amarillo)
- [x] `src/pages/servers/ServerFormModal.tsx`: modal crear servidor

### 8.2 — Formulario de servidor ✓
- [x] `ServerFormModal`: campos name, host, port, ssh_user, ssh_password, type, environment
- [x] `validate_ssh: false` por defecto (no bloquea UI con timeouts SSH)

### 8.3 — Detalle de servidor ✓
- [x] `src/pages/servers/ServerDetailPage.tsx`: vista con gauges CPU/RAM/Disk
- [x] KPI cards: Load 1m/5m, RAM used, process count
- [x] Odoo workers panel, PostgreSQL panel
- [x] Server info section

### 8.4 — Gauge / Métricas en tiempo real ✓
- [x] `src/hooks/useWebSocket.ts`: WS con reconexión automática a 3s
- [x] `src/hooks/useServerMetrics.ts`: REST inicial + WS live updates
- [x] `src/components/metrics/MetricGauge.tsx`: gauge circular con ECharts
- [x] `src/components/metrics/MetricChart.tsx`: línea temporal con ECharts

---

## FASE 9 — Frontend: Dashboard dinámico

**Objetivo:** Dashboard personalizable con widgets arrastrables y gráficas históricas.

### 9.1 — Dashboard engine ✓
- [x] `src/pages/DashboardPage.tsx`: KPI cards + server status + recent alerts + react-grid-layout
- [x] `react-grid-layout` con drag-and-drop de widgets, layout guardado en localStorage
- [x] `src/types/dashboard.ts`: DashboardLayout, WidgetConfig, GridItem, DEFAULT_LAYOUT
- [x] Code splitting: vendor/query/charts/grid chunks (echarts ~1GB gzip 350kB)

### 9.2 — Widgets (básico, en DashboardPage) ✓
- [x] Server Status widget con lista de servidores
- [x] Open Alerts widget con últimas alertas

### 9.3 — Filtros: pendiente (deferred post-Docker)

---

## FASE 10 — Frontend: Alertas y configuración

**Objetivo:** UI completa para gestionar alertas, canales de notificación y configuración del sistema.

### 10.1 — Gestión de alertas ✓
- [x] `src/pages/AlertsPage.tsx`: tabs Events/Rules con tabla completa
- [x] `src/hooks/useAlerts.ts`: TanStack Query para rules, events, channels
- [x] Botones Acknowledge + Resolve en events

### 10.2 — Canales de notificación ✓
- [x] `src/pages/SettingsPage.tsx`: lista de canales + modal crear canal
- [x] Formularios por tipo: Email, Telegram, Webhook
- [x] Botón "Probar canal"

### 10.3 — Gestión de usuarios (deferred)
- [ ] `src/pages/UsersPage.tsx` — pendiente post-Docker

---

## FASE 11 — Docker y despliegue

**Objetivo:** Un solo `docker compose up -d` levanta todo en producción.

### 11.1 — Dockerfiles optimizados ✓
- [x] `backend/Dockerfile`: multi-stage python:3.11-slim, non-root appuser, HEALTHCHECK
- [x] `frontend/Dockerfile`: node:20-alpine → nginx:alpine, HEALTHCHECK
- [x] `backend/Dockerfile.dev`: editable install para hot-reload
- [x] `frontend/Dockerfile.dev`: npm ci, EXPOSE 5173

### 11.2 — docker-compose.yml (producción) ✓
- [x] Servicios: postgres, redis, backend, celery-worker, celery-beat, frontend, nginx
- [x] Networks: backend-net + frontend-net
- [x] Volúmenes: postgres_data, redis_data, backend_logs
- [x] Healthchecks + depends_on service_healthy
- [x] **TEST:** `docker compose config` → OK ✓

### 11.3 — docker-compose.dev.yml ✓
- [x] hot-reload backend (uvicorn --reload), Vite dev server :5173
- [x] Celery Flower :5555
- [x] Volume mounts de código fuente
- [x] **TEST:** `docker compose -f ... -f ... config` → OK ✓

### 11.4 — Nginx ✓
- [x] `nginx/nginx.conf`: API proxy, WebSocket upgrade, frontend, /docs
- [x] Gzip compression, security headers (X-Frame-Options, nosniff, XSS)

### 11.5 — Scripts de inicialización ✓
- [x] `backend/scripts/start.sh`: espera postgres, alembic upgrade head, seed, uvicorn
- [x] `backend/scripts/seed.py`: crea admin desde ADMIN_EMAIL/PASSWORD
- [x] `scripts/wait-for-it.sh`: helper TCP wait

### 11.6 — .env.example completo ✓
- [x] Todas las variables documentadas con comentarios y ejemplos generación de claves

---

## FASE 12 — Documentación y CI básico

**Objetivo:** Documentación actualizada y pipeline CI funcional.

### 12.1 — Actualizar ROADMAP.md ✓
- [x] Estado actual, arquitectura, fases, stack, API endpoints, guía dev, variables

### 12.2 — GitHub Actions CI ✓
- [x] `.github/workflows/backend-ci.yml`: lint (ruff+mypy) + test (pytest con postgres+redis)
- [x] `.github/workflows/frontend-ci.yml`: type-check + lint + vitest + build

### 12.3 — API Docs ✓
- [x] FastAPI genera `/docs` (Swagger) y `/redoc` automáticamente
- [x] Nginx hace proxy de /docs, /redoc, /openapi.json al backend

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

## FASE 14 — Correcciones y mejoras de producción

**Objetivo:** Activar funcionalidad implementada pero no conectada; mejorar visibilidad en producción.

### 14.1 — Actualizar `last_seen` tras cada colección exitosa ✓
- [x] En `monitoring_orchestrator.collect()`, antes de retornar `True`, asignar `server.last_seen = now.isoformat()`
- [x] SQLAlchemy trackea el cambio automáticamente; se persiste en el mismo `session.commit()` del worker
- [x] El campo ya existe en el modelo; no requiere migración
- **Verificación:** Después de un ciclo de colección, `server.last_seen` muestra timestamp reciente en el frontend

### 14.2 — Conectar `AlertEngine` al pipeline de colección ✓
- [x] Añadir parámetro opcional `alert_engine: AlertEngine | None` al constructor de `MonitoringOrchestrator`
- [x] En `collect()`, construir `metrics_snapshot: dict[str, float]` con valores de sistema, Odoo y PG
- [x] Llamar `await self._alert_engine.evaluate_rules(server_id, metrics_snapshot)` si está configurado
- [x] En `tasks.py`, instanciar `AlertEngine` con repos y pasarlo al orquestador
- **Verificación:** Crear regla de alerta con threshold bajo → aparece evento en `/api/v1/alerts/events`

### 14.3 — WebSocket real-time pipeline → EN PROGRESO
- [x] En `monitoring_orchestrator.collect()`, llamar `publish_metrics(server_id, snapshot)` tras guardar
- [x] En `main.py` lifespan, lanzar tarea asyncio que suscribe a `ws:metrics:*` en Redis
- [x] El subscriber llama `ws_manager.broadcast_to_server(server_id, data)` por cada mensaje
- **Verificación:** Abrir detalle de servidor → métricas se actualizan sin recargar durante un ciclo de colección

### 14.4 — Histórico de métricas Odoo y PostgreSQL ✓
- [x] Añadir `get_odoo_range()` y `get_pg_range()` a `MetricRepository`
- [x] Añadir endpoints `GET /servers/{id}/metrics/odoo/history` y `GET /servers/{id}/metrics/pg/history`
- [x] Frontend: añadir `getOdooHistory()` y `getPgHistory()` en `metricsApi`
- [x] Frontend: añadir hooks `useOdooHistory` y `usePgHistory`
- [x] Frontend: añadir sección de gráficas Odoo/PG en `ServerDetailPage`
- **Verificación:** Gráficas de conexiones PG y workers Odoo visibles con datos históricos

### 14.5 — Push a GitHub
- [ ] `git push origin master` (requiere autorización del usuario)

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
