# 🗄️ CICOR ERP — Esquemas de Base de Datos

> Cada módulo tiene su propia instancia de PostgreSQL 15 (Alpine) en un pod dedicado dentro de su namespace, con persistencia garantizada por Persistent Volume Claims (PVC).

---

## Índice

- [Visión General](#visión-general)
- [BD: commercial_db](#bd-commercial_db--módulo-comercial)
- [BD: inventory_db](#bd-inventory_db--módulo-inventario)
- [BD: accounting_db](#bd-accounting_db--módulo-contabilidad)
- [BD: operations_db](#bd-operations_db--módulo-operaciones)
- [BD: hr_db](#bd-hr_db--módulo-rrhh)
- [Convenciones y Estándares](#convenciones-y-estándares)
- [Acceso a las Bases de Datos](#acceso-a-las-bases-de-datos)

---

## Visión General

| Módulo       | Base de datos       | Tabla principal       | Host interno (K8s)                                           |
|:-------------|:--------------------|:----------------------|:-------------------------------------------------------------|
| Comercial    | `commercial_db`     | `sales`               | `cicor-commercial-db-svc.cicor-commercial.svc.cluster.local` |
| Inventario   | `inventory_db`      | `products`            | `cicor-inventory-db-svc.cicor-inventory.svc.cluster.local`   |
| Contabilidad | `accounting_db`     | `accounting_entries`  | `cicor-accounting-db-svc.cicor-accounting.svc.cluster.local` | 
| Operaciones  | `operations_db`     | `processes`           | `cicor-operations-db-svc.cicor-operations.svc.cluster.local` |
| RRHH         | `hr_db`             | `employees`           | `cicor-hr-db-svc.cicor-hr.svc.cluster.local`                 | 

---

## BD: `commercial_db` — Módulo Comercial

### Tabla `sales`

Registra todas las ventas generadas por el módulo Comercial.

```sql
CREATE TABLE sales (
    id            SERIAL          PRIMARY KEY,
    product_name  VARCHAR(255)    NOT NULL,
    quantity      INT             NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2)   NOT NULL CHECK (unit_price >= 0),
    total_amount  NUMERIC(10,2)   NOT NULL CHECK (total_amount >= 0),
    customer_name VARCHAR(255)    NOT NULL,
    sale_date     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    status        VARCHAR(50)     DEFAULT 'PENDING'
                                  CHECK (status IN (
                                      'PENDING',
                                      'CONFIRMED',
                                      'CANCELLED',
                                      'PENDING_INVENTORY'
                                  )),
    created_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
```

### Descripción de columnas

| Columna        | Tipo            | Nulo | Descripción                                                                        |
|:---------------|:----------------|:----:|:-----------------------------------------------------------------------------------|
| `id`           | `SERIAL`        | No   | Clave primaria autoincremental                                                     |
| `product_name` | `VARCHAR(255)`  | No   | Nombre del producto vendido                                                        |
| `quantity`     | `INT`           | No   | Cantidad de unidades (must be > 0)                                                 |
| `unit_price`   | `NUMERIC(10,2)` | No   | Precio por unidad                                                                  |
| `total_amount` | `NUMERIC(10,2)` | No   | Total de la venta (`quantity × unit_price`)                                       |
| `customer_name`| `VARCHAR(255)`  | No   | Nombre del cliente                                                                 |
| `sale_date`    | `TIMESTAMP`     | Sí   | Fecha y hora de la venta (default: ahora)                                          |
| `status`       | `VARCHAR(50)`   | Sí   | Estado del pedido (ver enum)                                                       |
| `created_at`   | `TIMESTAMP`     | Sí   | Fecha de creación del registro                                                     |
| `updated_at`   | `TIMESTAMP`     | Sí   | Fecha de última modificación (actualizado por trigger)                             |

### Enum `status`

| Valor                | Descripción                                                       |
|:---------------------|:------------------------------------------------------------------|
| `PENDING`            | Venta creada, pendiente de procesamiento                          |
| `CONFIRMED`          | Inventario confirmó la reserva de stock                           |
| `CANCELLED`          | Venta cancelada                                                   |
| `PENDING_INVENTORY`  | No se pudo reservar stock; venta creada en espera                 |

### Índices

```sql
CREATE INDEX idx_sales_status    ON sales(status);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_sales_customer  ON sales(customer_name);
CREATE INDEX idx_sales_product   ON sales(product_name);
```

### Trigger `updated_at`

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sales_updated_at
    BEFORE UPDATE ON sales
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## BD: `inventory_db` — Módulo Inventario

### Tabla `products`

Catálogo completo de productos con control de stock.

```sql
CREATE TABLE products (
    id             SERIAL          PRIMARY KEY,
    name           VARCHAR(255)    NOT NULL,
    sku            VARCHAR(100)    NOT NULL UNIQUE,
    description    TEXT,
    category       VARCHAR(100),
    stock_quantity INT             DEFAULT 0  CHECK (stock_quantity >= 0),
    reorder_level  INT             DEFAULT 10 CHECK (reorder_level >= 0),
    unit_price     NUMERIC(10,2)   NOT NULL   CHECK (unit_price >= 0),
    created_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
```

### Descripción de columnas

| Columna          | Tipo            | Nulo | Descripción                                                       |
|:-----------------|:----------------|:----:|:------------------------------------------------------------------|
| `id`             | `SERIAL`        | No   | Clave primaria autoincremental                                    |
| `name`           | `VARCHAR(255)`  | No   | Nombre descriptivo del producto                                   |
| `sku`            | `VARCHAR(100)`  | No   | Stock Keeping Unit — identificador único de producto              |
| `description`    | `TEXT`          | Sí   | Descripción detallada                                             |
| `category`       | `VARCHAR(100)`  | Sí   | Categoría del producto (ej: "Electrónica", "Mobiliario")         |
| `stock_quantity` | `INT`           | Sí   | Unidades disponibles en inventario (default: 0)                   |
| `reorder_level`  | `INT`           | Sí   | Nivel mínimo antes de alerta de reorden (default: 10)            |
| `unit_price`     | `NUMERIC(10,2)` | No   | Precio de referencia del producto                                 |
| `created_at`     | `TIMESTAMP`     | Sí   | Fecha de ingreso al catálogo                                      |
| `updated_at`     | `TIMESTAMP`     | Sí   | Última modificación (trigger automático)                          |

### Índices

```sql
CREATE INDEX idx_products_sku      ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_name     ON products(name);
CREATE INDEX idx_products_stock    ON products(stock_quantity);
```

### Lógica del endpoint `/reserve`

El endpoint `POST /api/inventory/reserve` ejecuta la siguiente lógica sobre esta tabla:

```sql
-- Buscar por nombre y reducir stock si hay suficiente
UPDATE products
SET stock_quantity = stock_quantity - :quantity
WHERE name = :product_name
  AND stock_quantity >= :quantity
RETURNING id, stock_quantity AS remaining_stock;

-- Si no retorna filas → success: false
-- Si retorna filas   → success: true
```

---

## BD: `accounting_db` — Módulo Contabilidad

### Tabla `accounting_entries`

Registro de asientos contables con partida doble (débito o crédito, nunca ambos).

```sql
CREATE TABLE accounting_entries (
    id           SERIAL          PRIMARY KEY,
    account_code VARCHAR(50)     NOT NULL,
    account_name VARCHAR(255)    NOT NULL,
    debit        NUMERIC(12,2)   CHECK (debit IS NULL OR debit >= 0),
    credit       NUMERIC(12,2)   CHECK (credit IS NULL OR credit >= 0),
    description  TEXT,
    entry_date   DATE            NOT NULL,
    status       VARCHAR(50)     DEFAULT 'DRAFT'
                                 CHECK (status IN ('DRAFT', 'POSTED', 'REVERSED')),
    created_at   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    -- Constraint de partida doble: XOR entre debit y credit
    CONSTRAINT chk_debit_xor_credit
        CHECK (
            (debit IS NOT NULL OR credit IS NOT NULL)
            AND NOT (debit IS NOT NULL AND credit IS NOT NULL)
        )
);
```

### Descripción de columnas

| Columna        | Tipo            | Nulo | Descripción                                                   |
|:---------------|:----------------|:----:|:--------------------------------------------------------------|
| `id`           | `SERIAL`        | No   | Clave primaria                                                |
| `account_code` | `VARCHAR(50)`   | No   | Código PUC (Plan Único de Cuentas, ej: `1105`, `4135`)       |
| `account_name` | `VARCHAR(255)`  | No   | Nombre de la cuenta contable                                  |
| `debit`        | `NUMERIC(12,2)` | Sí   | Valor al **debe**. Mutuamente exclusivo con `credit`          |
| `credit`       | `NUMERIC(12,2)` | Sí   | Valor al **haber**. Mutuamente exclusivo con `debit`          |
| `description`  | `TEXT`          | Sí   | Descripción o concepto del asiento                            |
| `entry_date`   | `DATE`          | No   | Fecha del asiento (formato `YYYY-MM-DD`)                     |
| `status`       | `VARCHAR(50)`   | Sí   | Estado del asiento contable                                   |
| `created_at`   | `TIMESTAMP`     | Sí   | Fecha de creación                                             |
| `updated_at`   | `TIMESTAMP`     | Sí   | Fecha de última modificación                                  |

### Enum `status`

| Valor      | Descripción                                |
|:-----------|:-------------------------------------------|
| `DRAFT`    | Borrador — no contabilizado aún            |
| `POSTED`   | Contabilizado en el libro mayor            |
| `REVERSED` | Asiento reversado (anulado)                |

### Constraint de partida doble

```
✅ debit=1000,  credit=null   → VÁLIDO  (asiento al debe)
✅ debit=null,  credit=1000   → VÁLIDO  (asiento al haber)
❌ debit=1000,  credit=500    → INVÁLIDO (violación de XOR)
❌ debit=null,  credit=null   → INVÁLIDO (al menos uno requerido)
```

### Índices

```sql
CREATE INDEX idx_entries_account_code ON accounting_entries(account_code);
CREATE INDEX idx_entries_entry_date   ON accounting_entries(entry_date);
CREATE INDEX idx_entries_status       ON accounting_entries(status);
```

---

## BD: `operations_db` — Módulo Operaciones

### Tabla `processes`

Gestión de procesos operacionales con seguimiento de fechas y estados.

```sql
CREATE TABLE processes (
    id                SERIAL          PRIMARY KEY,
    process_name      VARCHAR(255)    NOT NULL,
    description       TEXT,
    owner             VARCHAR(255),
    status            VARCHAR(50)     DEFAULT 'PLANNING'
                                      CHECK (status IN (
                                          'PLANNING',
                                          'IN_PROGRESS',
                                          'COMPLETED',
                                          'ON_HOLD'
                                      )),
    start_date        DATE            NOT NULL,
    expected_end_date DATE,
    actual_end_date   DATE,
    created_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_expected_end_after_start
        CHECK (expected_end_date IS NULL OR expected_end_date >= start_date),

    CONSTRAINT chk_actual_end_after_start
        CHECK (actual_end_date IS NULL OR actual_end_date >= start_date)
);
```

### Descripción de columnas

| Columna               | Tipo          | Nulo | Descripción                                              |
|:----------------------|:--------------|:----:|:---------------------------------------------------------|
| `id`                  | `SERIAL`      | No   | Clave primaria                                           |
| `process_name`        | `VARCHAR(255)`| No   | Nombre del proceso                                       |
| `description`         | `TEXT`        | Sí   | Descripción detallada del proceso                        |
| `owner`               | `VARCHAR(255)`| Sí   | Responsable/dueño del proceso                            |
| `status`              | `VARCHAR(50)` | Sí   | Estado actual (ver enum)                                 |
| `start_date`          | `DATE`        | No   | Fecha de inicio del proceso                              |
| `expected_end_date`   | `DATE`        | Sí   | Fecha estimada de finalización (≥ `start_date`)         |
| `actual_end_date`     | `DATE`        | Sí   | Fecha real de cierre (`null` si aún no finaliza)        |
| `created_at`          | `TIMESTAMP`   | Sí   | Fecha de creación del registro                           |
| `updated_at`          | `TIMESTAMP`   | Sí   | Última modificación                                      |

### Enum `status`

| Valor         | Descripción                             |
|:--------------|:----------------------------------------|
| `PLANNING`    | En planificación, aún no iniciado       |
| `IN_PROGRESS` | En ejecución activa                     |
| `COMPLETED`   | Finalizado con éxito                    |
| `ON_HOLD`     | Pausado temporalmente                   |

### Índices

```sql
CREATE INDEX idx_processes_status       ON processes(status);
CREATE INDEX idx_processes_owner        ON processes(owner);
CREATE INDEX idx_processes_start_date   ON processes(start_date);
```

---

## BD: `hr_db` — Módulo RRHH

### Tabla `employees`

Registro maestro de empleados de la organización.

```sql
CREATE TABLE employees (
    id          SERIAL          PRIMARY KEY,
    full_name   VARCHAR(255)    NOT NULL,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    phone       VARCHAR(20),
    position    VARCHAR(255),
    department  VARCHAR(255),
    hire_date   DATE            NOT NULL,
    salary      NUMERIC(10,2)   CHECK (salary IS NULL OR salary >= 0),
    status      VARCHAR(50)     DEFAULT 'ACTIVE'
                                CHECK (status IN ('ACTIVE', 'INACTIVE', 'ON_LEAVE')),
    created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
```

### Descripción de columnas

| Columna      | Tipo            | Nulo | Descripción                                              |
|:-------------|:----------------|:----:|:---------------------------------------------------------|
| `id`         | `SERIAL`        | No   | Clave primaria                                           |
| `full_name`  | `VARCHAR(255)`  | No   | Nombre completo del empleado                             |
| `email`      | `VARCHAR(255)`  | No   | Correo corporativo (único en la tabla)                   |
| `phone`      | `VARCHAR(20)`   | Sí   | Teléfono de contacto                                     |
| `position`   | `VARCHAR(255)`  | Sí   | Cargo dentro de la organización                          |
| `department` | `VARCHAR(255)`  | Sí   | Área o departamento                                      |
| `hire_date`  | `DATE`          | No   | Fecha de vinculación a la empresa                        |
| `salary`     | `NUMERIC(10,2)` | Sí   | Salario mensual en COP                                   |
| `status`     | `VARCHAR(50)`   | Sí   | Estado laboral del empleado                              |
| `created_at` | `TIMESTAMP`     | Sí   | Fecha de creación del registro                           |
| `updated_at` | `TIMESTAMP`     | Sí   | Última modificación                                      |

### Enum `status`

| Valor      | Descripción                         |
|:-----------|:------------------------------------|
| `ACTIVE`   | Empleado activo y en funciones      |
| `INACTIVE` | Empleado retirado o desvinculado    |
| `ON_LEAVE` | En licencia (maternidad, médica...) |

### Índices

```sql
CREATE INDEX idx_employees_email      ON employees(email);
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_status     ON employees(status);
CREATE INDEX idx_employees_hire_date  ON employees(hire_date);
```

---

## Convenciones y Estándares

### Tipos de datos

| Caso de uso                      | Tipo PostgreSQL    |
|:---------------------------------|:-------------------|
| IDs autoincrementales            | `SERIAL`           |
| Textos cortos (nombres, códigos) | `VARCHAR(n)`       |
| Textos largos (descripciones)    | `TEXT`             |
| Valores monetarios               | `NUMERIC(10,2)`    |
| Valores contables                | `NUMERIC(12,2)`    |
| Fechas                           | `DATE`             |
| Fecha y hora                     | `TIMESTAMP`        |
| Enumerados                       | `VARCHAR(50)` + `CHECK` |

### Columnas de auditoría (todas las tablas)

Todas las tablas incluyen:

```sql
created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Inmutable
updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Actualizado por trigger
```

El trigger de actualización es idéntico en todas las BDs:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Acceso local con port-forward (desarrollo)

```bash
# Levantar todos los port-forwards de BD
./scripts/local-port-forward.sh --db

# Conectar con psql
psql -h localhost -p 5431 -U commercial_user -d commercial_db   # Comercial
psql -h localhost -p 5432 -U inventory_user  -d inventory_db    # Inventario
psql -h localhost -p 5433 -U accounting_user -d accounting_db   # Contabilidad
psql -h localhost -p 5434 -U operations_user -d operations_db   # Operaciones
psql -h localhost -p 5435 -U hr_user         -d hr_db           # RRHH
```


### Credenciales por módulo

> ⚠️ Solo para entorno local. En AWS las credenciales vienen de Secrets Manager.

| Módulo       | Usuario           | Contraseña        | Base de datos    |
|:-------------|:------------------|:------------------|:-----------------|
| Comercial    | `commercial_user` | `commercial_pass` | `commercial_db`  |
| Inventario   | `inventory_user`  | `inventory_pass`  | `inventory_db`   |
| Contabilidad | `accounting_user` | `accounting_pass` | `accounting_db`  |
| Operaciones  | `operations_user` | `operations_pass` | `operations_db`  |
| RRHH         | `hr_user`         | `hr_pass`         | `hr_db`          |
