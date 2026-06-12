# 🏗️ CICOR ERP — Presentación Ejecutiva y Demo Funcional

## 📋 Presentación Ejecutiva: Negocio + Demo Funcional

---

# SECCIÓN 1 — NEGOCIO 🎯

## ¿Qué es CICOR?

**CICOR** es una plataforma ERP modular y desacoplada diseñada para integrar, automatizar y optimizar los procesos de negocio de una organización. Su propósito central: **independencia operativa** entre áreas funcionales con **interoperabilidad de datos garantizada**.

> Cada módulo escala, falla y se despliega de forma independiente. El conjunto opera como un sistema unificado.

### 🎯 Propuesta de valor

| Dimensión | Solución CICOR |
|:---|:---|
| **Escalabilidad** | Escalado horizontal independiente por módulo según demanda |
| **Resiliencia** | Falla de un módulo no afecta a los demás |
| **Seguridad** | Defensa en profundidad: red, identidad, runtime y datos |
| **Auditabilidad** | Trazabilidad completa de operaciones con CloudTrail + CloudWatch |
| **Alta disponibilidad** | Infraestructura cloud-native sobre AWS EKS |

---

## 🧩 Los 5 Módulos de Negocio

```
┌──────────────────────────────────────────────────────────────┐
│                      CICOR ERP PLATFORM                      │
├───────────┬───────────┬──────────────┬───────────┬──────────┤
│ COMERCIAL │INVENTARIO │ CONTABILIDAD │OPERACIONES│   RRHH   │
│     🟢    │    🔵     │      🔴      │    🟠     │    🟣    │
├───────────┼───────────┼──────────────┼───────────┼──────────┤
│ Ventas    │ Productos │ Asientos     │ Procesos  │Empleados │
│ Clientes  │ Stock     │ Contables    │ Operativos│ Nómina   │
│ Facturación│ SKU      │ PUC          │ Tareas    │Cargos    │
│           │ Categorías│ D/H          │ Deadlines │Asistencia│
└───────────┴───────────┴──────────────┴───────────┴──────────┘
```

| Módulo | Color | Responsabilidad |
|:---|:---|:---|
| **Comercial** 🟢 | `#10B981` | Gestión de ventas, clientes y facturación |
| **Inventario** 🔵 | `#3B82F6` | Catálogo de productos, control de stock y SKUs |
| **Contabilidad** 🔴 | `#EF4444` | Registro de asientos contables con débito/crédito |
| **Operaciones** 🟠 | `#F97316` | Gestión de procesos operacionales y seguimiento |
| **RRHH** 🟣 | `#A855F7` | Administración de empleados, nómina y permisos |

---

## 🏛️ Filosofía de Arquitectura Modular

