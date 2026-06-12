# 🛠️ CICOR ERP — Guía de Desarrollo

Guía para contribuir al desarrollo de CICOR. Cubre la estructura del proyecto, el setup de desarrollo local, las convenciones de código y el flujo para agregar nuevos módulos.

---

## Requisitos del Entorno

- **Python 3.11+** — para las APIs (FastAPI)
- **Node 18+** — para el frontend (React + Vite)
- **Docker** — para construir imágenes y ejecutar bases de datos
- **Cliente PostgreSQL** (`psql`) — para conectar a las bases de datos y depurar
- **Git** — control de versiones

---

## Estructura del Proyecto (`v3/`)

```
v3/
├── apis/                          ← APIs (FastAPI), una por módulo
│   ├── commercial-api/
│   │   ├── main.py                ← Punto de entrada, rutas FastAPI
│   │   ├── models.py              ← Schemas Pydantic (entrada/salida)
│   │   ├── database.py            ← Pool de conexiones PostgreSQL
│   │   ├── requirements.txt       ← Dependencias Python
│   │   └── Dockerfile             ← Imagen multi-stage (python:3.11-slim)
│   ├── inventory-api/
│   ├── accounting-api/
│   ├── operations-api/
│   └── hr-api/
│
├── databases/                     ← Scripts SQL y Dockerfiles de BD
│   ├── commercial/
│   │   ├── init.sql               ← Esquema, índices, triggers, datos semilla
│   │   ├── entrypoint.sh          ← Entrypoint que delega a postgres oficial
│   │   └── Dockerfile             ← Imagen basada en postgres:15-alpine
│   ├── inventory/
│   ├── accounting/
│   ├── operations/
│   └── hr/
│
├── frontend/                      ← React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx                ← Router principal (react-router-dom)
│   │   ├── main.jsx               ← Punto de entrada React
│   │   ├── components/
│   │   │   ├── Navbar.jsx         ← Barra de navegación con módulos
│   │   │   ├── Dashboard.jsx      ← Pantalla de inicio
│   │   │   ├── modules/           ← Componentes por módulo (1 por cada uno)
│   │   │   │   ├── Commercial.jsx
│   │   │   │   ├── Inventory.jsx
│   │   │   │   ├── Accounting.jsx
│   │   │   │   ├── Operations.jsx
│   │   │   │   └── RRHH.jsx
│   │   │   └── shared/            ← Componentes reutilizables
│   │   │       ├── Button.jsx
│   │   │       ├── Modal.jsx
│   │   │       ├── Table.jsx
│   │   │       └── Notification.jsx
│   │   ├── utils/
│   │   │   ├── api.js             ← Cliente HTTP y funciones por módulo
│   │   │   └── constants.js       ← URLs, colores, etiquetas, estados
│   │   └── index.css              ← Estilos globales + Tailwind
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf                 ← Config de Nginx para servir el build
│   └── Dockerfile                 ← Multi-stage: build con Node, serve con Nginx
│
├── nginx/
│   ├── default.conf               ← Reverse proxy para Docker Compose
│   └── Dockerfile                 ← Imagen nginx con la config incluida
│
├── releases/                      ← Manifiestos Kubernetes (Minikube)
│   ├── base/web.yaml              ← Bundle del frontend
│   ├── commercial/bundle.yaml     ← Bundle Comercial
│   ├── inventory/bundle.yaml
│   ├── accounting/bundle.yaml
│   ├── operations/bundle.yaml
│   └── hr/bundle.yaml
│
├── docs/                          ← Documentación del proyecto
│   ├── DESPLIEGUE.md
│   └── DESARROLLO.md
│
├── docker-compose.yml             ← Orquestación local de 12 servicios
├── load_images.ps1                ← Script para cargar imágenes en Minikube
├── .env.example                   ← Template de variables de entorno
└── .gitignore
```

---

## Setup de Desarrollo Local

### Backend (APIs)

Cada API sigue el mismo patrón de tres archivos principales:

