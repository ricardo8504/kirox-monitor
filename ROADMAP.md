# Odoo Monitor — Roadmap

## Estado actual

**Fase activa:** 11 — Docker y despliegue  
**Backend:** Fases 0-6 completas · 117 tests · ruff OK · mypy OK  
**Frontend:** Fases 7-10 completas · 17 tests · build OK · lint OK  
**Inicio:** 2026-05-12  
**Última actualización:** 2026-05-13

---

## Resumen del sistema

Sistema de monitoreo y administración de servidores Odoo.
Permite configurar múltiples servidores remotos y monitorear en tiempo real métricas del
sistema operativo, procesos Odoo y base de datos PostgreSQL, con alertas configurables
y notificaciones multi-canal (Email, Telegram, Webhook).

---

## Arquitectura

```
Browser ←→ Nginx :80 ←→ Frontend (React 18 + Vite + Tailwind)
                    ↕
              FastAPI :8000
                    ↕ WebSocket + REST
       ┌────────────┴────────────┐
       │                         │
    PostgreSQL 15           Redis 7
       │                         │
       └────────────┬────────────┘
                    │
             Celery Workers
             Celery Beat
             (monitoreo SSH)
```

**Flujo de métricas:**
`Beat` → `collect_metrics` → `SSH → server` → parsers → `PostgreSQL` → `API/WS`

**Flujo de alertas:**
`collect_metrics` → `AlertEngine` → `Redis cooldown` → `NotificationDispatcher` → `Email/Telegram/Webhook`

---

## Fases de desarrollo

| # | Fase | Estado | Tests |
|---|------|--------|-------|
| 0 | Setup del proyecto e infraestructura | ✅ Completo | — |
| 1 | Backend: Esqueleto FastAPI | ✅ Completo | 13 tests |
| 2 | Autenticación y usuarios | ✅ Completo | 24 tests |
| 3 | Gestión de servidores | ✅ Completo | 18 tests |
| 4 | Motor de monitoreo (SSH + collectors) | ✅ Completo | 38 tests |
| 5 | Sistema de alertas | ✅ Completo | 18 tests |
| 6 | WebSockets y tiempo real | ✅ Completo | 6 tests |
| 7 | Frontend: Base (tipos, API, stores, layout) | ✅ Completo | 17 tests |
| 8 | Frontend: Servidores y métricas | ✅ Completo | — |
| 9 | Frontend: Dashboard dinámico | ✅ Completo | — |
| 10 | Frontend: Alertas y configuración | ✅ Completo | — |
| 11 | Docker y despliegue | 🔄 En progreso | — |
| 12 | Documentación y CI | 🔄 En progreso | — |
| 13 | Extras (Prometheus, anomalías, reports) | ⏳ Pendiente | — |

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | Python + FastAPI | 3.12 / 0.115 |
| ORM | SQLAlchemy async + Alembic | 2.0 |
| Auth | JWT (PyJWT) + bcrypt | — |
| Cifrado | Fernet (cryptography) | — |
| Queue | Celery 5 + Redis | 7 |
| SSH | paramiko | — |
| BD | PostgreSQL | 15 |
| Cache | Redis | 7 |
| Frontend | React 18 + TypeScript + Vite | 18 / 5.7 / 6.0 |
| Estado | Zustand | 5.0 |
| Fetching | TanStack Query | v5 |
| Gráficas | Apache ECharts | 5.5 |
| Dashboard | react-grid-layout | — |
| Estilos | Tailwind CSS | 3.4 |
| Proxy | Nginx | alpine |
| Logs | structlog | — |
| Tests BE | pytest + pytest-asyncio + httpx | — |
| Tests FE | Vitest + React Testing Library | 2.1 |

---

