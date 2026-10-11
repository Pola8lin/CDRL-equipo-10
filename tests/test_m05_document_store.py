import sys
from pathlib import Path

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
    # levanta la conexion a firestore leyendo el .env
    return DocumentStore()


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
    reading = make_reading(23.50)
    
    # pasa por el validador y se crea
    result = store.create_document("m05-test-001", reading)
    assert result == "m05-test-001"
    
    # checo que si este en la bd
    saved = store.get_document("m05-test-001")
    assert saved == reading


def test_m05_get_existing_document():
    store = make_store()
    reading = make_reading(24.00)
    
    # meto uno de prueba para luego buscarlo
    store.create_document("m05-test-002", reading) 
    
    result = store.get_document("m05-test-002")
    assert result == reading


def test_m05_get_absent_document():
    store = make_store()
    # le paso un id fake a ver si truena o devuelve none
    result = store.get_document("m05-no-existe-nunca")
    assert result is None


def test_m05_update_existing_document():
    store = make_store()
    
    store.create_document("m05-test-003", make_reading(23.50))
    
    # enviamos el documento completo con el nuevo valor para que el validador no se queje
    nuevo_dato = make_reading(30.00)
    result = store.update_document("m05-test-003", nuevo_dato)
    assert result is True
    
    # valido que si se guardo el cambio
    updated = store.get_document("m05-test-003")
    assert updated["value"] == 30.00


def test_m05_delete_document():
    store = make_store()
    store.create_document("m05-test-004", make_reading(20.00))
    
    # lo borro
    result = store.delete_document("m05-test-004")
    assert result is True
    
    # aseguro que ya no traiga nada
    assert store.get_document("m05-test-004") is None


def test_m05_duplicate_create_is_idempotent_upsert():
    store = make_store()
    first = make_reading(23.50)
    second = make_reading(25.00)

    result1 = store.create_document("m05-duplicate-001", first)
    result2 = store.create_document("m05-duplicate-001", second)

    assert result1 == "m05-duplicate-001"
    assert result2 == "m05-duplicate-001"
    
    # si meto el mismo id dos veces se tiene que sobreescribir con el ultimo
    saved = store.get_document("m05-duplicate-001")
    assert saved["value"] == 25.00


def test_m05_firestore_index_configuration():
    import json
    
    # esto lo deje igual, jala el json de indices de erick
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
    assert {"fieldPath": "device_id", "order": "ASCENDING"} in fields
    assert {"fieldPath": "timestamp", "order": "DESCENDING"} in fields