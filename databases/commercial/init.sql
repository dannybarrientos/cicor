-- ============================================================
-- CICOR ERP - Módulo Comercial
-- Base de Datos: commercial_db
-- Descripción: Script de inicialización para el módulo de
--              gestión de ventas y relación con inventario
-- ============================================================

-- Extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================
-- TABLA PRINCIPAL: sales
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    id            SERIAL          PRIMARY KEY,
    product_name  VARCHAR(255)    NOT NULL,
    quantity      INT             NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2)   NOT NULL CHECK (unit_price >= 0),
    total_amount  NUMERIC(10,2)   NOT NULL CHECK (total_amount >= 0),
    customer_name VARCHAR(255)    NOT NULL,
    sale_date     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    status        VARCHAR(50)     DEFAULT 'PENDING'
                                  CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'PENDING_INVENTORY')),
    created_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_sales_status       ON sales(status);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date    ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer     ON sales(customer_name);
CREATE INDEX IF NOT EXISTS idx_sales_product      ON sales(product_name);

-- ============================================================
-- FUNCIÓN: auto-update de updated_at
-- ============================================================
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

-- ============================================================
-- DATOS SEMILLA (seed data para desarrollo)
-- ============================================================
INSERT INTO sales (product_name, quantity, unit_price, total_amount, customer_name, status)
VALUES
    ('Laptop Dell XPS 15',     2, 1200.00, 2400.00, 'Empresa ABC S.A.S.',    'CONFIRMED'),
    ('Mouse Logitech MX',      5,   45.00,  225.00, 'Juan Pérez',             'CONFIRMED'),
    ('Monitor LG 27"',         1,  350.00,  350.00, 'Distribuidora Norte',    'PENDING'),
    ('Teclado Mecánico ASUS',  3,   85.00,  255.00, 'Tech Solutions Ltda.',   'PENDING'),
    ('Auriculares Sony WH',    4,  120.00,  480.00, 'María García',           'CANCELLED'),
    ('Silla Ergonómica Herman',1,  750.00,  750.00, 'Oficinas Modernas SAS',  'PENDING_INVENTORY'),
    ('Webcam Logitech C920',   2,   95.00,  190.00, 'Juan Pérez',             'CONFIRMED'),
    ('SSD Samsung 1TB',        6,  110.00,  660.00, 'Empresa ABC S.A.S.',     'CONFIRMED');

-- ============================================================
-- COMENTARIOS DE TABLA
-- ============================================================
COMMENT ON TABLE  sales                IS 'Registro de ventas del módulo Comercial - CICOR ERP';
COMMENT ON COLUMN sales.status         IS 'Estado: PENDING | CONFIRMED | CANCELLED | PENDING_INVENTORY';
COMMENT ON COLUMN sales.total_amount   IS 'Calculado: quantity * unit_price';

-- ============================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ commercial_db inicializada correctamente. Tabla: sales.';
END $$;