## API Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/login` | No | Login → tokens |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| GET | `/api/v1/auth/me` | JWT | Usuario actual |
| GET | `/api/v1/users` | ADMIN | Listar usuarios |
| POST | `/api/v1/users` | ADMIN | Crear usuario |
| GET | `/api/v1/servers` | Todos | Listar servidores |
| POST | `/api/v1/servers` | OPERATOR+ | Crear servidor |
| GET | `/api/v1/servers/{id}` | Todos | Detalle servidor |
| PATCH | `/api/v1/servers/{id}` | OPERATOR+ | Actualizar servidor |
| DELETE | `/api/v1/servers/{id}` | ADMIN | Eliminar servidor |
| POST | `/api/v1/servers/{id}/test-connection` | OPERATOR+ | Probar SSH |
| GET | `/api/v1/metrics/{id}/latest` | Todos | Métricas recientes |
| GET | `/api/v1/metrics/{id}/history` | Todos | Historial de métricas |
| GET | `/api/v1/alerts/rules` | Todos | Listar reglas |
| POST | `/api/v1/alerts/rules` | OPERATOR+ | Crear regla |
| PATCH | `/api/v1/alerts/rules/{id}` | OPERATOR+ | Actualizar regla |
| DELETE | `/api/v1/alerts/rules/{id}` | ADMIN | Eliminar regla |
| GET | `/api/v1/alerts/events` | Todos | Historial alertas |
| POST | `/api/v1/alerts/events/{id}/acknowledge` | OPERATOR+ | Reconocer alerta |
| POST | `/api/v1/alerts/events/{id}/resolve` | OPERATOR+ | Resolver alerta |
| GET | `/api/v1/alerts/channels` | Propietario | Canales notif. |
| POST | `/api/v1/alerts/channels` | Todos | Crear canal |
| DELETE | `/api/v1/alerts/channels/{id}` | Propietario | Eliminar canal |
| WS | `/ws/metrics/{server_id}?token=` | JWT | Stream métricas |
| WS | `/ws/alerts?token=` | JWT | Stream alertas |

---

## Guía rápida de desarrollo

### Requisitos
- Python 3.12, Node 20, Docker Desktop / Docker Engine

### Backend local
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Con postgres y redis corriendo:
alembic upgrade head
python scripts/seed.py          # crea admin
uvicorn app.main:app --reload
```

### Frontend local
```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

### Todo en Docker
```bash
cp .env.example .env            # editar valores reales
docker compose up -d
# Esperar ~30s, luego:
curl http://localhost/api/v1/health
```

### Dev con hot-reload
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

---

## Variables de entorno (mínimas para producción)

| Variable | Descripción |
|----------|------------|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `POSTGRES_PASSWORD` | Contraseña fuerte PostgreSQL |
| `ADMIN_EMAIL` | Email del primer admin |
| `ADMIN_PASSWORD` | Contraseña del primer admin (mín. 8 chars) |
| `DATABASE_URL` | URL asyncpg completa |
| `REDIS_URL` | URL Redis |

---

## Problemas conocidos resueltos

| Problema | Solución |
|----------|---------|
| `structlog` cachea stdout cerrado en tests | `cache_logger_on_first_use=False` + `PrintLoggerFactory()` sin arg |
| `asyncio.run()` conflicto con pytest-asyncio AUTO | Mockear módulo `asyncio` completo en tests de tasks |
| ENCRYPTION_KEY inválida (31 bytes) | Usar `base64.urlsafe_b64encode(b"test_fernet_key_32bytes_exactly_")` |
| `UserCreate` datetime None en tests | Fijar `datetime(2025,1,1,tzinfo=timezone.utc)` en mock |
| SSH validate bloqueante en HTTP | `validate_ssh=False` por defecto en endpoint POST /servers |
| ECharts chunk >500kB | Code splitting + `chunkSizeWarningLimit: 1100` |
| Hooks condicionales en SettingsPage | Mover todos los useState al top del componente |
| `vitest/config` vs `vite` type conflict | `vitest.config.ts` separado con `mergeConfig` |

---

## Lo que funciona hoy

- ✅ Auth completo: login, refresh, roles, JWT
- ✅ CRUD de servidores con credenciales SSH cifradas
- ✅ Colección de métricas vía SSH: CPU, RAM, Disco, Load, Red, Procesos
- ✅ Métricas Odoo: workers, response time, conexiones DB
- ✅ Métricas PostgreSQL: conexiones, locks, slow queries
- ✅ Motor de alertas con cooldown Redis anti-spam
- ✅ Notificaciones: Email SMTP, Telegram Bot, Webhook
- ✅ WebSockets: stream métricas en tiempo real por servidor
- ✅ Frontend React completo: Dashboard, Servers, Alerts, Settings
- ✅ Gauges ECharts en tiempo real (CPU/RAM/Disk)
- ✅ Dashboard drag-and-drop (react-grid-layout)
- ✅ Docker Compose validado (producción + dev)
- ✅ GitHub Actions CI (backend + frontend)
