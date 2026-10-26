
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.document_evolution import (
    migrate_to_v2,
    read_telemetry_compatible,
    rollback_to_v1,
)
from src.validator import ALLOWED_UNIT


def load_v1_documents():
    path = ROOT / "fixtures" / "m06-documents-v1.json"
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def test_valid_legacy_document_migrates_to_v2():
    document = load_v1_documents()[0]
    original = document.copy()

    result = migrate_to_v2(document)

    assert result["schema_version"] == 2
    assert result["reading"]["device_id"] == document["device_id"]
    assert result["reading"]["metric"] == "temperature"
    assert document == original
    assert "_description" not in result["reading"]


def test_invalid_temperature_is_rejected():
    document = load_v1_documents()[0].copy()
    document["value"] = 150

    with pytest.raises(ValueError, match="Invalid legacy document"):
        migrate_to_v2(document)


def test_unsupported_schema_version_is_rejected():
    document = load_v1_documents()[0].copy()
    document["schema_version"] = 3

    with pytest.raises(ValueError, match="Unsupported source schema version"):
        migrate_to_v2(document)


def test_missing_required_field_is_rejected():
    document = load_v1_documents()[0].copy()
    del document["device_id"]

    with pytest.raises(ValueError, match="Invalid legacy document"):
        migrate_to_v2(document)


from src.document_evolution import (
    migrate_to_v2,
    read_telemetry_compatible,
    rollback_to_v1,
)


def test_migration_is_idempotent():
    legacy = load_v1_documents()[0]
    first = migrate_to_v2(legacy)
    second = migrate_to_v2(first)

    assert second == first
    assert legacy.get("schema_version", 1) == 1


def test_v1_and_v2_are_read_compatibly():
    legacy = load_v1_documents()[0]
    migrated = migrate_to_v2(legacy)

    assert read_telemetry_compatible(legacy) == migrated["reading"]
    assert read_telemetry_compatible(migrated) == migrated["reading"]


def test_rollback_restores_legacy_structure():
    legacy = load_v1_documents()[0]
    migrated = migrate_to_v2(legacy)
    restored = rollback_to_v1(migrated)

    expected = {
        key: value
        for key, value in legacy.items()
        if key != "_description"
    }
    assert restored == expected
    assert "schema_version" not in restored
    assert "reading" not in restored


def test_rollback_rejects_legacy_document():
    legacy = load_v1_documents()[0]

    with pytest.raises(ValueError, match="Rollback requires a v2 document"):
        rollback_to_v1(legacy)
