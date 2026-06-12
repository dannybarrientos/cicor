-- ============================================================
-- CICOR ERP - Módulo Inventario
-- Base de Datos: inventory_db
-- Descripción: Script de inicialización para el módulo de
--              gestión de productos y control de stock
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================
-- TABLA PRINCIPAL: products
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id             SERIAL          PRIMARY KEY,
    name           VARCHAR(255)    NOT NULL,
    sku            VARCHAR(100)    NOT NULL UNIQUE,
    description    TEXT,
    category       VARCHAR(100),
    stock_quantity INT             DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_level  INT             DEFAULT 10 CHECK (reorder_level >= 0),
    unit_price     NUMERIC(10,2)   NOT NULL CHECK (unit_price >= 0),
    created_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_products_sku      ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_name     ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_stock    ON products(stock_quantity);

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

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS SEMILLA (seed data para desarrollo)
-- ============================================================
INSERT INTO products (name, sku, description, category, stock_quantity, reorder_level, unit_price)
VALUES
    ('Laptop Dell XPS 15',      'LAPTOP-DELL-XPS15', 'Laptop profesional Intel i7 32GB RAM',       'Computadores',    50, 10, 1200.00),
    ('Mouse Logitech MX Master','MOUSE-LOGI-MX',     'Mouse inalámbrico ergonómico avanzado',       'Periféricos',    200,  20,   45.00),
    ('Monitor LG 27" 4K',       'MONITOR-LG-27-4K',  'Monitor UltraFine 4K IPS 27 pulgadas',       'Monitores',       30,   5,  350.00),
    ('Teclado Mecánico ASUS',   'TECLADO-ASUS-MECA', 'Teclado mecánico switches Cherry MX Brown',  'Periféricos',    150,  15,   85.00),
    ('Auriculares Sony WH-1000','AUDIO-SONY-WH1000', 'Auriculares noise-cancelling premium',        'Audio',           80,  10,  120.00),
    ('Silla Ergonómica Herman', 'SILLA-HERMAN-ERG',  'Silla ergonómica oficina Herman Miller',      'Mobiliario',      15,   3,  750.00),
    ('Webcam Logitech C920',    'CAM-LOGI-C920',     'Cámara web Full HD 1080p con micrófono',     'Periféricos',    100,  20,   95.00),
    ('SSD Samsung 870 EVO 1TB', 'SSD-SAM-870-1TB',  'Disco sólido SATA 1TB lectura 560MB/s',      'Almacenamiento',  75,  10,  110.00),
    ('Hub USB-C 7 en 1',        'HUB-USB-C-7IN1',   'Hub multipuerto USB-C con HDMI y USB 3.0',   'Accesorios',     120,  25,   55.00),
    ('Impresora HP LaserJet',   'IMP-HP-LASER-M',   'Impresora láser monocromática 40 ppm',       'Impresión',       20,   5,  280.00);

-- ============================================================
-- COMENTARIOS DE TABLA
-- ============================================================
COMMENT ON TABLE  products               IS 'Catálogo de productos del módulo Inventario - CICOR ERP';
COMMENT ON COLUMN products.sku           IS 'Stock Keeping Unit - identificador único de producto';
COMMENT ON COLUMN products.reorder_level IS 'Nivel mínimo de stock antes de generar alerta de reorden';

-- ============================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ inventory_db inicializada correctamente. Tabla: products.';
END $$;
