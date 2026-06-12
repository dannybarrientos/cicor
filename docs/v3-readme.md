# CICOR ERP — v3

> Plataforma ERP modular con arquitectura de microservicios. Implementación funcional con 5 APIs FastAPI, 5 bases de datos PostgreSQL 15, frontend React + Vite + Tailwind, desplegable en Minikube y Docker Compose.

## 🧩 Módulos

| Módulo | Color | API | Base de Datos | Entidad principal |
|---|---|---|---|---|
| Comercial | 🟢 `#10B981` | `commercial-api :8001` | `commercial_db` | Ventas (`sales`) |
| Inventario | 🔵 `#3B82F6` | `inventory-api :8002` | `inventory_db` | Productos (`products`) |
| Contabilidad | 🔴 `#EF4444` | `accounting-api :8003` | `accounting_db` | Asientos (`accounting_entries`) |
| Operaciones | 🟠 `#F97316` | `operations-api :8004` | `operations_db` | Procesos (`processes`) |
| RRHH | 🟣 `#A855F7` | `hr-api :8005` | `hr_db` | Empleados (`employees`) |

## 🚀 Inicio Rápido

**Opción 1 — Docker Compose** (recomendada para desarrollo):
```bash
cp .env.example .env
docker compose up -d
```

**Opción 2 — Minikube** (entorno K8s local):
```bash
minikube start
minikube addons enable ingress
minikube tunnel
kubectl apply -f releases/base/web.yaml
kubectl apply -f releases/commercial/bundle.yaml
kubectl apply -f releases/inventory/bundle.yaml
kubectl apply -f releases/accounting/bundle.yaml
kubectl apply -f releases/operations/bundle.yaml
kubectl apply -f releases/hr/bundle.yaml
```

> Guía detallada en [`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md)

## 📚 Documentación

| Documento | Descripción |
|---|---|
| [`docs/INDEX.md`](docs/INDEX.md) | Índice completo de la documentación |
| [`docs/PRESENTACION.md`](docs/PRESENTACION.md) | Presentación ejecutiva, arquitectura y demo funcional |
| [`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md) | Guía de despliegue local con Minikube y Docker Compose |
| [`docs/REFERENCIA-API.md`](docs/REFERENCIA-API.md) | Referencia completa de endpoints por módulo con ejemplos `curl` |
| [`docs/ESQUEMA-BD.md`](docs/ESQUEMA-BD.md) | Esquemas SQL de las 5 bases de datos, constraints e índices |
| [`docs/SISTEMA-DISEÑO.md`](docs/SISTEMA-DISEÑO.md) | Sistema de diseño, paleta de colores y componentes Tailwind |
| [`docs/DESARROLLO.md`](docs/DESARROLLO.md) | Guía para desarrolladores: setup, convenciones, contribución |
| [`releases/`](releases/) | Manifiestos Kubernetes por módulo y namespace |

## 🏗️ Arquitectura

CICOR sigue el patrón **un microservicio = una API = una base de datos = un namespace Kubernetes**. Cada módulo es autónomo: tiene su propia API FastAPI, su instancia PostgreSQL 15 dedicada, y sus propios manifests K8s (Deployment, Service, ConfigMap, Secret, PVC, Ingress).

La comunicación entre módulos se da vía HTTP entre APIs. El módulo Comercial consulta `POST /api/inventory/reserve` en Inventario para validar stock antes de confirmar una venta.

Nginx actúa como reverse proxy central, enrutando por path (`/api/commercial`, `/api/inventory`, etc.) hacia cada API. Todos los servicios exponen health checks (`/health/live`, `/health/ready`, `/health/startup`) para que Kubernetes y Docker Compose monitoreen su estado.

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS |
| APIs | Python 3.11 + FastAPI |
| Bases de datos | PostgreSQL 15 Alpine (1 por módulo) |
| Reverse Proxy | Nginx (Alpine) |
| Orquestación | Kubernetes (Minikube local / AWS EKS producción) |
| Contenedores | Docker + Docker Compose |

## 📂 Estructura del Proyecto

```
v3/
├── README.md
├── .env / .env.example
├── docker-compose.yml
├── load_images.ps1
├── docs/                   # Documentación
├── apis/                   # 5 APIs FastAPI
│   ├── commercial-api/
│   ├── inventory-api/
│   ├── accounting-api/
│   ├── operations-api/
│   └── hr-api/
├── databases/              # Scripts SQL + entrypoints
│   ├── commercial/
│   ├── inventory/
│   ├── accounting/
│   ├── operations/
│   └── hr/
├── frontend/               # React + Vite + Tailwind
├── nginx/                  # Reverse proxy
│   ├── default.conf
│   └── Dockerfile
└── releases/               # Manifiestos Kubernetes
    ├── base/
    ├── commercial/
    ├── inventory/
    ├── accounting/
    ├── operations/
    └── hr/
```

## 🔗 Enlaces rápidos

| Servicio | Swagger | Health |
|---|---|---|
| Frontend | `http://localhost:3000` | — |
| Comercial | `http://localhost:8001/docs` | `http://localhost:8001/health/live` |
| Inventario | `http://localhost:8002/docs` | `http://localhost:8002/health/live` |
| Contabilidad | `http://localhost:8003/docs` | `http://localhost:8003/health/live` |
| Operaciones | `http://localhost:8004/docs` | `http://localhost:8004/health/live` |
| RRHH | `http://localhost:8005/docs` | `http://localhost:8005/health/live` |
