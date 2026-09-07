import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import insert_telemetry


def make_reading(value):
    return {
        "device_id": f"integration-{uuid4().hex[:8]}",
        "timestamp": "2026-09-06T19:00:00Z",
        "metric": "temperature",
        "value": value,
        "unit": "°C",
    }


def test_insert_normal_case():
    valid, result = insert_telemetry(make_reading(23.50))

    assert valid is True
    assert result[3] == "temperature"
    assert str(result[4]) == "23.50"
    assert result[5] == "°C"


def test_insert_lower_boundary():
    valid, result = insert_telemetry(make_reading(-50.00))

    assert valid is True
    assert str(result[4]) == "-50.00"


def test_insert_upper_boundary():
    valid, result = insert_telemetry(make_reading(100.00))

    assert valid is True
    assert str(result[4]) == "100.00"


def test_declared_failure_is_rejected():
    valid, errors = insert_telemetry(make_reading(150.00))

    assert valid is False
    assert errors != []