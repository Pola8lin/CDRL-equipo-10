
from copy import deepcopy

from src.validator import validate_telemetry


CURRENT_SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1


def _validate_reading(reading, error_prefix="Invalid telemetry document"):
    if not isinstance(reading, dict):
        raise ValueError("The reading must be a dictionary")

    valid, errors = validate_telemetry(reading)
    if not valid:
        raise ValueError(f"{error_prefix}: " + "; ".join(errors))


def read_telemetry_compatible(document):
    """Lee documentos v1 o v2 y devuelve los campos de telemetría."""
    if not isinstance(document, dict):
        raise ValueError("The document must be a dictionary")

    version = document.get("schema_version", LEGACY_SCHEMA_VERSION)

    if version == LEGACY_SCHEMA_VERSION:
        reading = {
            key: deepcopy(value)
            for key, value in document.items()
            if key != "_description"
        }
    elif version == CURRENT_SCHEMA_VERSION:
        reading = deepcopy(document.get("reading"))
    else:
        raise ValueError(f"Unsupported schema version: {version}")

    if version == LEGACY_SCHEMA_VERSION:
        _validate_reading(
            reading,
            error_prefix="Invalid legacy document",
        )
    else:
        _validate_reading(
            reading,
            error_prefix="Invalid v2 document",
        )

    return reading


def migrate_to_v2(document):
    """Migra v1 a v2 y permite repetir la migración de forma idempotente."""
    if not isinstance(document, dict):
        raise ValueError("The document must be a dictionary")

    version = document.get("schema_version", LEGACY_SCHEMA_VERSION)

    if version == CURRENT_SCHEMA_VERSION:
        reading = read_telemetry_compatible(document)
        return {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "reading": reading,
        }

    if version != LEGACY_SCHEMA_VERSION:
        raise ValueError(f"Unsupported source schema version: {version}")

    reading = read_telemetry_compatible(document)
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "reading": reading,
    }


def rollback_to_v1(document):
    """Reconstruye un documento v1 sin modificar el documento v2."""
    if not isinstance(document, dict):
        raise ValueError("The document must be a dictionary")

    if document.get("schema_version") != CURRENT_SCHEMA_VERSION:
        raise ValueError("Rollback requires a v2 document")

    reading = read_telemetry_compatible(document)
    return deepcopy(reading)