```
Un Módulo = Una API = Una Base de Datos = Un Namespace

┌─────────────────────────────────────────────────────────┐
│ Namespace: cicor-commercial                             │
│  ┌─────────────────┐    ┌──────────────────┐            │
│  │ commercial-api  │───▶│ commercial-db    │            │
│  │ FastAPI :8000   │    │ PostgreSQL :5432 │            │
│  └─────────────────┘    └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Principios

- **Independencia de datos**: cada módulo dueño de su esquema (no hay base de datos compartida)
- **Comunicación controlada**: solo mediante APIs REST entre módulos (ej. Comercial → Inventario)
- **Aislamiento estricto**: NetworkPolicies que impiden tráfico entre Pods de distintos namespaces
- **Escalado granular**: cada Deployment tiene su propio HPA (Horizontal Pod Autoscaler)
- **Bases de datos segregadas**: PostgreSQL 15 Alpine, una instancia por módulo

---

## 🏗️ Arquitectura Cloud — Visión AWS

```
                        Internet (HTTPS)
                              │
                    ┌─────────▼──────────┐
                    │   AWS ELB (ALB)    │
                    │  Balanceo público  │
                    └─────────┬──────────┘
                              │
              ┌───────────────▼────────────────┐
              │     AWS VPC — Private Subnet   │
              │  ┌──────────────────────────┐  │
              │  │    AWS EKS Cluster        │  │
              │  │                           │  │
              │  │  ┌─ namespace: default ─┐ │  │
              │  │  │ Ingress Controller   │ │  │
              │  │  │ + Frontend React     │ │  │
              │  │  └──────────────────────┘ │  │
              │  │                           │  │
              │  │  ┌─ cicor-commercial ───┐ │  │
              │  │  │ API │ DB  │ PVC/EBS  │ │  │
              │  │  └──────────────────────┘ │  │
              │  │  ┌─ cicor-inventory ────┐ │  │
              │  │  │ API │ DB  │ PVC/EBS  │ │  │
              │  │  └──────────────────────┘ │  │
              │  │  ┌─ cicor-accounting ───┐ │  │
              │  │  │ API │ DB  │ PVC/EBS  │ │  │
              │  │  └──────────────────────┘ │  │
              │  │  ┌─ cicor-operations ───┐ │  │
              │  │  │ API │ DB  │ PVC/EBS  │ │  │
              │  │  └──────────────────────┘ │  │
              │  │  ┌─ cicor-hr ───────────┐ │  │
              │  │  │ API │ DB  │ PVC/EBS  │ │  │
              │  │  └──────────────────────┘ │  │
              │  └──────────────────────────┘  │
              │           │                    │
              │    ┌──────▼──────┐             │
              │    │  AWS EBS    │             │
              │    │  Volúmenes  │             │
              │    │  Persistentes│            │
              │    └─────────────┘             │
              └────────────────────────────────┘
                              │
              ┌───────────────▼────────────────┐
              │     AWS Services               │
              │  S3 │ IAM │ Secrets Mgr │ KMS  │
              └────────────────────────────────┘
```

### 6 Namespaces segregados

| Namespace | Componentes |
|:---|:---|
| `default` | Ingress Controller (Nginx) + Frontend React |
| `cicor-commercial` | Commercial API + commercial-db + PVC |
| `cicor-inventory` | Inventory API + inventory-db + PVC |
| `cicor-accounting` | Accounting API + accounting-db + PVC |
| `cicor-operations` | Operations API + operations-db + PVC |
| `cicor-hr` | HR API + hr-db + PVC |

### Servicios AWS requeridos

| Servicio | Rol |
|:---|:---|
| **EKS** | Orquestación de contenedores Kubernetes |
| **EC2** | Worker Nodes del clúster (min. 3 nodos) |
| **VPC** | Segmentación de red con subredes públicas/privadas |
| **ELB** | Balanceo de carga externo hacia Ingress |
| **S3** | Almacenamiento de objetos y documentos |
| **EBS** | Volúmenes persistentes para bases de datos |
| **IAM** | Roles y políticas de acceso mínimo privilegio |
| **Secrets Manager** | Gestión centralizada de credenciales |
| **CloudWatch** | Centralización de logs y métricas |
| **X-Ray** | Trazabilidad distribuida de requests |
| **Config** | Detección de drift y cumplimiento |
| **CloudTrail** | Auditoría de llamadas API |

---

## 🔄 Diagrama de Flujo de Datos Interno

El tráfico ingresa por el Ingress Controller de Nginx, que enruta según la ruta URI hacia cada API de módulo. Cada API se comunica exclusivamente con su propia base de datos PostgreSQL, y la comunicación entre módulos (Comercial → Inventario) ocurre vía HTTP interno dentro del clúster.

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

## 🔐 Modelo de Seguridad — Defensa en Profundidad

```
     ┌────────────────────────────────────────────────────┐
     │               CAPA 1: RED                          │
     │  VPC + Subredes Privadas + NetworkPolicies         │
     │  Tráfico entre namespaces BLOQUEADO por defecto     │
     ├────────────────────────────────────────────────────┤
     │               CAPA 2: IDENTIDAD                    │
     │  IAM Roles (mínimo privilegio) + RBAC por namespace│
     │  Service Accounts dedicados por Deployment          │
     ├────────────────────────────────────────────────────┤
     │               CAPA 3: SECRETOS                     │
     │  Kubernetes Secrets (etcd encriptado)              │
     │  AWS Secrets Manager (rotación automática)         │
     │  Variables de entorno NUNCA exponen credenciales    │
     ├────────────────────────────────────────────────────┤
     │               CAPA 4: DATOS                        │
     │  TLS en tránsito (HTTPS para clientes)             │
     │  Encriptación en reposo (EBS, S3, RDS, etcd)      │
     │  cert-manager para gestión automática de TLS        │
     ├────────────────────────────────────────────────────┤
     │               CAPA 5: RUNTIME                      │
     │  Seccomp (restricción de syscalls)                  │
     │  Falco (detección de comportamiento anómalo)        │
     │  Escaneo CVE de imágenes antes del despliegue       │
     ├────────────────────────────────────────────────────┤
     │               CAPA 6: AUDITORÍA                    │
     │  CloudTrail (todas las llamadas API AWS)            │
     │  Kubernetes Audit Logs (acceso a recursos K8s)     │
     │  AWS Config (detección de drift)                   │
     └────────────────────────────────────────────────────┘
