# Odoo Monitor

Panel de monitoreo en tiempo real para servidores Odoo. Recolecta métricas de sistema, Odoo y PostgreSQL vía SSH, muestra dashboards con gráficas históricas y dispara alertas configurables.

---

## Características

- **Métricas de sistema**: CPU, RAM, swap, disco, red, carga, temperatura
- **Métricas Odoo**: workers activos, procesos colgados, memoria, CPU, tiempo de respuesta
- **Métricas PostgreSQL**: conexiones, queries lentas, locks, deadlocks, tamaño de DB
- **Tiempo real**: WebSocket con actualización automática vía Redis pub/sub
- **Alertas**: reglas por umbral con canales de notificación (email, Telegram, webhook)
- **Audit log**: registro de todas las acciones CRUD
- **Multi-servidor**: gestiona múltiples instancias Odoo desde un solo panel
- **Roles**: ADMIN, OPERATOR, READONLY

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [INSTALL.md](INSTALL.md) | Instalación paso a paso |
| [MANUAL.md](MANUAL.md) | Manual de uso de la aplicación |
| `http://localhost/docs` | API interactiva (Swagger UI, solo en development) |

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 async, Alembic |
| Workers | Celery 5 + Redis (broker y result backend) |
| Frontend | React 18, TypeScript, Vite, TanStack Query, ECharts, Tailwind |
| Base de datos | PostgreSQL 15 |
| SSH | Paramiko |
| Auth | JWT + bcrypt + Fernet (credenciales cifradas) |
| Deploy | Docker Compose v2 |

---

## Arquitectura

```
Nginx (puerto 80)
├── /api/*   → FastAPI (backend:8000)
├── /ws/*    → FastAPI WebSocket
└── /*       → React SPA (frontend:80)

Celery Beat  → programa recolección cada 60s
Celery Worker → SSH al servidor → guarda métricas → publica en Redis
FastAPI      → suscribe Redis pub/sub → reenvía por WebSocket al navegador
```
