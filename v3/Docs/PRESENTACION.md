# 🏗️ CICOR ERP

Plataforma ERP modular con arquitectura de microservicios desplegada en Kubernetes (Minikube local → AWS EKS en producción).

Puertos expuestos con Docker Compose:

| Servicio | Puerto Local |
|---|---|
| Frontend | http://localhost:3000 |
| API Comercial | http://localhost:8001 |
| API Inventario | http://localhost:8002 |
| API Contabilidad | http://localhost:8003 |
| API Operaciones | http://localhost:8004 |
| API RRHH | http://localhost:8005 |




## 🔧 Desarrollo Rápido con Docker Compose (Opcional)

Para desarrollo local sin Kubernetes:

```bash
docker-compose up -d
```

## 📁 Estructura del Proyecto

```
cicor-erp/
├─ README.md
├─ ARCHITECTURE.md
├─ SECURITY.md
├─ OBSERVABILITY.md
├─ DEVELOPMENT.md
├─ docker-compose.yml
├─ .env.example
├─ frontend/           # React + Vite + Tailwind CSS
├─ apis/               # 5 APIs FastAPI (Python 3.11)
├─ databases/          # Scripts SQL de inicialización
├─ kubernetes/         # Manifiestos YAML
├─ scripts/            # Scripts de automatización
└─ docs/               # Documentación detallada
```


### 4.1 Estructura de cada API

```
apis/<modulo>-api/
├─ Dockerfile
├─ requirements.txt
├─ main.py          # Punto de entrada + rutas FastAPI
├─ models.py        # Schemas Pydantic (validación de datos)
└─ database.py      # Pool de conexiones PostgreSQL
```

---

## 🗺️ Roadmap

**Fase 1 (Actual):** Validación local con Minikube
**Fase 2:** Migración a AWS EKS con CloudFormation (ver especificación en `docs/`)
**Fase 3:** Activación de CRUDs adicionales por módulo (Proveedores, Nómina, Reportes, etc.)


---

## Desarrollo del Frontend (React)

### Estructura del frontend

```
frontend/
├─ Dockerfile
├─ package.json
├─ tailwind.config.js
├─ vite.config.js
├─ index.html
└─ src/
   ├─ main.jsx
   ├─ App.jsx
   ├─ index.css
   ├─ components/
   │  ├─ Navbar.jsx
   │  ├─ Dashboard.jsx
   │  ├─ modules/          # Un componente por módulo ERP
   │  └─ shared/           # Button, Modal, Table, Notification
   └─ utils/
      ├─ api.js            # Funciones HTTP hacia las APIs
      └─ constants.js      # URLs y configuración
```

# 🏛️ ARCHITECTURE.md — Arquitectura de CICOR ERP

---

## Visión General

CICOR ERP está construido sobre una arquitectura de **microservicios** donde cada módulo funciona de forma independiente. El sistema utiliza Kubernetes como plataforma de orquestación, con Ingress Nginx como punto de entrada único hacia el frontend y las APIs.

Principios de diseño:

- **Un módulo = una API = una base de datos** (aislamiento total de datos)
- **Un namespace por módulo** (aislamiento de red y RBAC)
- **Comunicación síncrona** entre Comercial e Inventario vía HTTP interno
- **Portabilidad**: la misma arquitectura corre en Minikube local y en AWS EKS

---

## Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO FINAL                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (Local) / HTTPS (AWS)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INGRESS NGINX CONTROLLER                        │
│            (Reenvío de tráfico por ruta URI)                    │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
  ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │Frontend │ │Comerc. │ │Invent. │ │Contab. │ │  Ops   │
  │ Service │ │Service │ │Service │ │Service │ │Service │
  └────┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
       │          │          │          │          │
       │          ▼          ▼          ▼          ▼
       │     ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
       │     │Comerc. │ │Invent. │ │Contab. │ │  Ops   │
       │     │API Pod │ │API Pod │ │API Pod │ │API Pod │
       │     └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
       │         │          ▲          │          │
       │         │  POST /reserve      │          │
       │         └──────────┘          │          │
       │         │          │          │          │
       │         ▼          ▼          ▼          ▼
       │    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
       │    │Comerc. │ │Invent. │ │Contab. │ │  Ops   │
       │    │DB Pod  │ │DB Pod  │ │DB Pod  │ │DB Pod  │
       │    │(PVC)   │ │(PVC)   │ │(PVC)   │ │(PVC)   │
       │    └────────┘ └────────┘ └────────┘ └────────┘
       │
       │    ┌────────┐ ┌────────┐
       │    │  RRHH  │ │RRHH DB │
       │    │API Pod │ │  Pod   │
       └───►│        │ │ (PVC)  │
            └────────┘ └────────┘

                    ┌──────────────────────────┐
                    │  Prometheus + Grafana     │
                    │  (Scrape :8000/metrics)   │
                    └──────────────────────────┘
```

---

## Interacción entre Módulos

Actualmente solo existe **una interacción activa** entre módulos:

```
Comercial API  ──POST /api/inventory/reserve──►  Inventario API
```

**Flujo:**

1. El usuario crea una venta en Comercial (`POST /api/commercial/sales`)
2. Comercial llama internamente a Inventario con `POST /api/inventory/reserve`
   - Payload: `{ "product_name": "...", "quantity": ... }`
3. Inventario reduce el stock temporalmente y responde:
   - `{ "success": true, "remaining_stock": N, "message": "..." }`
4. Si Inventario falla o responde error, la venta igual se crea pero queda en estado `PENDING_INVENTORY`

Esta llamada ocurre dentro del clúster, a través de la dirección DNS interna de Kubernetes:
```
http://cicor-inventory-api-svc.cicor-inventory.svc.cluster.local:8002/api/inventory/reserve
```

---

## Persistencia de Datos

Cada base de datos PostgreSQL tiene su propio **PersistentVolumeClaim (PVC)**:

| PVC | Namespace | Tamaño Local | Tamaño AWS (EBS gp3) |
|---|---|---|---|
| `cicor-commercial-db-pvc` | cicor-commercial | Dinámico | 50 Gi |
| `cicor-inventory-db-pvc` | cicor-inventory | Dinámico | 50 Gi |
| `cicor-accounting-db-pvc` | cicor-accounting | Dinámico | 50 Gi |
| `cicor-operations-db-pvc` | cicor-operations | Dinámico | 50 Gi |
| `cicor-hr-db-pvc` | cicor-hr | Dinámico | 50 Gi |

Los datos sobreviven a reinicios y recreación de pods gracias a los volúmenes persistentes.

---

## Ingress y Enrutamiento

Un único recurso `Ingress` en el namespace `default` gestiona todo el tráfico:

| Ruta | Destino |
|---|---|
| `/` | `cicor-frontend-svc:80` |
| `/api/commercial/` | `cicor-commercial-api-svc.cicor-commercial:8001` |
| `/api/inventory/` | `cicor-inventory-api-svc.cicor-inventory:8002` |
| `/api/accounting/` | `cicor-accounting-api-svc.cicor-accounting:8003` |
| `/api/operations/` | `cicor-operations-api-svc.cicor-operations:8004` |
| `/api/hr/` | `cicor-hr-api-svc.cicor-hr:8005` |