| Archivo | Responsabilidad |
|---------|----------------|
| `main.py` | Punto de entrada FastAPI. Define el `lifespan` (inicializa y cierra el pool de BD), configura CORS, Prometheus, registra los endpoints CRUD y los health checks (`/health/live`, `/health/ready`, `/health/startup`). |
| `models.py` | Schemas Pydantic v2. Define los modelos de entrada (`*Create`, `*Update`), los de salida (`*Response`), enumeraciones de estado y respuestas genéricas (`HealthResponse`, `ErrorResponse`). |
| `database.py` | Pool de conexiones PostgreSQL con `psycopg2`. Usa `ThreadedConnectionPool` con reintentos al iniciar. Expone `get_db_cursor()` como context manager que hace commit/rollback automático. Lee configuración desde variables de entorno mediante `pydantic_settings.BaseSettings`. |

#### Ejecutar una API localmente sin Docker

```bash
cd v3/apis/commercial-api

# Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (apuntar a la BD del docker-compose o una local)
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5431
export POSTGRES_USER=cicor_user
export POSTGRES_PASSWORD=cicor_pass
export POSTGRES_DB=cicor_commercial_db
export LOG_LEVEL=DEBUG

# Iniciar la API
python main.py
# o con uvicorn directamente:
uvicorn main:app --reload --port 8001
```

La API estará disponible en `http://localhost:8001/docs` (Swagger UI).

#### Agregar un nuevo endpoint a una API existente

1. Definí los schemas de entrada/salida en `models.py` (si son nuevos)
2. Agregá la función del endpoint en `main.py` usando los decoradores de FastAPI:
   ```python
   @app.get("/api/commercial/nuevo-endpoint", response_model=MiResponse, tags=["MiTag"])
   def nuevo_endpoint():
       with get_db_cursor() as cursor:
           cursor.execute("SELECT ...")
           rows = cursor.fetchall()
       return [MiResponse(**dict(row)) for row in rows]
   ```
3. El endpoint aparece automáticamente en Swagger UI (`/docs`)

#### Agregar una nueva entidad CRUD (patrón)

El patrón completo para una nueva entidad es:

1. **`models.py`**: Crear `EntityCreate`, `EntityUpdate`, `EntityResponse` (Pydantic)
2. **`main.py`**: Implementar `GET /entity`, `POST /entity`, `PUT /entity/{id}`, `DELETE /entity/{id}`
3. **`init.sql`**: Crear la tabla con `CREATE TABLE`, índices, trigger de `updated_at` y datos semilla

---

### Frontend

#### Instalación y ejecución

```bash
cd v3/frontend
npm install
npm run dev
```

Vite inicia con HMR (Hot Module Replacement) en `http://localhost:5173`. El proxy de Vite redirige las llamadas a `/api/*` hacia `http://localhost` (Nginx en Docker Compose).

#### Estructura de componentes

- **`components/modules/`** — Un componente por cada módulo del ERP. Cada uno implementa una tabla CRUD con su formulario modal. Ejemplo: `Commercial.jsx` maneja la entidad "ventas".
- **`components/shared/`** — Componentes reutilizables sin lógica de negocio:
  - `Button.jsx` — Botón con variantes de color y tamaño
  - `Modal.jsx` — Ventana modal con overlay, título y acciones
  - `Table.jsx` — Tabla genérica con columnas configurables
  - `Notification.jsx` — Toast de notificación (éxito/error)

#### Cliente de API (`src/utils/api.js`)

Define una función genérica `request(url, options)` con manejo de errores y logging. Cada módulo exporta un objeto con sus operaciones CRUD:

