-- M09: endurecimiento idempotente de permisos por operacion.
-- Se conserva la migracion historica M03 y se aplica esta correccion despues.

REVOKE ALL ON TABLE public.telemetry_reading FROM PUBLIC;
REVOKE ALL ON TABLE public.telemetry_summary FROM PUBLIC;

REVOKE ALL ON TABLE public.telemetry_reading
FROM cdrl_reader, cdrl_writer, cdrl_operator;
REVOKE ALL ON TABLE public.telemetry_summary
FROM cdrl_reader, cdrl_writer, cdrl_operator;

-- Reader: lectura solamente.
GRANT USAGE ON SCHEMA public TO cdrl_reader;
GRANT SELECT ON TABLE public.telemetry_reading TO cdrl_reader;

-- Writer: insercion solamente; no puede consultar, modificar ni borrar.
GRANT USAGE ON SCHEMA public TO cdrl_writer;
GRANT INSERT ON TABLE public.telemetry_reading TO cdrl_writer;
GRANT USAGE, SELECT ON SEQUENCE public.telemetry_reading_id_seq TO cdrl_writer;

-- Operator: consulta solamente la vista agregada.
GRANT USAGE ON SCHEMA public TO cdrl_operator;
GRANT SELECT ON TABLE public.telemetry_summary TO cdrl_operator;

-- Migrator conserva la administracion de la tabla y la secuencia.
GRANT USAGE, CREATE ON SCHEMA public TO cdrl_migrator;
GRANT ALL PRIVILEGES ON TABLE public.telemetry_reading TO cdrl_migrator;
GRANT ALL PRIVILEGES ON SEQUENCE public.telemetry_reading_id_seq TO cdrl_migrator;
