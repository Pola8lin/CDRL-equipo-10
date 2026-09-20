
-- M03: Roles y mínimo privilegio
-- Los roles de permisos no tienen inicio de sesión.
-- Las credenciales se configurarán fuera de este archivo.

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

-- Permisos sobre el esquema
GRANT USAGE ON SCHEMA public
TO cdrl_reader, cdrl_writer, cdrl_operator;

-- Permisos de lectura
GRANT SELECT ON TABLE telemetry_reading
TO cdrl_reader;

-- Permisos de escritura
GRANT SELECT, INSERT, UPDATE ON TABLE telemetry_reading
TO cdrl_writer;

-- Permisos de secuencia para INSERT
GRANT USAGE, SELECT ON SEQUENCE telemetry_reading_id_seq
TO cdrl_writer;

-- Permisos de migración
GRANT ALL PRIVILEGES ON TABLE telemetry_reading
TO cdrl_migrator;

GRANT ALL PRIVILEGES ON SEQUENCE telemetry_reading_id_seq
TO cdrl_migrator;