```js
// Agregar una nueva llamada a la API
export const nuevoModuloApi = {
  getItems:    ()         => request(`${API_PATHS.nuevo}/items`),
  createItem:  (body)     => request(`${API_PATHS.nuevo}/items`, { method: 'POST', body: JSON.stringify(body) }),
  updateItem:  (id, body) => request(`${API_PATHS.nuevo}/items/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteItem:  (id)       => request(`${API_PATHS.nuevo}/items/${id}`, { method: 'DELETE' }),
  getInfo:     ()         => request(`${API_PATHS.nuevo}/info`),
}
```

#### Constantes (`src/utils/constants.js`)

Centraliza toda la configuración del frontend:

- **`API_BASE_URL`** — se toma de `VITE_API_BASE_URL` (definida en `.env` y como build arg en el Dockerfile)
- **`API_PATHS`** — rutas base de cada módulo (`/api/commercial`, `/api/inventory`, etc.)
- **`MODULE_COLORS`** — color identificador de cada módulo (#10B981, #3B82F6, etc.)
- **`MODULE_LABELS`** — nombres en español: Comercial, Inventario, Contabilidad, Operaciones, Recursos Humanos
- **`STATUS_COLORS`** — clases Tailwind para badges de estado (PENDING = amarillo, CONFIRMED = verde, etc.)

---

### Bases de Datos

Cada módulo tiene su propia base de datos PostgreSQL independiente, con su propio esquema, índices y datos semilla.

#### `init.sql` — Script de inicialización

Define la estructura completa de la base de datos:

1. **Extensiones** — `uuid-ossp`, `pg_stat_statements`
2. **Tablas** — `CREATE TABLE IF NOT EXISTS` con columnas, tipos, constraints `CHECK` y defaults
3. **Índices** — sobre columnas frecuentemente consultadas (status, fechas, nombres)
4. **Triggers** — función `update_updated_at_column()` que actualiza `updated_at` en cada `UPDATE`
5. **Datos semilla** — registros de ejemplo para desarrollo
6. **Comentarios** — `COMMENT ON TABLE/COLUMN` para documentar el esquema

#### Patrón de `entrypoint.sh`

```bash
#!/bin/sh
set -e
exec docker-entrypoint.sh postgres "$@"
```

Delega en el entrypoint oficial de PostgreSQL, que ejecuta automáticamente los scripts en `/docker-entrypoint-initdb.d/`. Como `init.sql` se monta en ese directorio (vía Docker Compose o Dockerfile), se ejecuta al iniciar el contenedor por primera vez.

#### Conectar vía `psql` para depuración

Con Docker Compose corriendo:

```bash
# Conectar a la BD Comercial
psql -h localhost -p 5431 -U cicor_user -d cicor_commercial_db
# contraseña: cicor_pass

# Consultas útiles:
\dt                   # Listar tablas
\d sales              # Describir tabla
SELECT * FROM sales;  # Ver todos los registros
```

---

## Convenciones de Código

### Python (APIs)

- **FastAPI**: Endpoints usan decoradores con `response_model`, `tags`, `summary` y `responses` documentados
- **Pydantic v2**: Schemas con `BaseModel`, `Field()` con validaciones (`gt`, `min_length`), `@computed_field`, `@model_validator`
- **Type hints**: Todas las funciones usan anotaciones de tipo (`def get_sales() -> list[SaleResponse]`)
- **Logging**: JSON estructurado con `python-json-logger`, niveles consistentes (`logger.info`, `logger.warning`, `logger.error`)
- **Salud**: Health checks estandarizados en todas las APIs (`/health/live`, `/health/ready`, `/health/startup`)

### JavaScript/React (Frontend)

- **Componentes**: Functional components con JSX, sin clases
- **Tailwind CSS**: Clases utilitarias directamente en JSX, sin archivos CSS separados por componente
- **Nombres de componentes**: PascalCase para archivos y exports (`Commercial.jsx` → `export default function Commercial`)
- **Nombres de módulos**: El componente de RRHH se llama `RRHH.jsx` por ser la abreviatura en español usada en la UI
- **Ruteo**: `react-router-dom` v6 con `BrowserRouter`, rutas definidas en `App.jsx`

### SQL

- **Snake_case**: Nombres de tablas y columnas en minúsculas con guiones bajos (`product_name`, `total_amount`)
- **CHECK constraints**: Validaciones a nivel de base de datos (`CHECK (quantity > 0)`, `CHECK (status IN (...))`)
- **Triggers**: `BEFORE UPDATE` para actualizar `updated_at` automáticamente
- **Columnas de auditoría**: Todas las tablas incluyen `created_at` y `updated_at`

### Naming general

- **APIs y código**: Todo en inglés (`sales`, `products`, `employees`, `accounting_entries`)
- **Documentación**: En español
- **Frontend (UI)**: Usa abreviaturas en español donde corresponde (`RRHH` para Recursos Humanos, etiquetas como "Comercial", "Inventario")

---

## Construcción de Imágenes Docker

### Dockerfile de APIs (multi-stage)

```dockerfile
# Stage 1: Builder — compila dependencias
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime — solo lo necesario
FROM python:3.11-slim AS runtime
RUN apt-get update && apt-get install -y libpq5 curl
COPY --from=builder /install /usr/local
RUN groupadd --gid 1000 cicor && useradd --uid 1000 --gid cicor cicor
COPY --chown=cicor:cicor . .
USER cicor
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Características:
- **Multi-stage**: separa build (con compilador) de runtime (solo libs)
- **Non-root**: usuario `cicor` con UID 1000
- **Health check listo**: expone `/health/live` para probes de Kubernetes

