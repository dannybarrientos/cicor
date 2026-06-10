
## Resumen de Módulos y Puertos

| Módulo       | Puerto Interno | Base URL (Ingress)                 | Port-forward       |
|:-------------|:--------------:|:-----------------------------------|:-------------------|
| Comercial    | `8001`         | `http://cicor.local/api/commercial` | `localhost:8001`   |
| Inventario   | `8002`         | `http://cicor.local/api/inventory`  | `localhost:8002`   |
| Contabilidad | `8003`         | `http://cicor.local/api/accounting` | `localhost:8003`   |
| Operaciones  | `8004`         | `http://cicor.local/api/operations` | `localhost:8004`   |
| RRHH         | `8005`         | `http://cicor.local/api/hr`         | `localhost:8005`   |




---

## Health Checks (todos los módulos)

Todos los módulos exponen los mismos tres endpoints de salud en la ruta raíz del pod (sin prefijo `/api/`):

| Endpoint             | Método | Descripción                        | Usado por         |
|:---------------------|:------:|:-----------------------------------|:------------------|
| `/health/startup`    | GET    | Confirma que la app arrancó        | Startup Probe     |
| `/health/ready`      | GET    | Confirma que puede recibir tráfico | Readiness Probe   |
| `/health/live`       | GET    | Confirma que el proceso está vivo  | Liveness Probe    |

**Respuesta exitosa — HTTP 200:**
```json
{
  "status": "ok",
  "service": "commercial-api",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Módulo Comercial 🟢 Verde

**Base URL:** `http://cicor.local/api/commercial`  
**Namespace K8s:** `cicor-commercial`  
**Recurso gestionado:** Ventas (`sales`)

### `GET /api/commercial/info`

Retorna información general del módulo.

```bash
curl http://cicor.local/api/commercial/info
```

**Respuesta 200:**
```json
{
  "module": "commercial",
  "version": "1.0.0",
  "description": "Gestión de ventas",
  "status": "active"
}
```

---

### `GET /api/commercial/sales`

Lista todas las ventas registradas.

```bash
curl http://cicor.local/api/commercial/sales
```

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "product_name": "Laptop",
    "quantity": 5,
    "unit_price": 500.00,
    "total_amount": 2500.00,
    "customer_name": "Acme Corp",
    "sale_date": "2024-01-15T10:30:00Z",
    "status": "CONFIRMED",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### `POST /api/commercial/sales`

Crea una nueva venta. **Dispara automáticamente** `POST /api/inventory/reserve`.

```bash
curl -X POST http://cicor.local/api/commercial/sales \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop Dell XPS",
    "quantity": 2,
    "unit_price": 1200.00,
    "customer_name": "Empresa ABC"
  }'
```

**Body requerido:**

| Campo          | Tipo      | Requerido | Descripción                   |
|:---------------|:----------|:---------:|:------------------------------|
| `product_name` | `string`  | ✅        | Nombre del producto           |
| `quantity`     | `int`     | ✅        | Cantidad (debe ser > 0)       |
| `unit_price`   | `decimal` | ✅        | Precio unitario               |
| `customer_name`| `string`  | ✅        | Nombre del cliente            |

> `total_amount` se calcula automáticamente: `quantity × unit_price`

**Respuesta 200:**
```json
{
  "id": 3,
  "product_name": "Laptop Dell XPS",
  "quantity": 2,
  "unit_price": 1200.00,
  "total_amount": 2400.00,
  "customer_name": "Empresa ABC",
  "sale_date": "2024-01-15T10:30:00Z",
  "status": "CONFIRMED"
}
```

**Lógica de status al crear:**

| Condición de Inventario           | `status` resultante   |
|:----------------------------------|:----------------------|
| `/reserve` responde OK            | `CONFIRMED`           |
| `/reserve` responde error/timeout | `PENDING_INVENTORY`   |

---

### `PUT /api/commercial/sales/{id}`

Actualiza una venta existente.

```bash
curl -X PUT http://cicor.local/api/commercial/sales/3 \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop Dell XPS",
    "quantity": 3,
    "unit_price": 1200.00,
    "customer_name": "Empresa ABC",
    "status": "CONFIRMED"
  }'
```

**Body (todos los campos requeridos en PUT):**

