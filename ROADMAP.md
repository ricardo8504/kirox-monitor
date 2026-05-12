# Odoo Monitor — Roadmap

## Estado actual

**Fase:** 0 — Setup inicial  
**Completado:** 0%  
**Inicio:** 2026-05-12

---

## Resumen del sistema

Sistema de monitoreo y administración de servidores Odoo 9 (Python 2.7).
Permite configurar múltiples servidores y monitorear en tiempo real métricas del
sistema operativo, procesos Odoo y base de datos PostgreSQL.

---

## Fases de desarrollo

| # | Fase | Estado | % |
|---|------|--------|---|
| 0 | Setup del proyecto e infraestructura | En progreso | 0% |
| 1 | Backend: Esqueleto FastAPI | Pendiente | 0% |
| 2 | Autenticación y usuarios | Pendiente | 0% |
| 3 | Gestión de servidores | Pendiente | 0% |
| 4 | Motor de monitoreo | Pendiente | 0% |
| 5 | Sistema de alertas | Pendiente | 0% |
| 6 | WebSockets y tiempo real | Pendiente | 0% |
| 7 | Frontend: Base | Pendiente | 0% |
| 8 | Frontend: Servidores y métricas | Pendiente | 0% |
| 9 | Frontend: Dashboard dinámico | Pendiente | 0% |
| 10 | Frontend: Alertas y configuración | Pendiente | 0% |
| 11 | Docker y despliegue | Pendiente | 0% |
| 12 | Documentación y CI | Pendiente | 0% |
| 13 | Extras de alto valor | Pendiente | 0% |

---

## Decisiones de arquitectura

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy 2.0 async
- **Queue:** Celery 5 + Redis 7
- **Frontend:** React 18 + TypeScript + Vite + Zustand + TanStack Query
- **Gráficas:** Apache ECharts
- **DB:** PostgreSQL 15
- **Containers:** Docker + Docker Compose v2

---

## Problemas encontrados

(ninguno aún)

---

## Próximos pasos

1. Crear estructura de directorios del proyecto
2. Inicializar git con .gitignore
3. Configurar Docker Compose base
4. Configurar dependencias backend y frontend
