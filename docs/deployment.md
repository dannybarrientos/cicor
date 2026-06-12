# 🚀 CICOR ERP — Guía de Despliegue

CICOR ofrece dos opciones de despliegue local: **Docker Compose** para desarrollo rápido y **Minikube + Kubernetes** para un entorno similar a producción. Elegí la que mejor se adapte a tu necesidad.

---

## Opción A: Docker Compose (Desarrollo Rápido)

La forma más simple de levantar todo el sistema. Un solo comando arranca los 12 servicios (frontend, 5 APIs, Nginx y 5 bases de datos).

### Prerrequisitos

- **Docker Desktop** (o Docker Engine + Docker Compose v2). Verificá con:
  ```bash
  docker --version
  docker compose version
  ```

### Clonar y configurar variables de entorno

```bash
git clone <repo-url> cicor
cd cicor
cp .env.example .env
```

El archivo `.env` ya viene con valores por defecto que funcionan. Si necesitás cambiar puertos o credenciales, editá `.env` antes de continuar.

### Levantar todos los servicios

```bash
docker compose up -d
```

La primera vez descarga las imágenes base (`python:3.11-slim`, `node:18-alpine`, `postgres:15-alpine`, `nginx:alpine`) y construye las imágenes del proyecto. Puede tardar unos minutos.

### Servicios que se inician

| Servicio              | Puerto host | Descripción                          |
|-----------------------|-------------|--------------------------------------|
| `cicor-frontend`      | `3000`      | React + Vite + Tailwind              |
| `cicor-nginx`         | `80`        | Reverse proxy (rutea APIs y frontend)|
| `cicor-commercial-api`| `8001`      | API Comercial (FastAPI)              |
| `cicor-inventory-api` | `8002`      | API Inventario (FastAPI)             |
| `cicor-accounting-api`| `8003`      | API Contabilidad (FastAPI)           |
| `cicor-operations-api`| `8004`      | API Operaciones (FastAPI)            |
| `cicor-hr-api`        | `8005`      | API Recursos Humanos (FastAPI)       |
| `cicor-commercial-db` | `5431`      | PostgreSQL — Comercial               |
| `cicor-inventory-db`  | `5432`      | PostgreSQL — Inventario              |
| `cicor-accounting-db` | `5433`      | PostgreSQL — Contabilidad            |
| `cicor-operations-db` | `5434`      | PostgreSQL — Operaciones             |
| `cicor-hr-db`         | `5435`      | PostgreSQL — RRHH                    |

Todas las APIs exponen puerto `8000` internamente en el contenedor y se mapean a `8001-8005` en el host. Nginx expone el puerto `80` y rutea:

- `http://localhost/` → Frontend
- `http://localhost/api/commercial/*` → API Comercial
- `http://localhost/api/inventory/*` → API Inventario
- `http://localhost/api/accounting/*` → API Contabilidad
- `http://localhost/api/operations/*` → API Operaciones
- `http://localhost/api/hr/*` → API RRHH

### Verificación

```bash
# Ver todos los contenedores corriendo
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verificar frontend
curl -f http://localhost:3000 || echo "Frontend no responde"

# Verificar APIs vía Nginx
curl http://localhost/api/commercial/info
curl http://localhost/api/inventory/info
curl http://localhost/api/accounting/info
curl http://localhost/api/operations/info
curl http://localhost/api/hr/info

# Swagger UI de cada API (acceso directo sin Nginx)
open http://localhost:8001/docs  # Comercial
open http://localhost:8002/docs  # Inventario
open http://localhost:8003/docs  # Contabilidad
open http://localhost:8004/docs  # Operaciones
open http://localhost:8005/docs  # RRHH

# Abrir el frontend en el navegador
open http://localhost
```

### Limpiar todo

```bash
docker compose down -v
```

Esto detiene y elimina contenedores, redes y volúmenes (datos de BD). Para conservar los datos, usá `docker compose down` sin `-v`.

---

## Opción B: Minikube + Kubernetes (Producción-like)

Despliegue completo con namespaces, ConfigMaps, Secrets, PVCs, Deployments, Services e Ingress por módulo. Simula un entorno de producción en una máquina local.

### Prerrequisitos completos