| Campo          | Tipo      | Valores válidos de `status`                          |
|:---------------|:----------|:-----------------------------------------------------|
| `product_name` | `string`  | —                                                    |
| `quantity`     | `int`     | > 0                                                  |
| `unit_price`   | `decimal` | ≥ 0                                                  |
| `customer_name`| `string`  | —                                                    |
| `status`       | `enum`    | `PENDING` \| `CONFIRMED` \| `CANCELLED` \| `PENDING_INVENTORY` |

**Respuesta 200:** objeto `sale` actualizado.

---

### `DELETE /api/commercial/sales/{id}`

Elimina una venta por ID.

```bash
curl -X DELETE http://cicor.local/api/commercial/sales/3
```

**Respuesta 200:**
```json
{ "message": "Venta 3 eliminada correctamente" }
```

---

## Módulo Inventario 🔵 Azul

**Base URL:** `http://cicor.local/api/inventory`  
**Namespace K8s:** `cicor-inventory`  
**Recurso gestionado:** Productos (`products`)

### `GET /api/inventory/info`

```bash
curl http://cicor.local/api/inventory/info
```

---

### `GET /api/inventory/products`

Lista todos los productos del catálogo.

```bash
curl http://cicor.local/api/inventory/products
```

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "name": "Laptop",
    "sku": "LAP-001",
    "description": "High-performance laptop",
    "category": "Electronics",
    "stock_quantity": 15,
    "reorder_level": 10,
    "unit_price": 500.00,
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

---

### `POST /api/inventory/products`

Crea un nuevo producto.

```bash
curl -X POST http://cicor.local/api/inventory/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monitor LG 27\"",
    "sku": "MON-LG-27",
    "description": "Monitor 4K IPS",
    "category": "Monitores",
    "stock_quantity": 30,
    "reorder_level": 5,
    "unit_price": 350.00
  }'
```

**Body requerido:**

| Campo            | Tipo      | Requerido | Notas                    |
|:-----------------|:----------|:---------:|:-------------------------|
| `name`           | `string`  | ✅        |                          |
| `sku`            | `string`  | ✅        | Único en toda la tabla   |
| `description`    | `string`  | ❌        |                          |
| `category`       | `string`  | ❌        |                          |
| `stock_quantity` | `int`     | ❌        | Default: `0`             |
| `reorder_level`  | `int`     | ❌        | Default: `10`            |
| `unit_price`     | `decimal` | ✅        |                          |

---

### `PUT /api/inventory/products/{id}`

```bash
curl -X PUT http://cicor.local/api/inventory/products/1 \
  -H "Content-Type: application/json" \
  -d '{ "name": "Monitor LG 27\" 4K", "sku": "MON-LG-27", "stock_quantity": 25, "reorder_level": 5, "unit_price": 360.00 }'
```

---

### `DELETE /api/inventory/products/{id}`

```bash
curl -X DELETE http://cicor.local/api/inventory/products/1
```

---

### `POST /api/inventory/reserve` ⚡ Endpoint Especial

Endpoint llamado **internamente** por el módulo Comercial al crear una venta. Reduce el stock del producto indicado.

```bash
curl -X POST http://cicor.local/api/inventory/reserve \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop",
    "quantity": 2
  }'
```

**Body:**

| Campo          | Tipo     | Descripción                         |
|:---------------|:---------|:------------------------------------|
| `product_name` | `string` | Nombre del producto a reservar      |
| `quantity`     | `int`    | Cantidad a descontar del stock      |

**Respuesta 200 — Stock suficiente:**
```json
{
  "success": true,
  "remaining_stock": 13,
  "message": "Stock reservado correctamente"
}
```

**Respuesta 200 — Stock insuficiente:**
```json
{
  "success": false,
  "remaining_stock": 0,
  "message": "Stock insuficiente para Laptop"
}
```

---

## Módulo Contabilidad 🔴 Rojo

**Base URL:** `http://cicor.local/api/accounting`  
**Namespace K8s:** `cicor-accounting`  
**Recurso gestionado:** Asientos contables (`accounting_entries`)

### `GET /api/accounting/info`

```bash
curl http://cicor.local/api/accounting/info
```

---

### `GET /api/accounting/entries`

Lista todos los asientos contables.

