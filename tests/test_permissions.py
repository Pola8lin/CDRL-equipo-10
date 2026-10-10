
import os
import uuid
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

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


def connect_as(role):
    config = USERS[role]
    if not config["password"]:
        pytest.fail(f"Falta la contraseña configurada para el rol {role}")

    return psycopg.connect(
        **DB_CONFIG,
        user=config["user"],
        password=config["password"],
    )


def assert_permission_denied(role, query, params=None):
    """Solo acepta una denegación real de privilegios de PostgreSQL."""
    conn = connect_as(role)
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.cursor() as cur:
                cur.execute(query, params)
    finally:
        conn.rollback()
        conn.close()


def test_writer_can_insert():
    device_id = f"test-{uuid.uuid4()}"
    conn = connect_as("writer")
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                VALUES (%s, NOW(), 'temperature', 20.00, %s)
                """,
                (device_id, "°C"),
            )
        # No dejamos datos de prueba persistentes.
        conn.rollback()
    finally:
        conn.close()


def test_reader_can_select():
    with connect_as("reader") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT device_id FROM public.telemetry_reading LIMIT 1"
            )
            cur.fetchall()


def test_reader_cannot_insert():
    assert_permission_denied(
        "reader",
        """
        INSERT INTO public.telemetry_reading
            (device_id, timestamp, metric, value, unit)
        VALUES (%s, NOW(), 'temperature', 20.00, %s)
        """,
        (f"reader-{uuid.uuid4()}", "°C"),
    )


def test_reader_cannot_delete():
    assert_permission_denied(
        "reader",
        "DELETE FROM public.telemetry_reading WHERE device_id = %s",
        ("sensor-001",),
    )


def test_writer_cannot_delete():
    assert_permission_denied(
        "writer",
        "DELETE FROM public.telemetry_reading WHERE device_id = %s",
        ("sensor-001",),
    )


def test_operator_cannot_read_telemetry_table():
    assert_permission_denied(
        "operator",
        "SELECT * FROM public.telemetry_reading",
    )


def test_operator_can_read_summary_view():
    with connect_as("operator") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT metric, total_readings "
                "FROM public.telemetry_summary"
            )
            rows = cur.fetchall()

    assert all(metric == "temperature" for metric, _ in rows)
