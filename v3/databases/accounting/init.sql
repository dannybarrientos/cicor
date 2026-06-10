-- ============================================================
-- CICOR ERP - Módulo Contabilidad
-- Base de Datos: accounting_db
-- Descripción: Script de inicialización para el módulo de
--              registro de asientos contables
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================
-- TABLA PRINCIPAL: accounting_entries
-- ============================================================
CREATE TABLE IF NOT EXISTS accounting_entries (
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
    -- Restricción: debe tener débito O crédito, nunca ambos ni ninguno
    CONSTRAINT chk_debit_or_credit
        CHECK (
            (debit IS NOT NULL OR credit IS NOT NULL)
            AND NOT (debit IS NOT NULL AND credit IS NOT NULL)
        )
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_entries_account_code ON accounting_entries(account_code);
CREATE INDEX IF NOT EXISTS idx_entries_entry_date   ON accounting_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_entries_status       ON accounting_entries(status);

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

CREATE TRIGGER trg_entries_updated_at
    BEFORE UPDATE ON accounting_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS SEMILLA (seed data para desarrollo)
-- ============================================================
INSERT INTO accounting_entries (account_code, account_name, debit, credit, description, entry_date, status)
VALUES
    -- Apertura de caja
    ('1105', 'Caja General',            5000000.00, NULL,        'Apertura de caja periodo enero',           '2024-01-01', 'POSTED'),
    ('3115', 'Capital Social',          NULL,        5000000.00,  'Apertura de caja periodo enero',           '2024-01-01', 'POSTED'),
    -- Venta de mercancía
    ('1305', 'Clientes Nacionales',     2400000.00, NULL,        'Venta laptops a Empresa ABC - Fact 001',   '2024-01-15', 'POSTED'),
    ('4135', 'Comercio al por Mayor',   NULL,        2400000.00,  'Venta laptops a Empresa ABC - Fact 001',  '2024-01-15', 'POSTED'),
    -- Costo de ventas
    ('6135', 'Costo de Ventas Mercancía', 1800000.00, NULL,      'Costo mercancía vendida Fact 001',         '2024-01-15', 'POSTED'),
    ('1435', 'Mercancías en Existencia', NULL,       1800000.00,  'Salida inventario Fact 001',               '2024-01-15', 'POSTED'),
    -- Gasto arriendo oficina (borrador)
    ('5120', 'Arrendamientos',          1200000.00, NULL,        'Arriendo oficina sede principal enero',    '2024-01-31', 'DRAFT'),
    ('2205', 'Proveedores Nacionales',  NULL,        1200000.00,  'Arriendo oficina sede principal enero',   '2024-01-31', 'DRAFT'),
    -- Asiento reversado
    ('1105', 'Caja General',            500000.00,  NULL,        'Asiento de prueba - REVERSADO',            '2024-01-20', 'REVERSED');

-- ============================================================
-- COMENTARIOS DE TABLA
-- ============================================================
COMMENT ON TABLE  accounting_entries            IS 'Asientos contables del módulo Contabilidad - CICOR ERP';
COMMENT ON COLUMN accounting_entries.debit      IS 'Valor al debe. Mutuamente exclusivo con credit';
COMMENT ON COLUMN accounting_entries.credit     IS 'Valor al haber. Mutuamente exclusivo con debit';
COMMENT ON COLUMN accounting_entries.status     IS 'Estado: DRAFT (borrador) | POSTED (contabilizado) | REVERSED (reversado)';
COMMENT ON COLUMN accounting_entries.account_code IS 'Código PUC (Plan Único de Cuentas)';

-- ============================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ accounting_db inicializada correctamente. Tabla: accounting_entries.';
END $$;