```bash
curl http://cicor.local/api/accounting/entries
```

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "account_code": "1000",
    "account_name": "Caja General",
    "debit": 1000.00,
    "credit": null,
    "description": "Asiento de apertura",
    "entry_date": "2024-01-15",
    "status": "DRAFT",
    "created_at": "2024-01-15T08:00:00Z"
  }
]
```

---

### `POST /api/accounting/entries`

Crea un nuevo asiento contable. **Regla crítica:** `debit` y `credit` son mutuamente excluyentes — solo puede tener uno de los dos, nunca ambos ni ninguno.

```bash
# Asiento al DEBE (debit)
curl -X POST http://cicor.local/api/accounting/entries \
  -H "Content-Type: application/json" \
  -d '{
    "account_code": "1105",
    "account_name": "Caja General",
    "debit": 500000.00,
    "credit": null,
    "description": "Ingreso por ventas",
    "entry_date": "2024-01-15"
  }'
```

**Body:**

| Campo          | Tipo      | Requerido | Notas                                    |
|:---------------|:----------|:---------:|:-----------------------------------------|
| `account_code` | `string`  | ✅        | Código PUC                               |
| `account_name` | `string`  | ✅        |                                          |
| `debit`        | `decimal` | ⚠️        | Requerido si `credit` es `null`          |
| `credit`       | `decimal` | ⚠️        | Requerido si `debit` es `null`           |
| `description`  | `string`  | ❌        |                                          |
| `entry_date`   | `date`    | ✅        | Formato `YYYY-MM-DD`                     |

**Respuesta 422 — Ambos débito y crédito enviados:**
```json
{ "detail": "Un asiento no puede tener débito y crédito simultáneamente" }
```

---

### `PUT /api/accounting/entries/{id}`

```bash
curl -X PUT http://cicor.local/api/accounting/entries/1 \
  -H "Content-Type: application/json" \
  -d '{ "account_code": "1105", "account_name": "Caja General", "debit": 500000.00, "credit": null, "description": "Actualizado", "entry_date": "2024-01-15", "status": "POSTED" }'
```

**Valores válidos de `status`:** `DRAFT` | `POSTED` | `REVERSED`

---

### `DELETE /api/accounting/entries/{id}`

```bash
curl -X DELETE http://cicor.local/api/accounting/entries/1
```

---

## Módulo Operaciones 🟠 Naranja

**Base URL:** `http://cicor.local/api/operations`  
**Namespace K8s:** `cicor-operations`  
**Recurso gestionado:** Procesos (`processes`)

### `GET /api/operations/info`

```bash
curl http://cicor.local/api/operations/info
```

---

### `GET /api/operations/processes`

```bash
curl http://cicor.local/api/operations/processes
```

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "process_name": "Migración de datos",
    "description": "Migración del sistema legacy a CICOR ERP",
    "owner": "Carlos Rodríguez",
    "status": "IN_PROGRESS",
    "start_date": "2024-01-01",
    "expected_end_date": "2024-03-15",
    "actual_end_date": null,
    "created_at": "2024-01-01T08:00:00Z"
  }
]
```

---

### `POST /api/operations/processes`

```bash
curl -X POST http://cicor.local/api/operations/processes \
  -H "Content-Type: application/json" \
  -d '{
    "process_name": "Auditoría Q1",
    "description": "Revisión de cumplimiento Q1 2024",
    "owner": "Ana Martínez",
    "start_date": "2024-03-01",
    "expected_end_date": "2024-03-31"
  }'
```

**Body:**

| Campo               | Tipo     | Requerido | Notas                                          |
|:--------------------|:---------|:---------:|:-----------------------------------------------|
| `process_name`      | `string` | ✅        |                                                |
| `description`       | `string` | ❌        |                                                |
| `owner`             | `string` | ❌        | Responsable del proceso                        |
| `start_date`        | `date`   | ✅        | Formato `YYYY-MM-DD`                           |
| `expected_end_date` | `date`   | ❌        | Debe ser ≥ `start_date`                        |

---

### `PUT /api/operations/processes/{id}`

```bash
curl -X PUT http://cicor.local/api/operations/processes/1 \
  -H "Content-Type: application/json" \
  -d '{ "process_name": "Auditoría Q1", "description": "Completada", "owner": "Ana Martínez", "start_date": "2024-03-01", "expected_end_date": "2024-03-31", "status": "COMPLETED", "actual_end_date": "2024-03-28" }'
```

**Valores válidos de `status`:** `PLANNING` | `IN_PROGRESS` | `COMPLETED` | `ON_HOLD`

---

### `DELETE /api/operations/processes/{id}`

```bash
curl -X DELETE http://cicor.local/api/operations/processes/1
```

---

## Módulo RRHH 🟣 Púrpura

**Base URL:** `http://cicor.local/api/hr`  
**Namespace K8s:** `cicor-hr`  
**Recurso gestionado:** Empleados (`employees`)

