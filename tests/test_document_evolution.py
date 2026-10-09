
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.document_evolution import migrate_to_v2
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