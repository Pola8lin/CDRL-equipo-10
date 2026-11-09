import json
import logging

import pytest

from src.audit import AuditLogger


def test_registro_incluye_actor_accion_recurso_y_resultado():
    logger = AuditLogger()
    record = logger.create_audit_record(
        actor="reader",
        action="select",
        resource="public.telemetry_reading",
        result="success",
    )

    assert record["actor"] == "reader"
    assert record["action"] == "SELECT"
    assert record["resource"] == "public.telemetry_reading"
    assert record["result"] == "success"
    assert record["audit_id"]
    assert record["timestamp"]


def test_evento_auditoria_se_emite_como_json(caplog):
    logger = AuditLogger()
    with caplog.at_level(logging.INFO, logger="cdrl.audit"):
        record = logger.log_event(
            actor="writer",
            action="insert",
            resource="public.telemetry_reading",
            result="success",
        )

    emitted = json.loads(caplog.records[-1].message)
    assert emitted == record
    assert {"actor", "action", "resource", "result"} <= emitted.keys()


def test_auditoria_no_incluye_cargas_utiles_ni_secretos(caplog):
    logger = AuditLogger()
    secrets = [
        "synthetic-password-123",
        "synthetic-token-456",
        "postgresql://user:secret@localhost/db",
    ]
    with caplog.at_level(logging.INFO, logger="cdrl.audit"):
        record = logger.log_event(
            actor="test-user",
            action="update",
            resource="public.telemetry_reading",
            result="denied",
        )

    serialized = caplog.records[-1].message
    assert "payload" not in record
    assert all(secret not in serialized for secret in secrets)
    assert record["result"] == "denied"


def test_resultado_invalido_se_rechaza():
    with pytest.raises(ValueError):
        AuditLogger().create_audit_record(
            actor="reader",
            action="select",
            resource="telemetry_reading",
            result="maybe",
        )


def test_run_audited_registra_denegacion_sin_detalles_de_excepcion(caplog):
    class PermissionDenied(Exception):
        sqlstate = "42501"

    def denied_operation():
        raise PermissionDenied("password=do-not-log")

    with caplog.at_level(logging.INFO, logger="cdrl.audit"):
        with pytest.raises(PermissionDenied):
            AuditLogger().run_audited(
                actor="reader",
                action="insert",
                resource="public.telemetry_reading",
                operation=denied_operation,
            )

    event = json.loads(caplog.records[-1].message)
    assert event["result"] == "denied"
    assert event["actor"] == "reader"
    assert "do-not-log" not in caplog.records[-1].message