### `GET /api/hr/info`

```bash
curl http://cicor.local/api/hr/info
```

---

### `GET /api/hr/employees`

```bash
curl http://cicor.local/api/hr/employees
```

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "full_name": "Jane Smith",
    "email": "jane@cicor.com",
    "phone": "+57 311 234 5678",
    "position": "Senior Developer",
    "department": "Tecnología",
    "hire_date": "2022-01-15",
    "salary": 6200000.00,
    "status": "ACTIVE",
    "created_at": "2022-01-15T08:00:00Z"
  }
]
```

---

### `POST /api/hr/employees`

```bash
curl -X POST http://cicor.local/api/hr/employees \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "María Torres",
    "email": "m.torres@cicor.com",
    "phone": "+57 314 000 0000",
    "position": "Analista",
    "department": "Contabilidad",
    "hire_date": "2024-02-01",
    "salary": 4500000.00
  }'
```

**Body:**

| Campo        | Tipo      | Requerido | Notas                          |
|:-------------|:----------|:---------:|:-------------------------------|
| `full_name`  | `string`  | ✅        |                                |
| `email`      | `string`  | ✅        | Único en toda la tabla         |
| `phone`      | `string`  | ❌        |                                |
| `position`   | `string`  | ❌        | Cargo del empleado             |
| `department` | `string`  | ❌        |                                |
| `hire_date`  | `date`    | ✅        | Formato `YYYY-MM-DD`           |
| `salary`     | `decimal` | ❌        | Salario mensual (COP)          |

**Respuesta 409 — Email duplicado:**
```json
{ "detail": "Ya existe un empleado con el email m.torres@cicor.com" }
```

---

### `PUT /api/hr/employees/{id}`

```bash
curl -X PUT http://cicor.local/api/hr/employees/1 \
  -H "Content-Type: application/json" \
  -d '{ "full_name": "María Torres", "email": "m.torres@cicor.com", "phone": "+57 314 000 0000", "position": "Analista Senior", "department": "Contabilidad", "hire_date": "2024-02-01", "salary": 5000000.00, "status": "ACTIVE" }'
```

**Valores válidos de `status`:** `ACTIVE` | `INACTIVE` | `ON_LEAVE`

---

### `DELETE /api/hr/employees/{id}`

```bash
curl -X DELETE http://cicor.local/api/hr/employees/1
```

---

## Interacción Especial: Comercial → Inventario

Cuando se crea una venta (`POST /api/commercial/sales`), el módulo Comercial realiza internamente la siguiente llamada al módulo Inventario:

```
POST http://cicor-inventory-api-svc.cicor-inventory.svc.cluster.local/api/inventory/reserve
Body: { "product_name": "<nombre>", "quantity": <cantidad> }
```


## Códigos de Error Estándar

| HTTP | Significado                    | Ejemplo                                      |
|:----:|:-------------------------------|:---------------------------------------------|
| 200  | Éxito                          | Recurso creado/leído/actualizado/eliminado   |
| 400  | Petición inválida              | JSON malformado                              |
| 404  | Recurso no encontrado          | `GET /sales/9999` con ID inexistente         |
| 409  | Conflicto                      | SKU o email duplicado                        |
| 422  | Error de validación            | `quantity: -1`, o debit+credit simultáneos  |
| 500  | Error interno del servidor     | Fallo de conexión a la BD                    |
| 503  | Servicio no disponible         | Pod en estado no-Ready                       |

**Formato de error:**
```json
{
  "detail": "Descripción del error",
  "status_code": 422
}
```

---

## Documentación Interactiva (Swagger)

Cada API FastAPI expone documentación interactiva automáticamente:

| Módulo       | Swagger UI                                    | ReDoc                                         |
|:-------------|:----------------------------------------------|:----------------------------------------------|
| Comercial    | `http://localhost:8001/docs`                  | `http://localhost:8001/redoc`                 |
| Inventario   | `http://localhost:8002/docs`                  | `http://localhost:8002/redoc`                 |
| Contabilidad | `http://localhost:8003/docs`                  | `http://localhost:8003/redoc`                 |
| Operaciones  | `http://localhost:8004/docs`                  | `http://localhost:8004/redoc`                 |
| RRHH         | `http://localhost:8005/docs`                  | `http://localhost:8005/redoc`                 |

> Requiere tener activo el port-forward: `./scripts/local-port-forward.sh`
