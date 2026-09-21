
import os
import psycopg


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "cdrl"),
}


USERS = {
    "writer": {
        "user": "cdrl_writer_login",
        "password": os.getenv("CDRL_WRITER_PASSWORD"),
    },
    "reader": {
        "user": "cdrl_reader_login",
        "password": os.getenv("CDRL_READER_PASSWORD"),
    },
    "operator": {
        "user": "cdrl_operator_login",
        "password": os.getenv("CDRL_OPERATOR_PASSWORD"),
    },
}


def run_permission_test(name, config, query, expected):
    try:
        with psycopg.connect(
            **DB_CONFIG,
            user=config["user"],
            password=config["password"],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query)

        result = "PERMITIDO"

    except psycopg.Error:
        result = "DENEGADO"

    status = "OK" if result == expected else "ERROR"

    print(f"{name}: {result} ({status})")


def main():
    print(" VALIDACIÓN DE ACCESOS Y PERMISOS")
    print(" Autor Técnico: Ismael Hernández Jiménez")

    print("\n 1. Pruebas de caso normal")
    run_permission_test(
        "Writer puede insertar",
        USERS["writer"],
        """
        INSERT INTO telemetry_reading
        (device_id, timestamp, metric, value, unit)
        VALUES ('test-writer', NOW(), 'temperature', 20.00, '°C')
        """,
        "PERMITIDO",
    )

    print("\n 2. Dos casos límite")
    run_permission_test(
        "Writer inserta limite superior de temperatura (100.00)",
        USERS["writer"],
        """
        INSERT INTO telemetry_reading
        (device_id, timestamp, metric, value, unit)
        VALUES ('limit-max', NOW(), 'temperature', 100.00, '°C')
        """,
        "PERMITIDO",
    )
    run_permission_test(
        "Writer inserta limite inferior de temperatura (-50.00)",
        USERS["writer"],
        """
        INSERT INTO telemetry_reading
        (device_id, timestamp, metric, value, unit)
        VALUES ('limit-min', NOW(), 'temperature', -50.00, '°C')
        """,
        "PERMITIDO",
    )

    print("\n 3. Pruebas negativas de permisos")
    run_permission_test(
        "Reader no puede insertar",
        USERS["reader"],
        """
        INSERT INTO telemetry_reading
        (device_id, timestamp, metric, value, unit)
        VALUES ('test-reader', NOW(), 'temperature', 20.00, '°C')
        """,
        "DENEGADO",
    )
    run_permission_test(
        "Reader no puede eliminar",
        USERS["reader"],
        """
        DELETE FROM telemetry_reading
        WHERE device_id = 'test-writer'
        """,
        "DENEGADO",
    )
    run_permission_test(
        "Writer no puede eliminar",
        USERS["writer"],
        """
        DELETE FROM telemetry_reading
        WHERE device_id = 'test-writer'
        """,
        "DENEGADO",
    )
    run_permission_test(
        "Operator no puede consultar tabla",
        USERS["operator"],
        """
        SELECT * FROM telemetry_reading
        """,
        "DENEGADO",
    )

    print("\n 4. Fallo declarado")
    run_permission_test(
        "Operator puede ver roles del sistema interno",
        USERS["operator"],
        """
        SELECT rolname FROM pg_roles LIMIT 1
        """,
        "PERMITIDO",
    )

if __name__ == "__main__":
    main()