### Dockerfile del Frontend (multi-stage)

```dockerfile
# Stage 1: Build con Node
FROM node:18-alpine AS builder
ARG VITE_API_BASE_URL=http://localhost
COPY package.json package-lock.json* ./
RUN npm ci --silent
COPY . .
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL npm run build

# Stage 2: Serve con Nginx
FROM nginx:alpine
RUN apk add --no-cache curl
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

El build acepta `VITE_API_BASE_URL` como argumento para configurar a qué URL apuntan las llamadas a la API.

### `load_images.ps1`

Script PowerShell que automatiza la construcción y carga de imágenes en Minikube. Ver la [Guía de Despliegue](DESPLIEGUE.md#3-construir-y-cargar-imágenes) para más detalles.

---

## Adición de un Nuevo Módulo (paso a paso)

Seguí estos 8 pasos para agregar un módulo completo al ERP:

### 1. Crear la API

```
apis/nuevo-modulo-api/
├── main.py             ← Copiar de otro módulo y adaptar
├── models.py           ← Definir schemas de la nueva entidad
├── database.py         ← Copiar tal cual (solo cambia el nombre de BD en defaults)
├── requirements.txt    ← Copiar de otro módulo
└── Dockerfile          ← Copiar tal cual
```

### 2. Crear la base de datos

```
databases/nuevo-modulo/
├── init.sql            ← CREATE TABLE, índices, trigger, seed data
├── entrypoint.sh       ← Copiar tal cual
└── Dockerfile          ← Copiar de otro módulo de BD
```

### 3. Crear el componente del frontend

```
frontend/src/components/modules/NuevoModulo.jsx
```

Seguí el patrón de los existentes: tabla CRUD con Modal para crear/editar y botón de eliminar.

### 4. Agregar la ruta en `App.jsx`

```jsx
import NuevoModulo from './components/modules/NuevoModulo.jsx'

// En <Routes>:
<Route path="/nuevo-modulo" element={<NuevoModulo />} />
```

### 5. Agregar al `docker-compose.yml`

Duplicá el bloque de un módulo existente (API + DB) y ajustá nombres, puertos y variables de entorno. Agregá el volumen y la dependencia en el servicio `nginx`.

### 6. Crear los manifiestos de Kubernetes

```
releases/nuevo-modulo/
└── bundle.yaml    ← Namespace, ConfigMap, Secret, PVC, DB Deployment+Service, API Deployment+Service, Ingress
```

### 7. Agregar ruta en `nginx/default.conf`

```nginx
upstream nuevo_modulo_upstream { server nuevo-modulo-api:8000; }

# En el bloque server:
location /api/nuevo-modulo/ { proxy_pass http://nuevo_modulo_upstream/api/nuevo-modulo/; }
location = /api/nuevo-modulo/docs { proxy_pass http://nuevo_modulo_upstream/docs; }
```

### 8. Actualizar `constants.js`

```js
// En API_PATHS:
nuevoModulo: `${API_BASE_URL}/api/nuevo-modulo`,

// En MODULE_COLORS, MODULE_LABELS y STATUS_COLORS
```

---

## Testing

### Probar APIs con curl

```bash
# Health check
curl http://localhost:8001/health/live

# Info del módulo
curl http://localhost/api/commercial/info | jq

# CRUD completo
curl -X POST http://localhost/api/commercial/sales \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Test","quantity":1,"unit_price":100,"customer_name":"Test"}'

curl http://localhost/api/commercial/sales | jq

curl -X DELETE http://localhost/api/commercial/sales/1
```

### Swagger UI

Cada API expone Swagger UI en su puerto directo y a través de Nginx:

- `http://localhost:8001/docs` → Comercial
- `http://localhost:8002/docs` → Inventario
- `http://localhost:8003/docs` → Contabilidad
- `http://localhost:8004/docs` → Operaciones
- `http://localhost:8005/docs` → RRHH

También disponibles vía Nginx en `http://localhost/api/<modulo>/docs`.

Swagger permite probar todos los endpoints interactivamente: llenar parámetros, ejecutar requests y ver respuestas, sin necesidad de curl ni Postman.
