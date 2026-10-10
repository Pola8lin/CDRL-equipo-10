
from copy import deepcopy

from src.validator import validate_telemetry


CURRENT_SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1


def migrate_to_v2(document):
    """
    Convierte un documento legado de telemetría a la versión 2.

    La versión antigua usa directamente los campos de la lectura.
    La versión nueva agrupa esos campos dentro de "reading".
    No modifica el documento original.
    """
    if not isinstance(document, dict):
        raise ValueError("The document must be a dictionary")

    version = document.get("schema_version", LEGACY_SCHEMA_VERSION)

    if version != LEGACY_SCHEMA_VERSION:
        raise ValueError(f"Unsupported source schema version: {version}")

    # Excluye los metadatos de ejemplo de los fixtures.
    reading = {
        key: deepcopy(value)
        for key, value in document.items()
        if key not in ("_description", "schema_version")
    }

    valid, errors = validate_telemetry(reading)

    if not valid:
        raise ValueError("Invalid legacy document: " + "; ".join(errors))

    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "reading": reading,
    }