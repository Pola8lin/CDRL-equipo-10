
-- M03: Roles y mínimo privilegio

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'cdrl_migrator'
    ) THEN
        CREATE ROLE cdrl_migrator NOLOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'cdrl_writer'
    ) THEN
        CREATE ROLE cdrl_writer NOLOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'cdrl_reader'
    ) THEN
        CREATE ROLE cdrl_reader NOLOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'cdrl_operator'
    ) THEN
        CREATE ROLE cdrl_operator NOLOGIN;
    END IF;
END
$$;

-- Permisos de esquema
GRANT USAGE ON SCHEMA public
TO cdrl_migrator, cdrl_reader, cdrl_writer, cdrl_operator;

-- Reader: solo lectura
GRANT SELECT ON TABLE telemetry_reading
TO cdrl_reader;

-- Writer: lectura e inserción/modificación
GRANT SELECT, INSERT, UPDATE
ON TABLE telemetry_reading
TO cdrl_writer;

GRANT USAGE, SELECT
ON SEQUENCE telemetry_reading_id_seq
TO cdrl_writer;

-- Migrator: control completo sobre la tabla y secuencia
GRANT ALL PRIVILEGES ON TABLE telemetry_reading
TO cdrl_migrator;

GRANT ALL PRIVILEGES ON SEQUENCE telemetry_reading_id_seq
TO cdrl_migrator;

-- Operator: acceso únicamente a un resumen
CREATE OR REPLACE VIEW public.telemetry_summary AS
SELECT
    metric,
    COUNT(*) AS total_readings
FROM public.telemetry_reading
GROUP BY metric;

REVOKE ALL ON TABLE public.telemetry_summary
FROM PUBLIC;

GRANT SELECT ON TABLE public.telemetry_summary
TO cdrl_operator;