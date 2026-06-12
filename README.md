# CICOR ERP

> Plataforma ERP modular con arquitectura de microservicios, diseñada para entornos cloud-native sobre Kubernetes.

## ¿Qué es CICOR?

CICOR es un ERP empresarial compuesto por **5 módulos de negocio independientes** que operan como microservicios autónomos. Cada módulo tiene su propia API, su propia base de datos y su propio namespace en Kubernetes. La plataforma se despliega en **Minikube** para desarrollo local y escala a **AWS EKS** en producción sin cambios de arquitectura.

No es un monolito partido en carpetas: cada módulo puede desplegarse, escalarse y fallar sin afectar a los demás.

## Módulos

| Módulo | Color | Puerto | Entidad Principal |
|---|---|---|---|
| Comercial | `#10B981` | `:8001` | Ventas (`sales`) |
| Inventario | `#3B82F6` | `:8002` | Productos (`products`) |
| Contabilidad | `#EF4444` | `:8003` | Asientos contables |
| Operaciones | `#F97316` | `:8004` | Procesos |
| RRHH | `#A855F7` | `:8005` | Empleados |

## Inicio Rápido

```bash
git clone <repo-url> && cd cicor
cp .env.example .env
docker compose up -d
```

En minutos tenés las 5 APIs, 5 bases de datos y el frontend corriendo en `http://localhost:3000`.

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Bases de datos | PostgreSQL 15 Alpine (1 instancia por módulo) |
| Reverse proxy | Nginx Alpine |
| Orquestación | Kubernetes (Minikube local / AWS EKS producción) |
| Contenedores | Docker + Docker Compose |

## Estructura del Proyecto

```
cicor/
├── apis/                       ← 5 APIs FastAPI
│   ├── commercial/             ← Módulo Comercial (+ tests/)
│   ├── inventory/              ← Módulo Inventario
│   ├── accounting/             ← Módulo Contabilidad
│   ├── operations/             ← Módulo Operaciones
│   └── hr/                     ← Módulo RRHH
├── databases/                  ← Scripts SQL y Dockerfiles por módulo
├── frontend/                   ← React + Vite + Tailwind
├── nginx/                      ← Reverse proxy
├── kubernetes/                 ← Manifiestos K8s (Minikube y EKS)
├── scripts/                    ← load-images.sh y .ps1 para Minikube
├── docs/                       ← Documentación completa
├── prototypes/                 ← Prototipos (Astro Todo)
├── docker-compose.yml          ← Orquestación local
├── .env.example                ← Template de variables de entorno
└── pyproject.toml              ← Configuración Python (ruff, mypy, pytest)
```

## Documentación

| Documento | Contenido | Para quién |
|---|---|---|
| [`docs/presentation.md`](docs/presentation.md) | Visión ejecutiva, arquitectura y demo funcional | Todos |
| [`docs/deployment.md`](docs/deployment.md) | Despliegue local con Docker Compose y Minikube | DevOps, nuevos devs |
| [`docs/aws-deployment.md`](docs/aws-deployment.md) | Guía paso a paso de despliegue en AWS (EKS, RDS, ECR) | DevOps, SRE |
| [`docs/development.md`](docs/development.md) | Setup de entorno, convenciones, guía de contribución | Desarrolladores |
| [`docs/api-reference.md`](docs/api-reference.md) | Endpoints con ejemplos `curl` y Swagger | Frontend y backend |
| [`docs/database-schema.md`](docs/database-schema.md) | Esquemas SQL, constraints e índices | Backend |
| [`docs/design-system.md`](docs/design-system.md) | Paleta de colores, tipografía, componentes | Diseñadores, frontend |
| [`docs/v3-index.md`](docs/v3-index.md) | Índice completo con orden de lectura por rol | Todos |

## Verificación

```bash
# Contenedores healthy
docker ps --format 'table {{.Names}}\t{{.Status}}' --filter name=cicor

# APIs vía Nginx
curl http://localhost/api/commercial/info
curl http://localhost/api/inventory/info
curl http://localhost/api/accounting/info
curl http://localhost/api/operations/info
curl http://localhost/api/hr/info

# Swagger interactivo
open http://localhost:8001/docs   # Comercial
open http://localhost:8002/docs   # Inventario
open http://localhost:8003/docs   # Contabilidad
open http://localhost:8004/docs   # Operaciones
open http://localhost:8005/docs   # RRHH

# Tests
python -m pytest apis/ -v
```

## Desarrollo

**Requisitos mínimos:**
- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- Minikube (para despliegue K8s local)

**Flujo de contribución:**
1. Seguí las convenciones en [`docs/development.md`](docs/development.md)
2. Las APIs usan **pytest**; el frontend usa **ESLint**
3. Cada PR debe incluir tests y no romper los existentes
4. Commits en formato [Conventional Commits](https://www.conventionalcommits.org/)

## Roadmap

| Fase | Estado | Objetivo |
|---|---|---|
| **1. Docker Compose local** | ✅ Completado | 5 APIs + 5 DBs + frontend funcional |
| **2. Minikube local** | ✅ Completado | K8s local con namespaces, ingress, health checks |
| **3. CI/CD** | ✅ Completado | GitHub Actions: lint, test, typecheck |
| **4. AWS EKS producción** | 📋 Documentado | [Guía de despliegue AWS](docs/aws-deployment.md) lista |
| **5. Monitoreo** | 📋 Planeado | Prometheus + Grafana + CloudWatch |
