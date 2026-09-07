import os
from datetime import datetime
from decimal import Decimal

import psycopg

from src.validator import validate_telemetry


def get_connection():
    """
    Crea una conexión con PostgreSQL usando variables de entorno.
    """
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "cdrl"),
        user=os.getenv("POSTGRES_USER", "cdrl_dev"),
        password=os.getenv("POSTGRES_PASSWORD", "cdrl_dev_only"),
    )


def insert_telemetry(reading):
    """
    Valida e inserta una lectura de telemetría en PostgreSQL.

    Retorna:
        (True, datos_insertados) si la lectura fue válida y se insertó.
        (False, errores) si la lectura no cumple el contrato.
    """

    valid, errors = validate_telemetry(reading)

    if not valid:
        return False, errors

    timestamp = datetime.fromisoformat(
        reading["timestamp"].replace("Z", "+00:00")
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING id, device_id, timestamp, metric, value, unit
                """,
                (
                    reading["device_id"],
                    timestamp,
                    reading["metric"],
                    Decimal(str(reading["value"])),
                    reading["unit"],
                ),
            )

            row = cur.fetchone()

    return True, row