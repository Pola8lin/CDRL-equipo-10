import os
import uuid
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

from src.audit import AuditLogger

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "cdrl"),
}

USERS = {
    "writer": {"user": "cdrl_writer_login", "password": os.getenv("CDRL_WRITER_PASSWORD")},
    "reader": {"user": "cdrl_reader_login", "password": os.getenv("CDRL_READER_PASSWORD")},
    "operator": {"user": "cdrl_operator_login", "password": os.getenv("CDRL_OPERATOR_PASSWORD")},
}


def connect_as(role):
    config = USERS[role]
    if not config["password"]:
        pytest.fail(f"Falta la contraseña configurada para el rol {role}")
    return psycopg.connect(**DB_CONFIG, user=config["user"], password=config["password"])


def _execute(conn, query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params)


def assert_permission_denied(role, query, params=None, action="write"):
    """Exige SQLSTATE 42501 y registra el rechazo sin guardar SQL ni parametros."""
    conn = connect_as(role)
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            AuditLogger().run_audited(
                actor=role,
                action=action,
                resource="public.telemetry_reading",
                operation=lambda: _execute(conn, query, params),
            )
    finally:
        conn.rollback()
        conn.close()


def test_writer_can_insert():
    conn = connect_as("writer")
    try:
        AuditLogger().run_audited(
            actor="writer",
            action="insert",
            resource="public.telemetry_reading",
            operation=lambda: _execute(
                conn,
                """
                INSERT INTO public.telemetry_reading
                    (device_id, timestamp, metric, value, unit)
                VALUES (%s, NOW(), 'temperature', 20.00, %s)
                """,
                (f"test-{uuid.uuid4()}", "°C"),
            ),
        )
        conn.rollback()
    finally:
        conn.close()


def test_reader_can_select():
    conn = connect_as("reader")
    try:
        AuditLogger().run_audited(
            actor="reader",
            action="select",
            resource="public.telemetry_reading",
            operation=lambda: _execute(
                conn, "SELECT device_id FROM public.telemetry_reading LIMIT 1"
            ),
        )
    finally:
        conn.close()


def test_reader_cannot_insert():
    assert_permission_denied(
        "reader",
        """
        INSERT INTO public.telemetry_reading
            (device_id, timestamp, metric, value, unit)
        VALUES (%s, NOW(), 'temperature', 20.00, %s)
        """,
        (f"reader-{uuid.uuid4()}", "°C"),
        action="insert",
    )


def test_reader_cannot_delete():
    assert_permission_denied(
        "reader",
        "DELETE FROM public.telemetry_reading WHERE device_id = %s",
        ("synthetic-device",),
        action="delete",
    )


def test_writer_cannot_update():
    assert_permission_denied(
        "writer",
        "UPDATE public.telemetry_reading SET value = 21 WHERE device_id = %s",
        ("synthetic-device",),
        action="update",
    )


def test_writer_cannot_select():
    assert_permission_denied(
        "writer",
        "SELECT device_id FROM public.telemetry_reading LIMIT 1",
        action="select",
    )


def test_writer_cannot_delete():
    assert_permission_denied(
        "writer",
        "DELETE FROM public.telemetry_reading WHERE device_id = %s",
        ("synthetic-device",),
        action="delete",
    )


def test_operator_cannot_read_telemetry_table():
    assert_permission_denied(
        "operator",
        "SELECT * FROM public.telemetry_reading",
        action="select",
    )


def test_operator_can_read_summary_view():
    conn = connect_as("operator")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT metric, total_readings FROM public.telemetry_summary")
            rows = cur.fetchall()
        assert all(metric == "temperature" for metric, _ in rows)
    finally:
        conn.close()
