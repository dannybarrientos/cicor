-- ============================================================
-- CICOR ERP - Módulo Recursos Humanos (RRHH)
-- Base de Datos: hr_db
-- Descripción: Script de inicialización para el módulo de
--              gestión de empleados y nómina
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================
-- TABLA PRINCIPAL: employees
-- ============================================================
CREATE TABLE IF NOT EXISTS employees (
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

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_employees_email      ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_status     ON employees(status);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date  ON employees(hire_date);

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

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS SEMILLA (seed data para desarrollo)
-- ============================================================
INSERT INTO employees (full_name, email, phone, position, department, hire_date, salary, status)
VALUES
    ('Carlos Andrés Rodríguez',   'c.rodriguez@cicor.com',   '+57 311 234 5678', 'Gerente de TI',             'Tecnología',         '2022-03-01',  8500000.00, 'ACTIVE'),
    ('Ana María Martínez',        'a.martinez@cicor.com',    '+57 312 345 6789', 'Desarrolladora Backend',    'Tecnología',         '2022-06-15',  6200000.00, 'ACTIVE'),
    ('Luis Fernando González',    'l.gonzalez@cicor.com',    '+57 313 456 7890', 'Analista de Datos',         'Tecnología',         '2023-01-10',  5800000.00, 'ACTIVE'),
    ('María Camila Torres',       'm.torres@cicor.com',      '+57 314 567 8901', 'Especialista Seguridad',    'Tecnología',         '2023-04-20',  6500000.00, 'ACTIVE'),
    ('Juan Pablo Herrera',        'j.herrera@cicor.com',     '+57 315 678 9012', 'Director Comercial',        'Comercial',          '2021-08-01',  9200000.00, 'ACTIVE'),
    ('Sofía Alejandra Ramírez',   's.ramirez@cicor.com',     '+57 316 789 0123', 'Ejecutiva de Ventas',       'Comercial',          '2022-11-05',  4800000.00, 'ACTIVE'),
    ('Diego Armando Vargas',      'd.vargas@cicor.com',      '+57 317 890 1234', 'Coordinador Inventario',    'Operaciones',        '2022-02-14',  5200000.00, 'ACTIVE'),
    ('Valentina Cruz Ospina',     'v.cruz@cicor.com',        '+57 318 901 2345', 'Contadora Senior',          'Contabilidad',       '2021-05-03',  7100000.00, 'ACTIVE'),
    ('Andrés Felipe Morales',     'a.morales@cicor.com',     '+57 319 012 3456', 'Jefe de RRHH',              'Recursos Humanos',   '2020-09-15',  7800000.00, 'ACTIVE'),
    ('Isabela Jiménez Castro',    'i.jimenez@cicor.com',     '+57 320 123 4567', 'Desarrolladora Frontend',   'Tecnología',         '2023-07-01',  5900000.00, 'ACTIVE'),
    ('Roberto Suárez Peña',       'r.suarez@cicor.com',      '+57 321 234 5678', 'Analista Contable',         'Contabilidad',       '2023-02-20',  4500000.00, 'ON_LEAVE'),
    ('Natalia Gómez Restrepo',    'n.gomez@cicor.com',       '+57 322 345 6789', 'Asistente Administrativa',  'Administración',     '2022-08-08',  3200000.00, 'INACTIVE');

-- ============================================================
-- COMENTARIOS DE TABLA
-- ============================================================
COMMENT ON TABLE  employees             IS 'Registro de empleados del módulo RRHH - CICOR ERP';
COMMENT ON COLUMN employees.status      IS 'Estado: ACTIVE (activo) | INACTIVE (inactivo) | ON_LEAVE (permiso)';
COMMENT ON COLUMN employees.salary      IS 'Salario mensual en COP (pesos colombianos)';
COMMENT ON COLUMN employees.hire_date   IS 'Fecha de vinculación a la empresa';

-- ============================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ hr_db inicializada correctamente. Tabla: employees.';
END $$;
