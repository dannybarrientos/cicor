-- ============================================================
-- CICOR ERP - Módulo Operaciones
-- Base de Datos: operations_db
-- Descripción: Script de inicialización para el módulo de
--              gestión de procesos operacionales
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================
-- TABLA PRINCIPAL: processes
-- ============================================================
CREATE TABLE IF NOT EXISTS processes (
    id                SERIAL          PRIMARY KEY,
    process_name      VARCHAR(255)    NOT NULL,
    description       TEXT,
    owner             VARCHAR(255),
    status            VARCHAR(50)     DEFAULT 'PLANNING'
                                      CHECK (status IN ('PLANNING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD')),
    start_date        DATE            NOT NULL,
    expected_end_date DATE,
    actual_end_date   DATE,
    created_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    -- Validación: si hay fecha real de fin, debe ser >= fecha inicio
    CONSTRAINT chk_actual_end_after_start
        CHECK (actual_end_date IS NULL OR actual_end_date >= start_date),
    -- Validación: si hay fecha esperada, debe ser >= fecha inicio
    CONSTRAINT chk_expected_end_after_start
        CHECK (expected_end_date IS NULL OR expected_end_date >= start_date)
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_processes_status           ON processes(status);
CREATE INDEX IF NOT EXISTS idx_processes_owner            ON processes(owner);
CREATE INDEX IF NOT EXISTS idx_processes_start_date       ON processes(start_date);
CREATE INDEX IF NOT EXISTS idx_processes_expected_end     ON processes(expected_end_date);

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

CREATE TRIGGER trg_processes_updated_at
    BEFORE UPDATE ON processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS SEMILLA (seed data para desarrollo)
-- ============================================================
INSERT INTO processes (process_name, description, owner, status, start_date, expected_end_date, actual_end_date)
VALUES
    ('Implementación ERP Módulo Comercial',
     'Despliegue y configuración del módulo comercial en producción',
     'Carlos Rodríguez', 'COMPLETED',
     '2024-01-05', '2024-01-31', '2024-01-28'),

    ('Migración Base de Datos Legacy',
     'Migración de datos del sistema anterior a CICOR ERP',
     'Ana Martínez', 'IN_PROGRESS',
     '2024-02-01', '2024-02-28', NULL),

    ('Capacitación Equipo Ventas',
     'Capacitación en uso del módulo comercial e inventario',
     'Luis González', 'PLANNING',
     '2024-03-01', '2024-03-15', NULL),

    ('Auditoría de Seguridad Infraestructura',
     'Revisión de políticas RBAC, NetworkPolicies y secretos',
     'María Torres', 'IN_PROGRESS',
     '2024-02-10', '2024-02-25', NULL),

    ('Optimización Queries PostgreSQL',
     'Revisión y optimización de índices y consultas lentas',
     'Carlos Rodríguez', 'ON_HOLD',
     '2024-02-15', '2024-03-15', NULL),

    ('Integración API Inventario-Comercial',
     'Implementar y validar endpoint /reserve entre módulos',
     'Ana Martínez', 'COMPLETED',
     '2024-01-10', '2024-01-20', '2024-01-18'),

    ('Configuración Prometheus + Grafana',
     'Despliegue y configuración de dashboards de monitoreo',
     'Luis González', 'COMPLETED',
     '2024-01-15', '2024-01-25', '2024-01-24');

-- ============================================================
-- COMENTARIOS DE TABLA
-- ============================================================
COMMENT ON TABLE  processes                    IS 'Procesos operacionales del módulo Operaciones - CICOR ERP';
COMMENT ON COLUMN processes.status             IS 'Estado: PLANNING | IN_PROGRESS | COMPLETED | ON_HOLD';
COMMENT ON COLUMN processes.actual_end_date    IS 'Fecha real de finalización. NULL si no ha concluido';
COMMENT ON COLUMN processes.expected_end_date  IS 'Fecha estimada de finalización del proceso';

-- ============================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ operations_db inicializada correctamente. Tabla: processes.';
END $$;