```

### Reglas de NetworkPolicy

| Origen | Destino | Permitido |
|:---|:---|:---|
| Ingress Controller | APIs de módulos | ✅ |
| Ingress Controller | Otro Ingress | ❌ |
| Comercial API | Inventory API (`/reserve`) | ✅ |
| Comercial API | Accounting API | ❌ |
| Cualquier API | Su propia DB | ✅ |
| Cualquier API | DB de otro módulo | ❌ |

### Buenas prácticas en YAML

- `resources.requests` y `resources.limits` definidos
- `readinessProbe`, `livenessProbe`, `startupProbe` configurados
- `securityContext` endurecido (no root, no privileged)
- Imágenes con versión fija (`:latest` prohibido)
- `ConfigMap` y `Secret` separados explícitamente
- `serviceAccountName` declarado por Deployment

---

## 📊 Observabilidad — Stack Completo

```
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Frontend  │   │  APIs    │   │  DBs     │   │ Serverless│
 │  React    │   │ FastAPI  │   │PostgreSQL│   │ Lambda   │
 └────┬──────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
      │               │              │              │
      ▼               ▼              ▼              ▼
 ┌─────────────────────────────────────────────────────────┐
 │                                                         │
 │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
 │  │  CloudWatch  │  │   X-Ray      │  │  Prometheus  │  │
 │  │  Logs/Metrics│  │  Trazas      │  │  + Grafana   │  │
 │  │  + Alarmas   │  │  Distribuidas│  │  Dashboards  │  │
 │  └──────────────┘  └──────────────┘  └──────────────┘  │
 │                                                         │
 │  ┌──────────────┐  ┌──────────────┐                    │
 │  │  AWS Config  │  │    Falco     │                    │
 │  │  Cumplimiento│  │  Runtime Sec │                    │
 │  └──────────────┘  └──────────────┘                    │
 │                                                         │
 └─────────────────────────────────────────────────────────┘
