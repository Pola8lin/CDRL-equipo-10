import sys
from pathlib import Path

# Permite importar validator.py desde la carpeta src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from validator import (
    validate_telemetry,
    NORMAL_CASE,
    LOWER_BOUNDARY_CASE,
    UPPER_BOUNDARY_CASE,
    DECLARED_FAILURE_CASE,
)


def test_normal_case():
    valid, errors = validate_telemetry(NORMAL_CASE)

    assert valid is True
    assert errors == []


def test_lower_boundary():
    valid, errors = validate_telemetry(LOWER_BOUNDARY_CASE)

    assert valid is True
    assert errors == []


def test_upper_boundary():
    valid, errors = validate_telemetry(UPPER_BOUNDARY_CASE)

    assert valid is True
    assert errors == []


def test_declared_failure():
    valid, errors = validate_telemetry(DECLARED_FAILURE_CASE)

    assert valid is False
    assert errors != []