- **Docker Desktop** (o motor compatible)
- **Minikube** — [guía de instalación](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl** — [guía de instalación](https://kubernetes.io/docs/tasks/tools/)

Verificá las instalaciones:
```bash
docker --version
minikube version
kubectl version --client
```

### 1. Iniciar Minikube

```bash
minikube start
```

### 2. Habilitar Ingress y levantar el túnel

```bash
# Habilitar el addon de Ingress
minikube addons enable ingress

# En una terminal separada (como Administrador en Windows, con sudo en Mac/Linux),
# ejecutar y DEJAR CORRIENDO:
minikube tunnel
```

El túnel es necesario porque en Docker Desktop las IPs de Minikube no son accesibles directamente desde el host.

### 3. Construir y cargar imágenes

El script `scripts/load-images.sh` (Linux/Mac) y `scripts/load-images.ps1` (Windows) compilan todas las imágenes Docker del proyecto y las cargan en el registro interno de Minikube. Luego aplican los manifiestos de Kubernetes.

**En Linux/Mac:**
```bash
./scripts/load-images.sh
```

**En Windows (PowerShell como Administrador):**
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\load-images.ps1
```

**¿Qué hace el script?**

1. Compila la imagen del frontend (`docker build -t cicor-frontend:v3-local ./frontend`)
2. Carga la imagen del frontend en Minikube (`minikube image load cicor-frontend:v3-local`)
3. Aplica el bundle base del frontend (`kubectl apply -f kubernetes/base-web.yaml`)
4. Para cada uno de los 5 módulos (accounting, commercial, hr, inventory, operations):
   - Compila la imagen de la base de datos (`docker build -t cicor-$mod-db:v3-local ./databases/$mod`)
   - Compila la imagen de la API (`docker build -t cicor-$mod-api:v3-local ./apis/$mod`)
   - Carga ambas en Minikube
   - Aplica el bundle del módulo (`kubectl apply -f kubernetes/$mod-bundle.yaml`)

### 4. Configurar el dominio local

Agregá `cicor.local` al archivo `hosts` de tu sistema operativo:

**Windows:**
1. Abrí el Bloc de notas como Administrador
2. Archivo → Abrir → `C:\Windows\System32\drivers\etc\`
3. Cambiá el filtro a "Todos los archivos (*.*)"
4. Abrí el archivo `hosts`
5. Agregá al final:
   ```
   127.0.0.1 cicor.local
   ```
6. Guardá y cerrá

**Mac/Linux:**
```bash
sudo nano /etc/hosts
```
Agregá la línea:
```
127.0.0.1 cicor.local
```
Guardá con `Ctrl+O`, salí con `Ctrl+X`.

### 5. Verificación

```bash
# Ver pods en todos los namespaces del proyecto
kubectl get pods -A | grep cicor

# Ver servicios por módulo
kubectl get svc -n cicor-web
kubectl get svc -n cicor-commercial
kubectl get svc -n cicor-inventory
kubectl get svc -n cicor-accounting
kubectl get svc -n cicor-operations
kubectl get svc -n cicor-hr

# Ver todos los Ingress
kubectl get ingress -A | grep cicor
```

Una vez que todos los pods estén en estado `Running`, abrí el navegador en:

```
http://cicor.local
```

---

## Estructura de `kubernetes/`

El directorio `kubernetes/` contiene los manifiestos de Kubernetes organizados por módulo:

```
kubernetes/
├── README.md                  ← Descripción y orden de aplicación
├── base-web.yaml              ← Bundle del frontend (Deployment, Service, Ingress, Namespace)
├── commercial-bundle.yaml     ← Bundle del módulo Comercial (API + DB + ConfigMap + Secret + PVC + Ingress)
├── inventory-bundle.yaml      ← Bundle del módulo Inventario
├── accounting-bundle.yaml     ← Bundle del módulo Contabilidad
├── operations-bundle.yaml     ← Bundle del módulo Operaciones
└── hr-bundle.yaml             ← Bundle del módulo Recursos Humanos
```

Cada `bundle.yaml` contiene en un solo archivo (separado por `---`):
- **Namespace** — aísla los recursos del módulo
- **ConfigMap** — variables de configuración no sensibles (hosts, puertos, nivel de log)
- **Secret** — credenciales de base de datos (usuario, contraseña)
- **PersistentVolumeClaim** — almacenamiento persistente para la base de datos (1 Gi)
- **Deployment + Service** para la base de datos (`cicor-<modulo>-db`)
- **Deployment + Service** para la API (`cicor-<modulo>-api`)
- **Ingress** — rutea `cicor.local/api/<modulo>` al Service de la API

El bundle `base-web.yaml` contiene el frontend (React servido por Nginx) y su Ingress en la raíz (`/`).

**Orden de aplicación recomendado:**
1. `kubernetes/base-web.yaml`
2. Los 5 bundles de módulo (el orden entre módulos no importa)

La UI y las APIs usan `cicor.local` como host de Ingress.

---

## Solución de Problemas

### Pods en `ContainerCreating`

Es normal que los pods tarden unos minutos en pasar a `Running`, especialmente la primera vez que Minikube descarga las imágenes. Esperá y volvé a verificar:

```bash
kubectl get pods -n cicor-commercial -w   # -w = watch (actualización en vivo)
```

Si después de varios minutos siguen en `ContainerCreating`, revisá los eventos:

```bash
kubectl describe pod -n cicor-commercial <nombre-del-pod>
```

### Conflictos de puertos

Si Docker Compose falla con `port is already allocated`, algo ya está usando los puertos 80, 3000, 8001-8005 o 5431-5435. Verificá:

```bash
# Mac/Linux
lsof -i :80 -i :3000 -i :8001 -i :8002 -i :8003 -i :8004 -i :8005

# Windows (PowerShell)
netstat -ano | findstr ":80 :3000 :8001 :8002 :8003 :8004 :8005"
```

Cambiá los puertos en `.env` si es necesario (ej: `FRONTEND_PORT=3001`).

### `minikube tunnel` pide permisos de administrador

El túnel necesita permisos elevados para exponer servicios tipo LoadBalancer e Ingress en `127.0.0.1`. En Mac/Linux usá `sudo minikube tunnel`. En Windows ejecutá PowerShell como Administrador.

### Docker Compose: limpiar completamente

```bash
docker compose down -v     # Elimina volúmenes (pierde datos de BD)
docker compose down        # Sin -v: conserva los datos
```

### Ver logs de un servicio específico

```bash
# Docker Compose
docker compose logs -f commercial-api

# Kubernetes
kubectl logs -n cicor-commercial deployment/cicor-commercial-api -f
```

### Verificar que Nginx está ruteando correctamente

```bash
# Desde Docker Compose
curl -v http://localhost/api/commercial/info

# Desde Kubernetes (con el túnel activo)
curl -v http://cicor.local/api/commercial/info
```

---

## Variables de Entorno

El archivo `.env` (creado a partir de `.env.example`) controla toda la configuración local:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `FRONTEND_PORT` | `3000` | Puerto del frontend en el host |
| `VITE_API_BASE_URL` | `http://localhost` | URL base para llamadas a la API desde el frontend |
| `LOG_LEVEL` | `INFO` | Nivel de log para todas las APIs (DEBUG, INFO, WARNING, ERROR) |
| `COMMERCIAL_API_PORT` | `8001` | Puerto host de la API Comercial |
| `INVENTORY_API_PORT` | `8002` | Puerto host de la API Inventario |
| `ACCOUNTING_API_PORT` | `8003` | Puerto host de la API Contabilidad |
| `OPERATIONS_API_PORT` | `8004` | Puerto host de la API Operaciones |
| `HR_API_PORT` | `8005` | Puerto host de la API RRHH |
| `DB_USER` | `cicor_user` | Usuario global de referencia |
| `DB_PASSWORD` | `cicor_pass` | Contraseña global de referencia |
| `COMMERCIAL_DB_USER` | `cicor_user` | Usuario BD Comercial |
| `COMMERCIAL_DB_PASSWORD` | `cicor_pass` | Contraseña BD Comercial |
| `COMMERCIAL_DB_NAME` | `cicor_commercial_db` | Nombre de la BD Comercial |
| `COMMERCIAL_DB_PORT_HOST` | `5431` | Puerto host de la BD Comercial |
| `INVENTORY_DB_USER` | `cicor_user` | Usuario BD Inventario |
| `INVENTORY_DB_PASSWORD` | `cicor_pass` | Contraseña BD Inventario |
| `INVENTORY_DB_NAME` | `cicor_inventory_db` | Nombre de la BD Inventario |
| `INVENTORY_DB_PORT_HOST` | `5432` | Puerto host de la BD Inventario |
| `ACCOUNTING_DB_USER` | `cicor_user` | Usuario BD Contabilidad |
| `ACCOUNTING_DB_PASSWORD` | `cicor_pass` | Contraseña BD Contabilidad |
| `ACCOUNTING_DB_NAME` | `cicor_accounting_db` | Nombre de la BD Contabilidad |
| `ACCOUNTING_DB_PORT_HOST` | `5433` | Puerto host de la BD Contabilidad |
| `OPERATIONS_DB_USER` | `cicor_user` | Usuario BD Operaciones |
| `OPERATIONS_DB_PASSWORD` | `cicor_pass` | Contraseña BD Operaciones |
| `OPERATIONS_DB_NAME` | `cicor_operations_db` | Nombre de la BD Operaciones |
| `OPERATIONS_DB_PORT_HOST` | `5434` | Puerto host de la BD Operaciones |
| `HR_DB_USER` | `cicor_user` | Usuario BD RRHH |
| `HR_DB_PASSWORD` | `cicor_pass` | Contraseña BD RRHH |
| `HR_DB_NAME` | `cicor_hr_db` | Nombre de la BD RRHH |
| `HR_DB_PORT_HOST` | `5435` | Puerto host de la BD RRHH |

Para desarrollo local, los valores por defecto del `.env.example` son suficientes. Solo ajustalos si tenés conflictos de puertos.

---

## Próximo paso: AWS

Cuando estés listo para producción, seguí la guía de despliegue en AWS:

→ [`aws-deployment.md`](aws-deployment.md) — EKS, RDS, ECR, Route 53, CI/CD
