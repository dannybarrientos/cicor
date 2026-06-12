# CICOR ERP

> Plataforma ERP modular con arquitectura de microservicios, diseñada para entornos cloud-native sobre Kubernetes.

## Que es CICOR

CICOR es un ERP empresarial compuesto por **5 modulos de negocio independientes** que operan como microservicios autonomos. Cada modulo tiene su propia API, su propia base de datos y su propio namespace en Kubernetes. La plataforma se despliega en **Minikube** para desarrollo local y escala a **AWS EKS** en produccion sin cambios de arquitectura.

No es un monolito partido en carpetas: cada modulo puede desplegarse, escalarse y fallar sin afectar a los demas.

## Modulos

| Modulo | Color | API | Puerto | Entidad Principal |
|---|---|---|---|---|
| Comercial | `#10B981` | `commercial-api` | `:8001` | Ventas (`sales`) |
| Inventario | `#3B82F6` | `inventory-api` | `:8002` | Productos (`products`) |
| Contabilidad | `#EF4444` | `accounting-api` | `:8003` | Asientos contables |
| Operaciones | `#F97316` | `operations-api` | `:8004` | Procesos |
| RRHH | `#A855F7` | `hr-api` | `:8005` | Empleados |

## Arquitectura

CICOR sigue el patron **un microservicio = una API = una base de datos = un namespace**. Cada modulo tiene:

- **API independiente** en Python 3.11 + FastAPI, con Swagger autodocumentado
- **Base de datos dedicada** en PostgreSQL 15 Alpine, sin esquemas compartidos
- **Namespace aislado** en Kubernetes con NetworkPolicies que restringen la comunicacion entre modulos

Toda comunicacion entre modulos ocurre via HTTP REST. Por ejemplo, Comercial consulta a Inventario (`POST /api/inventory/reserve`) para validar stock antes de confirmar una venta. Nginx actua como reverse proxy central, enrutando por path (`/api/commercial`, `/api/inventory`, etc.) hacia cada API.

## Inicio Rapido

```bash
# Clonar y levantar todo con Docker Compose
git clone <repo-url> && cd cicor/v3
cp .env.example .env
docker compose up -d
```

En minutos tenes las 5 APIs, 5 bases de datos y el frontend corriendo en `http://localhost:3000`.

> Guia completa de despliegue (incluye Minikube paso a paso) en [`v3/Docs/DESPLIEGUE.md`](v3/Docs/DESPLIEGUE.md).

## Stack Tecnologico

| Capa | Tecnologia |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Bases de datos | PostgreSQL 15 Alpine (1 instancia por modulo) |
| Reverse proxy | Nginx Alpine |
| Orquestacion | Kubernetes (Minikube local / AWS EKS produccion) |
| Contenedores | Docker + Docker Compose |

## Estructura del Proyecto

```
cicor/
├── README.md               ← este archivo
├── v3/                     ← implementacion principal
│   ├── apis/               ← 5 APIs FastAPI
│   ├── databases/          ← scripts SQL por modulo
│   ├── frontend/           ← React + Vite + Tailwind
│   ├── nginx/              ← reverse proxy
│   ├── releases/           ← manifiestos Kubernetes
│   └── Docs/               ← documentacion completa de v3
├── docs/                   ← documentacion transversal
│   ├── design/             ← fase de diseno v2 (misiones)
│   └── vision-aws.md       ← vision cloud original (AWS)
└── prototypes/             ← prototipos legacy (Astro)
    └── astro-todo/
```

## Documentacion

| Documento | Contenido |
|---|---|
| [`v3/README.md`](v3/README.md) | Readme detallado de la implementacion v3 |
| [`v3/Docs/INDEX.md`](v3/Docs/INDEX.md) | Indice completo de documentacion tecnica |
| [`v3/Docs/PRESENTACION.md`](v3/Docs/PRESENTACION.md) | Presentacion ejecutiva, arquitectura y demo funcional |
| [`v3/Docs/DESPLIEGUE.md`](v3/Docs/DESPLIEGUE.md) | Guia de despliegue con Minikube y Docker Compose |
| [`v3/Docs/REFERENCIA-API.md`](v3/Docs/REFERENCIA-API.md) | Referencia completa de endpoints con ejemplos `curl` |
| [`v3/Docs/ESQUEMA-BD.md`](v3/Docs/ESQUEMA-BD.md) | Esquemas SQL de las 5 bases de datos |
| [`v3/Docs/DESARROLLO.md`](v3/Docs/DESARROLLO.md) | Guia para desarrolladores: setup, convenciones, contribucion |
| [`v3/Docs/SISTEMA-DISEÑO.md`](v3/Docs/SISTEMA-DISEÑO.md) | Sistema de diseno, paleta de colores y componentes |
| [`docs/design/`](docs/design/) | Documentos de la fase de diseno arquitectonico v2 |
| [`docs/vision-aws.md`](docs/vision-aws.md) | Vision original de arquitectura cloud sobre AWS |

## Desarrollo

**Requisitos minimos:**
- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- Minikube (para despliegue K8s local)

**Flujo de contribucion:**
1. Segui las convenciones detalladas en [`v3/Docs/DESARROLLO.md`](v3/Docs/DESARROLLO.md)
2. Las APIs usan **pytest** para testing; el frontend usa **ESLint** para linting
3. Cada PR debe incluir tests que validen el cambio y no romper los tests existentes
4. Los commits siguen el formato [Conventional Commits](https://www.conventionalcommits.org/)

## Roadmap

| Fase | Estado | Objetivo |
|---|---|---|
| **1. Minikube local** | ✅ Completado | 5 APIs + 5 DBs + frontend funcional en K8s local |
| **2. CI/CD** | 🔜 Proximo | Pipeline automatizado de build, test y deploy |
| **3. AWS EKS produccion** | 📋 Planeado | Migracion a cluster productivo con auto-scaling y monitoreo |