```

| Herramienta | Propósito |
|:---|:---|
| **CloudWatch** | Logs centralizados, métricas de infraestructura, alarmas |
| **X-Ray** | Trazabilidad distribuida end-to-end (frontend → API → DB) |
| **Prometheus + Grafana** | Métricas de aplicación y Kubernetes, dashboards visuales |
| **AWS Config** | Detección de cambios de configuración y desviaciones |
| **Falco** | Detección de anomalías en runtime de contenedores |
| **CloudTrail** | Auditoría de todas las llamadas a la API de AWS |

---

## 💾 Estrategia de Persistencia por Ambiente

| Ambiente | Base de Datos | Volúmenes | Snapshots | Retención |
|:---|:---|:---|:---|:---|
| **Local** | PostgreSQL 15 Alpine | Docker named volumes | — | Desarrollo |
| **Dev** | PostgreSQL 15 Alpine | EBS `gp3` | Cada 24h | 7 días |
| **QA** | PostgreSQL 15 Alpine | EBS `gp3` | Cada 12h | 30 días |
| **Prod** | PostgreSQL 15 Alpine | EBS `gp3` multi-zona | Diarios + AWS Backup | 90 días |

- **Dumps de respaldo**: exportación diaria a S3 para disaster recovery
- **Segregación**: buckets S3 independientes por ambiente
- **Encriptación**: reposo (EBS + S3) y tránsito (TLS)

### Volúmenes Persistentes por Módulo

Cada base de datos PostgreSQL tiene su propio **PersistentVolumeClaim (PVC)**, lo que garantiza que los datos sobrevivan a reinicios y recreación de pods:

| PVC | Namespace | Tamaño Local | Tamaño AWS (EBS gp3) |
|---|---|---|---|
| `cicor-commercial-db-pvc` | cicor-commercial | Dinámico | 50 Gi |
| `cicor-inventory-db-pvc` | cicor-inventory | Dinámico | 50 Gi |
| `cicor-accounting-db-pvc` | cicor-accounting | Dinámico | 50 Gi |
| `cicor-operations-db-pvc` | cicor-operations | Dinámico | 50 Gi |
| `cicor-hr-db-pvc` | cicor-hr | Dinámico | 50 Gi |

---

## ✅ Criterios de Éxito del Negocio

1. ✅ Clúster EKS operativo con ≥ 3 worker nodes `Ready`
2. ✅ 5 módulos ERP como Deployments independientes con ≥ 2 réplicas cada uno
3. ✅ APIs accesibles SOLO dentro del clúster (sin exposición directa a internet)
4. ✅ Ingress Controller enruta tráfico HTTPS correctamente por hostname/path
5. ✅ Comunicación API ↔ DB funcional con datos persistentes tras reinicio de Pod
6. ✅ HPA configurado para cada Deployment (escala a 70% CPU)
7. ✅ NetworkPolicies bloquean tráfico no autorizado entre namespaces
8. ✅ Secrets encriptados, nunca expuestos en logs ni descripciones de Pods
9. ✅ Logs centralizados en CloudWatch con capacidad de búsqueda
10. ✅ Snapshots diarios de EBS con política de retención de 90 días

---

# SECCIÓN 2 — DEMO: LO QUE YA FUNCIONA ⚡

## 🚀 ¿Qué está implementado?

**v3 de CICOR** es la implementación funcional completa con:

- **5 microservicios FastAPI** corriendo con CRUD completo
- **5 bases de datos PostgreSQL 15 Alpine** con datos semilla
- **Frontend React + Vite + Tailwind** con diseño responsive
- **Nginx reverse proxy** enrutando tráfico a los 5 módulos
- **Kubernetes manifests** para Minikube (listos para producción AWS EKS)
- **Docker Compose** para desarrollo local rápido
- **Health checks** Kubernetes-ready (liveness, readiness, startup)
- **Swagger/OpenAPI** docs interactivos por módulo
- **Comunicación inter-módulo** activa: Comercial → Inventario

---

## 🧩 Las 5 APIs — Endpoints Overview

```
CICOR ERP — APIs Activas

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   NGINX Reverse Proxy (port 80)                                  │
│                                                                  │
│   /api/commercial/*  ──▶ commercial-api  :8000  🟢 Comercial     │
│   /api/inventory/*   ──▶ inventory-api   :8000  🔵 Inventario    │
│   /api/accounting/*  ──▶ accounting-api  :8000  🔴 Contabilidad  │
│   /api/operations/*  ──▶ operations-api  :8000  🟠 Operaciones   │
│   /api/hr/*          ──▶ hr-api          :8000  🟣 RRHH          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| Módulo | Puerto Host | Endpoint CRUD | Entidad | Status flow |
|:---|:---|:---|:---|:---|
| 🟢 Comercial | `8001` | `/api/commercial/sales` | Ventas | PENDING → CONFIRMED / PENDING_INVENTORY |
| 🔵 Inventario | `8002` | `/api/inventory/products` | Productos | — |
| 🔴 Contabilidad | `8003` | `/api/accounting/entries` | Asientos | DRAFT → POSTED → REVERSED |
| 🟠 Operaciones | `8004` | `/api/operations/processes` | Procesos | PLANNING → IN_PROGRESS → COMPLETED |
| 🟣 RRHH | `8005` | `/api/hr/employees` | Empleados | ACTIVE / INACTIVE / ON_LEAVE |

### CRUD completo por módulo

| Módulo | GET (list) | POST (create) | PUT (update) | DELETE |
|:---|:---|:---|:---|:---|
| Comercial | ✅ `GET /sales` | ✅ `POST /sales` | ✅ `PUT /sales/{id}` | ✅ `DELETE /sales/{id}` |
| Inventario | ✅ `GET /products` | ✅ `POST /products` | ✅ `PUT /products/{id}` | ✅ `DELETE /products/{id}` |
| Contabilidad | ✅ `GET /entries` | ✅ `POST /entries` | ✅ `PUT /entries/{id}` | ✅ `DELETE /entries/{id}` |
| Operaciones | ✅ `GET /processes` | ✅ `POST /processes` | ✅ `PUT /processes/{id}` | ✅ `DELETE /processes/{id}` |
| RRHH | ✅ `GET /employees` | ✅ `POST /employees` | ✅ `PUT /employees/{id}` | ✅ `DELETE /employees/{id}` |

### Estructura Interna de cada API

Cada uno de los 5 microservicios comparte la misma estructura de archivos, garantizando consistencia en el desarrollo:

```
apis/<modulo>-api/
├─ Dockerfile
├─ requirements.txt
├─ main.py          # Punto de entrada + rutas FastAPI
├─ models.py        # Schemas Pydantic (validación de datos)
└─ database.py      # Pool de conexiones PostgreSQL
```

---

## 🔗 Comunicación Inter-Módulo: Comercial → Inventario

El flujo estrella de la demo: **al crear una venta, se reserva stock automáticamente**.

```
┌─────────────────────────────────────────────────────────────┐
│                  FLUJO DE VENTA CON RESERVA                  │
│                                                             │
│  1. Usuario crea venta en Frontend                          │
│     POST /api/commercial/sales                              │
│     {                                                       │
│       "product_name": "Laptop Dell XPS 15",                 │
│       "quantity": 2,                                        │
│       "unit_price": 1200.00,                                │
│       "total_amount": 2400.00,                              │
│       "customer_name": "Empresa ABC"                        │
│     }                                                       │
│          │                                                  │
│          ▼                                                  │
│  2. commercial-api recibe la request                        │
│     ┌──────────────────────────────────┐                    │
│     │ Paso A: Inserta venta con        │                    │
│     │         status = PENDING         │                    │
│     └──────────────────────────────────┘                    │
│          │                                                  │
│          ▼                                                  │
│  3. commercial-api llama a inventory-api                    │
│     POST http://inventory-api:8000/api/inventory/reserve    │
│     { "product_name": "Laptop Dell XPS 15", "quantity": 2 } │
│          │                                                  │
│          ▼                                                  │
│  4. inventory-api procesa la reserva                        │
│     ┌──────────────────────────────────┐                    │
│     │ ¿Producto existe?                │                    │
│     │  ├─ NO → success: false          │                    │
│     │  └─ SÍ → ¿Stock suficiente?      │                    │
│     │           ├─ NO → success: false  │                    │
│     │           └─ SÍ → descuenta stock │                    │
│     │                   success: true   │                    │
│     └──────────────────────────────────┘                    │
│          │                                                  │
│          ▼                                                  │
│  5. commercial-api actualiza el status                      │
│     ┌──────────────────────────────────┐                    │
│     │ Reserve OK  → status = CONFIRMED │                    │
│     │ Reserve FAIL → status = PENDING_INVENTORY             │
│     │ API caída   → status = PENDING_INVENTORY              │
│     └──────────────────────────────────┘                    │
│                                                             │
│  ⚡ La venta SIEMPRE se crea (incluso si Inventario falla)  │
└─────────────────────────────────────────────────────────────┘
```

### Ejemplo de respuesta exitosa

```json
// POST /api/commercial/sales → 201 Created
{
  "id": 9,
  "product_name": "Laptop Dell XPS 15",
  "quantity": 2,
  "unit_price": 1200.00,
  "total_amount": 2400.00,
  "customer_name": "Empresa ABC",
  "sale_date": "2026-06-10T14:30:00Z",
  "status": "CONFIRMED",
  "created_at": "2026-06-10T14:30:00Z",
  "updated_at": "2026-06-10T14:30:00Z"
}

// POST /api/inventory/reserve → 200 OK (llamada interna)
{
  "success": true,
  "remaining_stock": 48,
  "message": "Stock reservado exitosamente. Restante: 48 unidades"
}
```

---

## 🗄️ Esquemas de Base de Datos

Una tabla principal por módulo, PostgreSQL 15 Alpine con init scripts y datos semilla.

| Módulo | Base de Datos | Tabla | Columnas clave | Seed rows |
|:---|:---|:---|:---|:---|
| 🟢 Comercial | `commercial_db` | `sales` | id, product_name, quantity, unit_price, total_amount, customer_name, sale_date, status | 8 |
| 🔵 Inventario | `inventory_db` | `products` | id, name, sku (UNIQUE), description, category, stock_quantity, reorder_level, unit_price | 10 |
| 🔴 Contabilidad | `accounting_db` | `accounting_entries` | id, account_code, account_name, debit, credit, description, entry_date, status | 9 |
| 🟠 Operaciones | `operations_db` | `processes` | id, process_name, description, owner, status, start_date, expected_end_date, actual_end_date | 7 |
| 🟣 RRHH | `hr_db` | `employees` | id, full_name, email (UNIQUE), phone, position, department, hire_date, salary, status | 12 |

### Reglas de negocio en la BD

- **Contabilidad**: `CHECK (debit XOR credit)` — cada asiento tiene débito O crédito, nunca ambos
- **Inventario**: `stock_quantity >= 0`, `reorder_level >= 0`, `unit_price >= 0`
- **Operaciones**: `actual_end_date >= start_date`, `expected_end_date >= start_date`
- **Comercial**: `status IN ('PENDING','CONFIRMED','CANCELLED','PENDING_INVENTORY')`
- **Todas**: trigger `update_updated_at_column()` en cada UPDATE

---

## 🎨 Frontend con Design System

```
CICOR Design System — Identidad de color por módulo

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  🟦 CICOR Primary: #1E40AF (navbar corporativo)                │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐│
│  │Comercial │ │Inventario│ │Contabilid│ │Operacion │ │ RRHH  ││
│  │  🟢      │ │  🔵      │ │  🔴      │ │  🟠      │ │  🟣   ││
│  │ #10B981  │ │ #3B82F6  │ │ #EF4444  │ │ #F97316  │ │#A855F7││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Características del frontend

| Aspecto | Tecnología / Decisión |
|:---|:---|
| **Framework** | React 18 + Vite (HMR instantáneo) |
| **Estilos** | Tailwind CSS con tokens de diseño personalizados |
| **Ruteo** | React Router v6: `/`, `/commercial`, `/inventory`, `/accounting`, `/operations`, `/hr` |
| **Tipografía** | Sora (body), Lexend (headings), JetBrains Mono (código) |
| **Componentes** | Navbar, Dashboard, ModuleCards, Table, Modal, Button, Notification (reutilizables) |
| **API Client** | Fetch centralizado con `constants.js` (URLs, colores, status badges) |
| **Responsive** | Mobile-first: grid 1 col → 2 col → 3 col según breakpoint |
| **Animaciones** | fade-in, slide-up, nav-slide-down, pulse-dot (Tailwind keyframes) |

### Dashboard: vista principal

- 5 tarjetas de módulo con color, descripción y acceso directo
- Banner de arquitectura activa con tags: Nginx, RBAC, NetworkPolicies, Prometheus, Grafana
- Accesos rápidos a Prometheus (`:30090`) y Grafana (`:30300`) en Minikube
- Nota visual de interacción: Comercial → Inventario `/reserve`

---

## ❤️ Health Checks y Monitoreo

### Health endpoints por módulo (idénticos en los 5)

| Endpoint | Probe K8s | Qué verifica |
|:---|:---|:---|
| `GET /health/live` | `livenessProbe` | Proceso vivo (siempre responde si la app corre) |
| `GET /health/ready` | `readinessProbe` | Conexión a BD disponible (503 si no) |
| `GET /health/startup` | `startupProbe` | Inicialización completada (BD lista) |
| `GET /metrics` | Prometheus | Métricas HTTP (requests, latencia, errores) |

### Swagger / OpenAPI

Cada módulo expone documentación interactiva:

| Módulo | Swagger UI | ReDoc |
|:---|:---|:---|
| Comercial | `http://localhost:8001/docs` | `http://localhost:8001/redoc` |
| Inventario | `http://localhost:8002/docs` | `http://localhost:8002/redoc` |
| Contabilidad | `http://localhost:8003/docs` | `http://localhost:8003/redoc` |
| Operaciones | `http://localhost:8004/docs` | `http://localhost:8004/redoc` |
| RRHH | `http://localhost:8005/docs` | `http://localhost:8005/redoc` |

> A través del reverse proxy: `http://cicor.local/api/commercial/docs` (Minikube) o `http://localhost/api/commercial/docs` (Docker Compose)

---

## 🖥️ Despliegue Local con Minikube

### Paso a paso (5 comandos)

```bash
# 1. Iniciar el clúster Kubernetes local
minikube start

# 2. Habilitar Ingress (necesario para enrutar tráfico)
minikube addons enable ingress

# 3. Abrir túnel (en otra terminal, como administrador)
minikube tunnel
# → Expone LoadBalancer en 127.0.0.1

# 4. Construir imágenes Docker dentro de Minikube
./scripts/load-images.sh       # Linux/Mac
# .\scripts\load-images.ps1    # Windows

# 5. Aplicar manifiestos Kubernetes
kubectl apply -f kubernetes/base-web.yaml
kubectl apply -f kubernetes/commercial-bundle.yaml
kubectl apply -f kubernetes/inventory-bundle.yaml
kubectl apply -f kubernetes/accounting-bundle.yaml
kubectl apply -f kubernetes/operations-bundle.yaml
kubectl apply -f kubernetes/hr-bundle.yaml
```

### Verificación

```bash
# Ver pods corriendo
kubectl get pods
# Deben aparecer ~12 pods en estado Running

# Acceder desde navegador
# 1. Agregar al archivo hosts: 127.0.0.1 cicor.local
# 2. Abrir: http://cicor.local
```

### También disponible: Docker Compose

```bash
# Alternativa más simple para desarrollo rápido
docker-compose up -d
# Acceder en: http://localhost
```

---

## 🛣️ Camino a Producción: Minikube → AWS EKS

```
┌─────────────────────────────────────────────────────────┐
│                READY FOR PRODUCTION                      │
│                                                         │
│  LOCAL (HOY)              PRODUCCIÓN (MAÑANA)           │
│  ┌─────────────┐          ┌──────────────────┐          │
│  │  Minikube    │  ───▶   │  AWS EKS          │          │
│  │  1 nodo      │          │  3+ nodos multi-AZ│          │
│  └─────────────┘          └──────────────────┘          │
│  ┌─────────────┐          ┌──────────────────┐          │
│  │  Docker      │  ───▶   │  ECR (registro    │          │
│  │  images local│          │   privado AWS)    │          │
│  └─────────────┘          └──────────────────┘          │
│  ┌─────────────┐          ┌──────────────────┐          │
│  │  Docker      │  ───▶   │  EBS gp3           │          │
│  │  volumes     │          │  multi-zona        │          │
│  └─────────────┘          └──────────────────┘          │
│  ┌─────────────┐          ┌──────────────────┐          │
│  │  cicor.local │  ───▶   │  cicor.acme.com   │          │
│  │  (hosts file)│          │  (Route53 + TLS)  │          │
│  └─────────────┘          └──────────────────┘          │
│                                                         │
│  Lo que NO cambia:                                      │
│  ✅ Mismos Dockerfiles                                  │
│  ✅ Mismos manifiestos Kubernetes (ajustando imagePull) │
│  ✅ Mismos init.sql                                     │
│  ✅ Mismas APIs FastAPI                                 │
│  ✅ Mismo frontend React                                │
│                                                         │
│  Lo que se AGREGA en producción:                        │
│  ➕ AWS Secrets Manager (credentiales)                   │
│  ➕ AWS Backup (snapshots automatizados)                 │
│  ➕ CloudWatch + X-Ray (observabilidad)                  │
│  ➕ cert-manager (TLS automático)                        │
│  ➕ HPA + Cluster Autoscaler (escalado)                  │
│  ➕ Falco + Seccomp (seguridad runtime)                  │
│  ➕ AWS Config + CloudTrail (cumplimiento)               │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Resumen General

| Dimensión | v2 — Negocio (visión) | v3 — Demo (realidad) |
|:---|:---|:---|
| **Arquitectura** | 5 módulos + 6 namespaces en EKS | 5 APIs + 5 DBs + Nginx en Minikube |
| **APIs** | FastAPI con CRUD completo | ✅ 25 endpoints operativos |
| **Bases de datos** | PostgreSQL por módulo + PVC | ✅ PostgreSQL 15 Alpine con seed data |
| **Frontend** | React, estructura base | ✅ Dashboard + 5 vistas de módulo |
| **Inter-módulo** | REST entre namespaces | ✅ Comercial → Inventario `/reserve` |
| **Security** | RBAC, NetworkPolicies, Secrets, TLS | ✅ ConfigMaps, Secrets, CORS, probes |
| **Observability** | CloudWatch, X-Ray, Prometheus, Grafana, Falco | ✅ `/metrics`, JSON logging, health checks |
| **Despliegue** | AWS EKS multi-nodo | ✅ Minikube 1 nodo + Docker Compose |
| **Documentación** | Swagger por módulo | ✅ `/docs` y `/redoc` por API |

---

## 🎯 Conclusión: Del Negocio al Demo

```
 ┌────────────────────────────────────────────────────────────┐
 │                                                            │
 │   v2 — VISIÓN DE NEGOCIO        v3 — DEMO FUNCIONAL        │
 │  ┌─────────────────────┐      ┌─────────────────────┐      │
 │  │  Arquitectura cloud  │      │  5 APIs corriendo   │      │
 │  │  AWS EKS, VPC, ELB   │      │  CRUD completo      │      │
 │  │                      │      │                     │      │
 │  │  6 namespaces K8s    │      │  5 DBs PostgreSQL    │      │
 │  │  RBAC, NetPol, Sec   │      │  Seed data lista     │      │
 │  │                      │      │                     │      │
 │  │  Observabilidad full │      │  Frontend React      │      │
 │  │  CloudWatch+X-Ray    │      │  Design system       │      │
 │  │  Prometheus+Grafana  │      │  5 colores de módulo │      │
 │  │                      │      │                     │      │
 │  │  Defensa profundidad │      │  Comunicación real   │      │
 │  │  6 capas seguridad   │      │  Comercial→Inventario│      │
 │  └─────────────────────┘      └─────────────────────┘      │
 │           │                            │                   │
 │           └──────────┬─────────────────┘                   │
 │                      ▼                                     │
 │         ┌─────────────────────────┐                        │
 │         │   PRÓXIMOS PASOS        │                        │
 │         │                         │                        │
 │         │  1. CI/CD con GitHub    │                        │
 │         │     Actions + Helm      │                        │
 │         │                         │                        │
 │         │  2. Migración a AWS EKS │                        │
 │         │     (ECR + EBS + ELB)   │                        │
 │         │                         │                        │
 │         │  3. Observabilidad      │                        │
 │         │     CloudWatch + X-Ray  │                        │
 │         │     + Grafana dashboards│                        │
 │         │                         │                        │
 │         │  4. Seguridad producción│                        │
 │         │     Falco + Seccomp     │                        │
 │         │     + Secrets Manager   │                        │
 │         │                         │                        │
 │         │  5. Lógica de negocio   │                        │
 │         │     avanzada por módulo │                        │
 │         └─────────────────────────┘                        │
 │                                                            │
 └────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Roadmap

| Fase | Estado | Objetivo |
|:---|:---|:---|
| **Fase 1** | ✅ Actual | Validación local con Minikube — 5 APIs + 5 DBs + Frontend operativos |
| **Fase 2** | 🔲 Próxima | Migración a AWS EKS con CloudFormation (ECR + EBS + ELB + Route53) |
| **Fase 3** | 🔲 Planificada | Activación de CRUDs adicionales por módulo (Proveedores, Nómina, Reportes, etc.) |

---

> **CICOR ERP** — La visión de negocio está definida. La implementación base funciona. El camino a producción está trazado. 🚀

---

*Documento generado para presentación ejecutiva — Junio 2026*
