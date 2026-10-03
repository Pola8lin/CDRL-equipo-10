import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.document_store import DocumentStore
from src.validator import validate_telemetry


def make_reading(value):
    return {
        "device_id": "sensor-m05-test",
        "timestamp": "2026-10-01T10:30:00Z",
        "metric": "temperature",
        "value": value,
        "unit": "°C",
    }


def make_store():
    store = object.__new__(DocumentStore)
    store.db = MagicMock()
    store.collection_name = "telemetry_events"
    return store


def test_m05_normal_document_is_valid():
    valid, errors = validate_telemetry(make_reading(23.50))

    assert valid is True
    assert errors == []


def test_m05_lower_boundary_is_valid():
    valid, errors = validate_telemetry(make_reading(-50.00))

    assert valid is True
    assert errors == []


def test_m05_upper_boundary_is_valid():
    valid, errors = validate_telemetry(make_reading(100.00))

    assert valid is True
    assert errors == []


def test_m05_declared_failure_is_rejected():
    valid, errors = validate_telemetry(make_reading(150.00))

    assert valid is False
    assert errors != []


def test_m05_create_document():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    result = store.create_document("m05-test-001", make_reading(23.50))

    assert result == "m05-test-001"
    doc_ref.set.assert_called_once_with(make_reading(23.50))


def test_m05_get_existing_document():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    document = MagicMock()
    document.exists = True
    document.to_dict.return_value = make_reading(23.50)
    doc_ref.get.return_value = document

    result = store.get_document("m05-test-001")

    assert result == make_reading(23.50)


def test_m05_get_absent_document():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    document = MagicMock()
    document.exists = False
    doc_ref.get.return_value = document

    result = store.get_document("m05-no-existe")

    assert result is None


def test_m05_update_existing_document():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    result = store.update_document(
        "m05-test-001",
        {"value": 30.00}
    )

    assert result is True
    doc_ref.update.assert_called_once_with({"value": 30.00})


def test_m05_delete_document():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    result = store.delete_document("m05-test-001")

    assert result is True
    doc_ref.delete.assert_called_once()


def test_m05_duplicate_create_is_idempotent_upsert():
    store = make_store()
    doc_ref = store.db.collection.return_value.document.return_value

    first = make_reading(23.50)
    second = make_reading(25.00)

    result1 = store.create_document("m05-duplicate-001", first)
    result2 = store.create_document("m05-duplicate-001", second)

    assert result1 == "m05-duplicate-001"
    assert result2 == "m05-duplicate-001"
    assert doc_ref.set.call_count == 2
    doc_ref.set.assert_any_call(first)
    doc_ref.set.assert_any_call(second)

def test_m05_firestore_index_configuration():
    import json

    index_path = Path(__file__).resolve().parents[1] / "firestore.indexes.json"

    with open(index_path, encoding="utf-8") as file:
        config = json.load(file)

    indexes = config["indexes"]

    assert len(indexes) >= 1

    telemetry_index = next(
        index for index in indexes
        if index["collectionGroup"] == "telemetry_events"
    )

    assert telemetry_index["queryScope"] == "COLLECTION"

    fields = telemetry_index["fields"]

    assert {
        "fieldPath": "device_id",
        "order": "ASCENDING"
    } in fields

    assert {
        "fieldPath": "timestamp",
        "order": "DESCENDING"
    } in fields